from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from models import db, User
from config import get_config

# Inicializar extensões
login_manager = LoginManager()
socketio = SocketIO()


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
    socketio.init_app(app, cors_allowed_origins=app.config["CORS_ALLOWED_ORIGINS"])

    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.kanban import kanban_bp
    from routes.team import team_bp
    from routes.export import export_bp
    from routes.history import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(kanban_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(history_bp)

    # Registrar eventos WebSocket
    from routes.websocket import register_websocket_events

    register_websocket_events(socketio)

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
    socketio.run(app, debug=config.DEBUG, host=config.HOST, port=config.PORT)
