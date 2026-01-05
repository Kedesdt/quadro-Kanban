from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Team, PasswordResetToken

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("kanban.kanban"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("kanban.kanban"))
        else:
            flash("Usuário ou senha inválidos", "error")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        team_name = request.form.get("team_name")

        if User.query.filter_by(username=username).first():
            flash("Usuário já existe", "error")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        # Criar admin
        new_user = User(username=username, password=hashed_password, is_admin=True)
        db.session.add(new_user)
        db.session.commit()

        # Criar equipe
        new_team = Team(name=team_name, admin_id=new_user.id)
        db.session.add(new_team)
        db.session.commit()

        # Associar admin à equipe
        new_user.team_id = new_team.id
        db.session.commit()

        flash("Conta criada com sucesso!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Página para redefinir senha usando token"""
    # Verificar se o token é válido
    user = PasswordResetToken.verify_token(token)

    if not user:
        flash("Link de redefinição inválido ou expirado.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or len(new_password) < 4:
            flash("A senha deve ter pelo menos 4 caracteres.", "error")
            return render_template(
                "reset_password.html", token=token, username=user.username
            )

        if new_password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template(
                "reset_password.html", token=token, username=user.username
            )

        # Atualizar senha
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Marcar token como usado
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        reset_token.mark_as_used()

        flash("Senha redefinida com sucesso! Faça login com sua nova senha.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token, username=user.username)
