import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from datetime import timedelta
import sys

# Configura caminhos para imports
sys.path.append(str(Path(__file__).parent))

# Imports absolutos
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.topics import topics_bp
from src.routes.study import study_bp
from src.routes.revisions import revisions_bp
from src.routes.edital import edital_bp

def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    
    # Configurações
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-key-fallback'),
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///instance/app.db').replace(
            'postgres://', 'postgresql://', 1),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True}
    )

    # Inicializações
    db.init_app(app)
    
    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(revisions_bp, url_prefix="/api/revisions")
    app.register_blueprint(edital_bp, url_prefix="/api/edital")

    # Database
    with app.app_context():
        try:
            if not os.path.exists('instance'):
                os.makedirs('instance')
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database error: {str(e)}")

    # Rotas
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

# Interface para Gunicorn
application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
