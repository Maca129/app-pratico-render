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

def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    
    # Configuração de segurança
    app.secret_key = os.environ["FLASK_SECRET_KEY"]  # Exigir variável de ambiente
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # Configuração do Banco de Dados
    DATABASE_DIR = os.environ.get("DATABASE_DIR", "/var/data")
    DATABASE_PATH = os.path.join(DATABASE_DIR, "praticante_app.db")
    os.makedirs(DATABASE_DIR, exist_ok=True)
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
        db.create_all()
        logger.info("Database tables created")

    # Rota para Single Page Application (SPA)
    @app.route("/")
    def serve_spa():
        return send_from_directory(app.static_folder, "index.html")
    
    # Rota para tratar atualizações do React Router
    @app.route("/<path:path>")
    def catch_all(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app


 
       
