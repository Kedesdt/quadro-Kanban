from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Card
from datetime import datetime, timedelta

kanban_bp = Blueprint("kanban", __name__)


def archive_old_completed_cards():
    """Arquiva cards que estão há mais de 2 dias na coluna 'done'"""
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    old_cards = Card.query.filter(
        Card.status == "done",
        Card.completed_at.isnot(None),
        Card.completed_at <= two_days_ago,
        Card.archived == False,
    ).all()

    for card in old_cards:
        card.archived = True
        card.archived_at = datetime.utcnow()

        # Registrar no histórico
        from models import CardHistory

        history = CardHistory(
            card_id=card.id,
            action="archived",
            old_status="done",
            new_status="archived",
            user_id=card.creator_id,
            details="Card arquivado automaticamente após 2 dias concluído",
        )
        db.session.add(history)

    if old_cards:
        db.session.commit()

    return len(old_cards)


@kanban_bp.route("/kanban")
@login_required
def kanban():
    if not current_user.team_id:
        flash("Você não está em nenhuma equipe", "error")
        return redirect(url_for("auth.logout"))

    # Arquivar cards antigos
    archive_old_completed_cards()

    # Buscar apenas cards não arquivados
    cards = (
        Card.query.filter_by(team_id=current_user.team_id, archived=False)
        .order_by(Card.position)
        .all()
    )

    team_members = User.query.filter_by(team_id=current_user.team_id).all()

    # Cores disponíveis para os cards
    card_colors = [
        "#667eea",
        "#764ba2",
        "#f093fb",
        "#4facfe",
        "#43e97b",
        "#fa709a",
        "#fee140",
        "#30cfd0",
        "#a8edea",
        "#ff9a9e",
        "#fbc2eb",
        "#a1c4fd",
    ]

    return render_template(
        "kanban.html", cards=cards, team_members=team_members, card_colors=card_colors
    )


@kanban_bp.route("/kanban/fullscreen")
@login_required
def kanban_fullscreen():
    """Visualização em tela cheia do quadro Kanban sem botões de criação"""
    if not current_user.team_id:
        flash("Você não está em nenhuma equipe", "error")
        return redirect(url_for("auth.logout"))

    # Arquivar cards antigos
    archive_old_completed_cards()

    # Buscar apenas cards não arquivados
    cards = (
        Card.query.filter_by(team_id=current_user.team_id, archived=False)
        .order_by(Card.position)
        .all()
    )

    team_members = User.query.filter_by(team_id=current_user.team_id).all()

    return render_template(
        "kanban_fullscreen.html", cards=cards, team_members=team_members
    )
