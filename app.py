from flask import Flask
from flask_login import LoginManager
from models import db, User
from config import get_config

# Inicializar extensões
login_manager = LoginManager()


def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)

    # Carregar configurações
    config_class = get_config()
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.kanban import kanban_bp
    from routes.team import team_bp
    from routes.export import export_bp
    from routes.history import history_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(kanban_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_bp)

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    config = get_config()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
