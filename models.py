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
