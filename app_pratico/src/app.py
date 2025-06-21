from flask import Flask, send_from_directory, jsonify
from datetime import timedelta
import os
from pathlib import Path

# Blueprints
from models.user import db
from routes.auth import auth_bp
from routes.topics import topics_bp
from routes.study import study_bp
from routes.revisions import revisions_bp
from routes.edital import edital_bp

def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    
    # Configuração para Render
    app.config.update(
        SECRET_KEY=os.environ['FLASK_SECRET_KEY'],
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///instance/praticante_app.db').replace(
            'postgres://', 'postgresql://'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Inicialização do banco
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(revisions_bp, url_prefix="/api/revisions")
    app.register_blueprint(edital_bp, url_prefix="/api/edital")

    # Criar tabelas
    with app.app_context():
        db.create_all()

    # Rotas
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "database": app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1]
        })

    @app.route('/')
    def serve_spa():
        return send_from_directory(app.static_folder, 'index.html')

    return app

# Aplicação para o Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
