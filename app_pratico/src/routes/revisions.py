from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.topic import Topic, Revision
from src.models.notification import Notification, NotificationPreference
import logging

revisions_bp = Blueprint('revisions', __name__)
logger = logging.getLogger(__name__)

@revisions_bp.route('/', methods=['GET'])
def get_revisions():
    """Obter todas as revisões do usuário atual"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros de filtro opcionais
    is_completed = request.args.get('is_completed')
    topic_id = request.args.get('topic_id')
    
    # Construir a consulta base
    query = db.session.query(Revision).join(Topic).filter(Topic.user_id == user_id)
    
    # Aplicar filtros se fornecidos
    if is_completed is not None:
        is_completed = is_completed.lower() == 'true'
        query = query.filter(Revision.is_completed == is_completed)
    
    if topic_id:
        query = query.filter(Revision.topic_id == topic_id)
    
    # Ordenar por data programada
    revisions = query.order_by(Revision.scheduled_date).all()
    
    return jsonify([revision.to_dict() for revision in revisions])

@revisions_bp.route('/calendar', methods=['GET'])
def get_calendar_revisions():
    """Obter revisões formatadas para visualização em calendário"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros para intervalo de datas (opcional)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    # Construir a consulta base
    query = db.session.query(Revision).join(Topic).filter(Topic.user_id == user_id)
    
    # Aplicar filtros de data se fornecidos
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Revision.scheduled_date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Revision.scheduled_date <= end_date)
        except ValueError:
            pass
    
    revisions = query.all()
    
    return jsonify([revision.to_calendar_dict() for revision in revisions])

@revisions_bp.route('/<int:revision_id>', methods=['PUT'])
def update_revision(revision_id):
    """Atualizar uma revisão específica"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Verificar se a revisão existe e pertence ao usuário
    revision = db.session.query(Revision).join(Topic).filter(
        Revision.id == revision_id,
        Topic.user_id == user_id
    ).first()
    
    if not revision:
        return jsonify({"error": "Revisão não encontrada ou acesso negado"}), 404
    
    data = request.json
    
    # Atualizar campos permitidos
    if 'is_completed' in data:
        revision.is_completed = data['is_completed']
        if data['is_completed']:
            revision.completed_at = datetime.utcnow()
        else:
            revision.completed_at = None
    
    if 'notes' in data:
        revision.notes = data['notes']
    
    if 'scheduled_date' in data:
        try:
            revision.scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Formato de data inválido"}), 400
    
    if 'notify' in data:
        revision.notify = data['notify']
    
    if 'color' in data:
        revision.color = data['color']
    
    try:
        db.session.commit()
        return jsonify(revision.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar revisão: {str(e)}")
        return jsonify({"error": "Erro ao atualizar revisão"}), 500

@revisions_bp.route('/mark-completed/<int:revision_id>', methods=['POST'])
def mark_revision_completed(revision_id):
    """Marcar uma revisão como concluída"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Verificar se a revisão existe e pertence ao usuário
    revision = db.session.query(Revision).join(Topic).filter(
        Revision.id == revision_id,
        Topic.user_id == user_id
    ).first()
    
    if not revision:
        return jsonify({"error": "Revisão não encontrada ou acesso negado"}), 404
    
    revision.is_completed = True
    revision.completed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Revisão marcada como concluída"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao marcar revisão como concluída: {str(e)}")
        return jsonify({"error": "Erro ao marcar revisão como concluída"}), 500

@revisions_bp.route('/notifications/preferences', methods=['GET', 'POST'])
def notification_preferences():
    """Obter ou atualizar preferências de notificação"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Obter preferências atuais
        prefs = NotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not prefs:
            # Criar preferências padrão se não existirem
            prefs = NotificationPreference(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()
        
        return jsonify(prefs.to_dict())
    
    elif request.method == 'POST':
        # Atualizar preferências
        data = request.json
        prefs = NotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.session.add(prefs)
        
        if 'enable_browser_notifications' in data:
            prefs.enable_browser_notifications = data['enable_browser_notifications']
        
        if 'enable_email_notifications' in data:
            prefs.enable_email_notifications = data['enable_email_notifications']
        
        if 'reminder_minutes_before' in data:
            prefs.reminder_minutes_before = data['reminder_minutes_before']
        
        try:
            db.session.commit()
            return jsonify(prefs.to_dict())
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar preferências de notificação: {str(e)}")
            return jsonify({"error": "Erro ao atualizar preferências de notificação"}), 500

@revisions_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Obter notificações do usuário"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros de filtro opcionais
    is_read = request.args.get('is_read')
    
    # Construir a consulta base
    query = Notification.query.filter_by(user_id=user_id)
    
    # Aplicar filtros se fornecidos
    if is_read is not None:
        is_read = is_read.lower() == 'true'
        query = query.filter(Notification.is_read == is_read)
    
    # Ordenar por data de criação (mais recentes primeiro)
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    return jsonify([notification.to_dict() for notification in notifications])

@revisions_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    """Marcar uma notificação como lida"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if not notification:
        return jsonify({"error": "Notificação não encontrada ou acesso negado"}), 404
    
    notification.is_read = True
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Notificação marcada como lida"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({"error": "Erro ao marcar notificação como lida"}), 500

@revisions_bp.route('/create-notification', methods=['POST'])
def create_notification():
    """Criar uma notificação manualmente (para testes)"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data or 'title' not in data or 'message' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    notification = Notification(
        user_id=user_id,
        title=data['title'],
        message=data['message'],
        revision_id=data.get('revision_id')
    )
    
    try:
        db.session.add(notification)
        db.session.commit()
        return jsonify(notification.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar notificação: {str(e)}")
        return jsonify({"error": "Erro ao criar notificação"}), 500
