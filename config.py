import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()


class Config:
    """Configuração base da aplicação"""

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-aqui-mude-em-producao")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///kanban.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""

    DEBUG = True


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""

    DEBUG = False


# Dicionário de configurações
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Retorna a configuração baseada no ambiente"""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
