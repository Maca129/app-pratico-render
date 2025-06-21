from flask import Flask, send_from_directory, jsonify
from datetime import timedelta
import os
import traceback

from models.user import db
from routes.auth import auth_bp
from routes.topics import topics_bp
from routes.study import study_bp
from routes.revisions import revisions_bp
from routes.edital import edital_bp

def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")

    # Segurança
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # Banco de Dados
    if 'DATABASE_URL' in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace(
            'postgres://', 'postgresql://'
        )
    else:
        db_path = os.path.join('/tmp', 'praticante_app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar banco
    db.init_app(app)

    # Registrar rotas
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(revisions_bp, url_prefix="/api/revisions")
    app.register_blueprint(edital_bp, url_prefix="/api/edital")

    # Criar tabelas
    with app.app_context():
        try:
            db.create_all()
            print("Banco de dados inicializado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
            print(traceback.format_exc())

    # Health check
    @app.route("/ping")
    def ping():
        return jsonify({"status": "online"}), 200

    # SPA fallback
    @app.route("/")
    def serve_spa():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def catch_all(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app


# Instância para o Gunicorn
application = create_app()
