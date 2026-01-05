from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Card

export_bp = Blueprint("export", __name__)


@export_bp.route("/export")
@login_required
def export_data():
    cards = (
        Card.query.filter_by(team_id=current_user.team_id, archived=False)
        .order_by(Card.created_at.desc())
        .all()
    )
    return render_template("export.html", cards=cards)


@export_bp.route("/api/export/json")
@login_required
def export_json():
    cards = Card.query.filter_by(team_id=current_user.team_id).all()
    data = []
    for card in cards:
        data.append(
            {
                "id": card.id,
                "title": card.title,
                "description": card.description,
                "status": card.status,
                "creator": card.creator.username,
                "created_at": card.created_at.isoformat(),
                "updated_at": card.updated_at.isoformat(),
            }
        )
    return jsonify(data)
