from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Card

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
@login_required
def history():
    """Página de histórico com cards arquivados e relatórios"""
    archived_cards = (
        Card.query.filter_by(team_id=current_user.team_id, archived=True)
        .order_by(Card.archived_at.desc())
        .all()
    )

    # Estatísticas
    total_archived = len(archived_cards)

    # Calcular tempo médio de conclusão
    completed_times = []
    for card in archived_cards:
        if card.completed_at and card.created_at:
            time_diff = (
                card.completed_at - card.created_at
            ).total_seconds() / 3600  # horas
            completed_times.append(time_diff)

    avg_completion_time = (
        sum(completed_times) / len(completed_times) if completed_times else 0
    )

    return render_template(
        "history.html",
        archived_cards=archived_cards,
        total_archived=total_archived,
        avg_completion_time=avg_completion_time,
    )
