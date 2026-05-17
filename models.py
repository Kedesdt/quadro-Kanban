from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship("Team", foreign_keys=[team_id], back_populates="members")
    created_cards = db.relationship(
        "Card", foreign_keys="Card.creator_id", back_populates="creator", lazy=True
    )
    assigned_cards = db.relationship(
        "Card",
        foreign_keys="Card.assigned_to_id",
        back_populates="assigned_to",
        lazy=True,
    )


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("User", foreign_keys=[admin_id])
    members = db.relationship(
        "User", foreign_keys="User.team_id", back_populates="team"
    )
    cards = db.relationship("Card", back_populates="team", lazy=True)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="todo")  # todo, doing, done
    position = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7), default="#667eea")  # Cor em hexadecimal
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = db.Column(db.DateTime, nullable=True)
    archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("card.id"), nullable=True)

    creator = db.relationship(
        "User", foreign_keys=[creator_id], back_populates="created_cards"
    )
    assigned_to = db.relationship(
        "User", foreign_keys=[assigned_to_id], back_populates="assigned_cards"
    )
    team = db.relationship("Team", back_populates="cards")
    history = db.relationship(
        "CardHistory", back_populates="card", cascade="all, delete-orphan", lazy=True
    )
    # Relação pai/filhos para subcards
    parent = db.relationship('Card', remote_side=[id], backref=db.backref('children', lazy=True))

    def completion_percentage(self):
        """Calcula a porcentagem de conclusão pelos subitens (children).
        Se não tiver subitens, retorna 100 se o próprio card estiver em 'done', senão 0.
        """
        total = len(self.children)
        if total == 0:
            return 100 if self.status == 'done' else 0
        done = sum(1 for c in self.children if c.status == 'done')
        return int((done / total) * 100)

    def propagate_status_to_parent(self, user_id=None):
        """Propaga o status do card para seus pais recursivamente.

        Regras:
        - Se qualquer filho estiver em 'doing' -> pai = 'doing'
        - Se todos os filhos estiverem em 'done' (e houver filhos) -> pai = 'done'
        - Caso contrário -> pai = 'todo'

        O método cria entradas de histórico (`CardHistory`) quando um pai muda de status.
        """
        parent = self.parent
        # Use provided user_id for history if given, else try to fall back to creator
        uid = user_id or getattr(self, 'creator_id', None)

        while parent:
            children_statuses = [c.status for c in parent.children]
            statuses = set(children_statuses)

            # Regras desejadas:
            # - Se qualquer filho estiver em 'doing' -> pai = 'doing'
            # - Se todos os filhos estiverem em 'done' -> pai = 'done'
            # - Se todos os filhos estiverem em 'todo' -> pai = 'todo'
            # - Caso misto (ex: some 'todo' e some 'done', sem 'doing') -> pai = 'doing'
            if 'doing' in statuses:
                new_status = 'doing'
            elif statuses == {'done'}:
                new_status = 'done'
            elif statuses == {'todo'}:
                new_status = 'todo'
            else:
                new_status = 'doing'

            if parent.status != new_status:
                old_status = parent.status
                parent.status = new_status
                if new_status == 'done':
                    parent.completed_at = datetime.utcnow()
                else:
                    parent.completed_at = None

                # registrar histórico se a classe CardHistory estiver disponível
                try:
                    history = CardHistory(
                        card_id=parent.id,
                        action='moved',
                        old_status=old_status,
                        new_status=new_status,
                        user_id=uid or parent.creator_id,
                        details=f'Auto-propagado a partir do subitem {self.id}',
                    )
                    db.session.add(history)
                except Exception:
                    # Se CardHistory não existir ainda ou erro, ignore histórico
                    pass

                db.session.commit()
                # continuar subindo na hierarquia
                parent = parent.parent
            else:
                # sem mudança — não precisa subir mais
                break

    def get_time_in_status(self):
        """Calcula tempo no status atual"""
        if self.completed_at and self.status == "done":
            return (
                self.completed_at - self.created_at
            ).total_seconds() / 3600  # em horas
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600


class CardHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("card.id"), nullable=False)
    action = db.Column(
        db.String(50), nullable=False
    )  # created, moved, assigned, completed, archived
    old_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)

    card = db.relationship("Card", back_populates="history")
    user = db.relationship("User")


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship(
        "User", backref=db.backref("reset_tokens", cascade="all, delete-orphan")
    )

    @staticmethod
    def create_token(user, hours=24):
        """Cria um token de reset para o usuário com validade em horas"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=hours)

        reset_token = PasswordResetToken(
            user_id=user.id, token=token, expires_at=expires_at
        )

        db.session.add(reset_token)
        db.session.commit()

        return token

    @staticmethod
    def verify_token(token):
        """Verifica se o token é válido e retorna o usuário"""
        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return None

        if reset_token.used:
            return None

        if datetime.utcnow() > reset_token.expires_at:
            return None

        return reset_token.user

    def mark_as_used(self):
        """Marca o token como usado"""
        self.used = True
        db.session.commit()
