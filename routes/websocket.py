from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from models import db, Card, CardHistory
from datetime import datetime


def register_websocket_events(socketio):
    """Registra todos os eventos WebSocket"""

    @socketio.on("connect")
    def handle_connect():
        if current_user.is_authenticated:
            join_room(f"team_{current_user.team_id}")
            emit(
                "user_connected",
                {"username": current_user.username},
                room=f"team_{current_user.team_id}",
            )

    @socketio.on("disconnect")
    def handle_disconnect():
        if current_user.is_authenticated:
            leave_room(f"team_{current_user.team_id}")

    @socketio.on("create_card")
    def handle_create_card(data):
        if not current_user.is_authenticated:
            return

        new_card = Card(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            position=data.get("position", 0),
            color=data.get("color", "#667eea"),
            creator_id=current_user.id,
            team_id=current_user.team_id,
        )

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

        emit(
            "card_created",
            {
                "id": new_card.id,
                "title": new_card.title,
                "description": new_card.description,
                "status": new_card.status,
                "position": new_card.position,
                "color": new_card.color,
                "creator": current_user.username,
                "assigned_to": None,
                "created_at": new_card.created_at.isoformat(),
            },
            room=f"team_{current_user.team_id}",
        )

    @socketio.on("update_card")
    def handle_update_card(data):
        if not current_user.is_authenticated:
            return

        card = Card.query.get(data["id"])

        if card and card.team_id == current_user.team_id:
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

            emit(
                "card_updated",
                {
                    "id": card.id,
                    "title": card.title,
                    "description": card.description,
                    "status": card.status,
                    "position": card.position,
                    "color": card.color,
                    "assigned_to": (
                        card.assigned_to.username if card.assigned_to else None
                    ),
                    "assigned_to_id": card.assigned_to_id,
                    "updated_by": current_user.username,
                },
                room=f"team_{current_user.team_id}",
            )

    @socketio.on("delete_card")
    def handle_delete_card(data):
        if not current_user.is_authenticated:
            return

        card = Card.query.get(data["id"])

        if card and card.team_id == current_user.team_id:
            # Deletar permanentemente (histórico será deletado em cascata)
            db.session.delete(card)
            db.session.commit()

            emit(
                "card_deleted",
                {"id": data["id"], "deleted_by": current_user.username},
                room=f"team_{current_user.team_id}",
            )
