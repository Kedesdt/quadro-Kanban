from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Card, CardHistory
from datetime import datetime

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/cards", methods=["POST"])
@login_required
def create_card():
    """Criar novo card"""
    if not current_user.team_id:
        return jsonify({"success": False, "error": "Usuário não está em equipe"}), 403

    data = request.get_json()

    new_card = Card(
        title=data.get("title", ""),
        description=data.get("description", ""),
        status=data.get("status", "todo"),
        position=data.get("position", 0),
        color=data.get("color", "#667eea"),
        creator_id=current_user.id,
        team_id=current_user.team_id,
    )

    # Parent (subcard) opcional
    parent_id = data.get('parent_id')
    if parent_id:
        parent = Card.query.get(parent_id)
        if not parent or parent.team_id != current_user.team_id:
            return jsonify({"success": False, "error": "Parent inválido"}), 400
        new_card.parent_id = parent_id

    db.session.add(new_card)
    db.session.commit()

    # Registrar no histórico
    history = CardHistory(
        card_id=new_card.id,
        action="created",
        new_status="todo",
        user_id=current_user.id,
        details=f"Card criado por {current_user.username}",
    )
    db.session.add(history)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "card": {
                "id": new_card.id,
                "title": new_card.title,
                "description": new_card.description,
                "status": new_card.status,
                "position": new_card.position,
                "color": new_card.color,
                "creator": current_user.username,
                "created_at": new_card.created_at.isoformat(),
            },
        }
    )


@api_bp.route("/cards/<int:card_id>", methods=["PUT"])
@login_required
def update_card(card_id):
    """Atualizar card existente"""
    print(f"📝 PUT /api/cards/{card_id} - User: {current_user.username}")

    if not current_user.team_id:
        print(f"❌ Usuário {current_user.username} não tem team_id")
        return jsonify({"success": False, "error": "Usuário não está em equipe"}), 403

    card = Card.query.get(card_id)

    if not card:
        print(f"❌ Card {card_id} não encontrado")
        return jsonify({"success": False, "error": "Card não encontrado"}), 404

    if card.team_id != current_user.team_id:
        print(
            f"❌ Sem permissão: card.team_id={card.team_id}, user.team_id={current_user.team_id}"
        )
        return jsonify({"success": False, "error": "Sem permissão"}), 403

    data = request.get_json()
    print(f"📦 Dados recebidos: {data}")

    old_status = card.status
    old_assigned = card.assigned_to_id

    if "title" in data:
        card.title = data["title"]
    if "description" in data:
        card.description = data["description"]
    if "status" in data:
        card.status = data["status"]

        # Se moveu o card, atribuir ao usuário atual
        if old_status != data["status"]:
            card.assigned_to_id = current_user.id

            # Se moveu para "done", registrar data de conclusão
            if data["status"] == "done" and old_status != "done":
                card.completed_at = datetime.utcnow()

            # Registrar movimento no histórico
            history = CardHistory(
                card_id=card.id,
                action="moved",
                old_status=old_status,
                new_status=data["status"],
                user_id=current_user.id,
                details=f'{current_user.username} moveu de {old_status} para {data["status"]}',
            )
            db.session.add(history)

            # Se foi atribuído, registrar no histórico
            if old_assigned != current_user.id:
                assign_history = CardHistory(
                    card_id=card.id,
                    action="assigned",
                    user_id=current_user.id,
                    details=f"Card atribuído a {current_user.username}",
                )
                db.session.add(assign_history)

    if "position" in data:
        card.position = data["position"]

    card.updated_at = datetime.utcnow()
    db.session.commit()

    print(f"✅ Card {card_id} atualizado: {old_status} -> {card.status}")

    # Propagar mudança de status para pais (se houver)
    try:
        card.propagate_status_to_parent(user_id=current_user.id)
    except Exception as e:
        print(f"⚠️ Erro ao propagar status para pais: {e}")

    return jsonify(
        {
            "success": True,
            "card": {
                "id": card.id,
                "title": card.title,
                "description": card.description,
                "status": card.status,
                "position": card.position,
                "color": card.color,
                "assigned_to": card.assigned_to.username if card.assigned_to else None,
            },
        }
    )


@api_bp.route("/cards/<int:card_id>", methods=["DELETE"])
@login_required
def delete_card(card_id):
    """Deletar card"""
    if not current_user.team_id:
        return jsonify({"success": False, "error": "Usuário não está em equipe"}), 403

    card = Card.query.get(card_id)

    if not card:
        return jsonify({"success": False, "error": "Card não encontrado"}), 404

    if card.team_id != current_user.team_id:
        return jsonify({"success": False, "error": "Sem permissão"}), 403

    # Deletar permanentemente (histórico será deletado em cascata)
    db.session.delete(card)
    db.session.commit()

    return jsonify({"success": True, "message": "Card deletado com sucesso"})
