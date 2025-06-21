import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session, jsonify
from datetime import timedelta
import sqlite3
import traceback

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar modelos
from src.models.user import db, User
from src.models.topic import Topic, Revision
from src.models.study import StudySession, QuestionRecord, EditalItem, EditalProgress
from src.models.notification import Notification, NotificationPreference

# Importar blueprints
from src.routes.auth import auth_bp
from src.routes.topics import topics_bp
from src.routes.study import study_bp
from src.routes.revisions import revisions_bp
from src.routes.edital import edital_bp

def create_app(environ=None, start_response=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    
    # Configuração de segurança
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # Configuração do Banco de Dados
    if 'DATABASE_URL' in os.environ:
        # Configuração para PostgreSQL no Render
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace(
            'postgres://', 'postgresql://')
    else:
        # Configuração para SQLite local
        DATABASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
        os.makedirs(DATABASE_DIR, exist_ok=True)
        DATABASE_PATH = os.path.join(DATABASE_DIR, "praticante_app.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Inicializar SQLAlchemy
    db.init_app(app)
    
    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(revisions_bp)
    app.register_blueprint(edital_bp)

    # Criar tabelas no contexto da aplicação
    with app.app_context():
        try:
            db.create_all()
            logger.info("Tabelas do banco criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas do banco: {str(e)}")
            logger.error(traceback.format_exc())

    # Rota para Single Page Application (SPA)
    @app.route("/")
    def serve_spa():
        return send_from_directory(app.static_folder, "index.html")
    
    # Rota para tratamento do React Router
    @app.route("/<path:path>")
    def catch_all(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    # Para compatibilidade com Gunicorn
    if environ is not None and start_response is not None:
        return app(environ, start_response)
    return app

# Para execução com Gunicorn
application = create_app()
