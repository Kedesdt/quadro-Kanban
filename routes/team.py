from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Team, PasswordResetToken

team_bp = Blueprint("team", __name__)


@team_bp.route("/team", methods=["GET", "POST"])
@login_required
def team_management():
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores.", "error")
        return redirect(url_for("kanban.kanban"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_member":
            username = request.form.get("username")
            password = request.form.get("password")

            if User.query.filter_by(username=username).first():
                flash("Usuário já existe", "error")
            else:
                hashed_password = generate_password_hash(password)
                new_member = User(
                    username=username,
                    password=hashed_password,
                    is_admin=False,
                    team_id=current_user.team_id,
                )
                db.session.add(new_member)
                db.session.commit()
                flash(f"Membro {username} adicionado com sucesso!", "success")

        elif action == "remove_member":
            user_id = request.form.get("user_id")
            user = User.query.get(user_id)
            if user and user.team_id == current_user.team_id and not user.is_admin:
                db.session.delete(user)
                db.session.commit()
                flash("Membro removido com sucesso!", "success")

    team = Team.query.get(current_user.team_id)
    members = User.query.filter_by(team_id=current_user.team_id).all()

    return render_template("team.html", team=team, members=members)


@team_bp.route("/team/reset-password/<int:user_id>", methods=["POST"])
@login_required
def generate_reset_link(user_id):
    """Gera link de reset de senha para um membro da equipe"""
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores.", "error")
        return redirect(url_for("kanban.kanban"))

    user = User.query.get(user_id)

    if not user or user.team_id != current_user.team_id:
        flash("Usuário não encontrado ou não pertence à sua equipe.", "error")
        return redirect(url_for("team.team_management"))

    if user.is_admin:
        flash("Não é possível gerar link de reset para administradores.", "error")
        return redirect(url_for("team.team_management"))

    # Criar token de reset
    token = PasswordResetToken.create_token(user, hours=24)

    # Gerar URL completo
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    flash(
        f"Link de reset gerado! Envie este link para {user.username}: {reset_url}",
        "success",
    )
    return redirect(url_for("team.team_management"))
