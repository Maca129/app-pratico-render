import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from datetime import timedelta
import sys

# Adiciona o diretório src ao PATH para imports absolutos
sys.path.append(str(Path(__file__).parent))

# Imports absolutos corrigidos
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.topics import topics_bp
from src.routes.study import study_bp
from src.routes.revisions import revisions_bp
from src.routes.edital import edital_bp

def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    
    # Configuração para Render (com fallbacks seguros)
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-key-123'),  # Fallback para desenvolvimento
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///instance/praticante_app.db').replace(
            'postgres://', 'postgresql://', 1),  # Corrige para PostgreSQL no Render
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True}  # Conexões persistentes
    )

    # Inicialização do banco
    db.init_app(app)
    
    # Registrar blueprints com prefixo API
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(revisions_bp, url_prefix="/api/revisions")
    app.register_blueprint(edital_bp, url_prefix="/api/edital")

    # Criar tabelas (apenas se não existirem)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Erro ao criar tabelas: {str(e)}")

    # Rotas básicas
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "environment": "production" if 'RENDER' in os.environ else "development"
        })

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app

# Aplicação para o Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
