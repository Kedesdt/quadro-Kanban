from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Team

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
