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

# Importar modelos para criação das tabelas
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
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey") # É crucial definir uma chave secreta segura
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # Configuração do Banco de Dados SQLite (mais simples para desenvolvimento)
    DATABASE_DIR = os.environ.get("DATABASE_DIR", "/var/data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "praticante_app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
   app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Habilitar logs de exceções SQL
    app.config["SQLALCHEMY_ECHO"] = True

    # Configurar CORS para permitir requisições do frontend
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(revisions_bp, url_prefix="/api/revisions")
    app.register_blueprint(edital_bp, url_prefix="/api/edital")

    @app.route("/")
    def index():
        return send_from_directory("static", "index.html")
        
    @app.errorhandler(Exception)
    def handle_error(e):
        error_traceback = traceback.format_exc()
        logger.error(f"Erro não tratado: {str(e)}\n{error_traceback}")
        return jsonify({"error": "Erro interno do servidor. Verifique os logs."}), 500

    with app.app_context():
        try:
            logger.info("Criando tabelas do banco de dados...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Erro ao criar tabelas: {str(e)}\n{error_traceback}")
            raise

    return app

# Criar uma instância do app para uso em scripts externos
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
