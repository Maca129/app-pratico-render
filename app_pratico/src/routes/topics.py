from flask import Blueprint, request, jsonify, session
from src.models.topic import Topic, Revision
from src.models.user import db
from datetime import datetime, timedelta

topics_bp = Blueprint('topics', __name__)

@topics_bp.route('/', methods=['GET'])
def get_topics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar todos os tópicos do usuário
    topics = Topic.query.filter_by(user_id=user_id).all()
    return jsonify({
        'topics': [topic.to_dict() for topic in topics]
    }), 200

@topics_bp.route('/', methods=['POST'])
def create_topic():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    
    # Verificar se os campos necessários estão presentes
    if not data or not data.get('name') or not data.get('group_id') or not data.get('group_name'):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    # Criar novo tópico
    new_topic = Topic(
        user_id=user_id,
        name=data['name'],
        group_id=data['group_id'],
        group_name=data['group_name'],
        description=data.get('description', ''),
        confidence_level=data.get('confidence_level', 'Baixo')
    )
    
    db.session.add(new_topic)
    db.session.commit()
    
    # Se o usuário quiser criar revisões automaticamente
    if data.get('create_revisions', False):
        try:
            create_revision_schedule(new_topic.id)
        except Exception as e:
            # Logar o erro, mas não falhar a criação do tópico
            print(f"Erro ao criar revisões: {str(e)}")
    
    return jsonify({
        'message': 'Tópico criado com sucesso',
        'topic': new_topic.to_dict()
    }), 201

@topics_bp.route('/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar o tópico
    topic = Topic.query.filter_by(id=topic_id, user_id=user_id).first()
    if not topic:
        return jsonify({'error': 'Tópico não encontrado'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'name' in data:
        topic.name = data['name']
    if 'description' in data:
        topic.description = data['description']
    if 'is_completed' in data:
        topic.is_completed = data['is_completed']
        if data['is_completed'] and not topic.completed_at:
            topic.completed_at = datetime.utcnow()
        elif not data['is_completed']:
            topic.completed_at = None
    if 'confidence_level' in data:
        topic.confidence_level = data['confidence_level']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Tópico atualizado com sucesso',
        'topic': topic.to_dict()
    }), 200

@topics_bp.route('/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar o tópico
    topic = Topic.query.filter_by(id=topic_id, user_id=user_id).first()
    if not topic:
        return jsonify({'error': 'Tópico não encontrado'}), 404
    
    db.session.delete(topic)
    db.session.commit()
    
    return jsonify({
        'message': 'Tópico excluído com sucesso'
    }), 200

@topics_bp.route('/<int:topic_id>/revisions', methods=['GET'])
def get_revisions(topic_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Verificar se o tópico pertence ao usuário
    topic = Topic.query.filter_by(id=topic_id, user_id=user_id).first()
    if not topic:
        return jsonify({'error': 'Tópico não encontrado'}), 404
    
    # Buscar revisões do tópico
    revisions = Revision.query.filter_by(topic_id=topic_id).all()
    
    return jsonify({
        'revisions': [revision.to_dict() for revision in revisions]
    }), 200

@topics_bp.route('/<int:topic_id>/revisions', methods=['POST'])
def create_revision_schedule_endpoint(topic_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Verificar se o tópico pertence ao usuário
    topic = Topic.query.filter_by(id=topic_id, user_id=user_id).first()
    if not topic:
        return jsonify({'error': 'Tópico não encontrado'}), 404
    
    # Chamar a função que realmente cria as revisões
    create_revision_schedule(topic_id)
    
    return jsonify({
        'message': 'Cronograma de revisões criado com sucesso'
    }), 201

def create_revision_schedule(topic_id):
    """Função interna para criar revisões programadas para um tópico"""
    # Verificar se o tópico existe
    topic = Topic.query.get(topic_id)
    if not topic:
        return
    
    # Definir intervalos para as revisões (em dias)
    intervals = [1, 7, 15, 30, 60]
    
    # Data inicial (hoje)
    start_date = datetime.utcnow()
    
    # Criar revisões
    for i, interval in enumerate(intervals):
        if i == 0:
            # Primeira revisão: 1 dia após hoje
            revision_date = start_date + timedelta(days=interval)
        else:
            # Revisões subsequentes: baseadas na revisão anterior
            previous_revision = Revision.query.filter_by(
                topic_id=topic_id, 
                revision_number=i
            ).first()
            
            if previous_revision:
                revision_date = previous_revision.scheduled_date + timedelta(days=interval)
            else:
                # Fallback se algo der errado
                revision_date = start_date + timedelta(days=sum(intervals[:i+1]))
        
        # Criar nova revisão
        new_revision = Revision(
            topic_id=topic_id,
            scheduled_date=revision_date,
            revision_number=i+1,
            is_completed=False
        )
        
        db.session.add(new_revision)
    
    db.session.commit()

@topics_bp.route('/revisions/<int:revision_id>', methods=['PUT'])
def update_revision(revision_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar a revisão
    revision = Revision.query.get(revision_id)
    if not revision:
        return jsonify({'error': 'Revisão não encontrada'}), 404
    
    # Verificar se o tópico pertence ao usuário
    topic = Topic.query.filter_by(id=revision.topic_id, user_id=user_id).first()
    if not topic:
        return jsonify({'error': 'Não autorizado a modificar esta revisão'}), 403
    
    data = request.get_json()
    
    # Atualizar campos
    if 'is_completed' in data:
        revision.is_completed = data['is_completed']
        if data['is_completed'] and not revision.completed_at:
            revision.completed_at = datetime.utcnow()
        elif not data['is_completed']:
            revision.completed_at = None
    
    if 'notes' in data:
        revision.notes = data['notes']
    
    if 'scheduled_date' in data:
        try:
            revision.scheduled_date = datetime.fromisoformat(data['scheduled_date'])
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Revisão atualizada com sucesso',
        'revision': revision.to_dict()
    }), 200

@topics_bp.route('/upcoming-revisions', methods=['GET'])
def get_upcoming_revisions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar tópicos do usuário
    topics = Topic.query.filter_by(user_id=user_id).all()
    topic_ids = [topic.id for topic in topics]
    
    # Parâmetros de filtro opcionais
    days_ahead = request.args.get('days', default=30, type=int)  # Padrão: próximos 30 dias
    include_completed = request.args.get('include_completed', default='false', type=str).lower() == 'true'
    
    # Construir a consulta base
    query = Revision.query.filter(Revision.topic_id.in_(topic_ids))
    
    # Aplicar filtro de data
    if days_ahead > 0:
        query = query.filter(Revision.scheduled_date <= datetime.utcnow() + timedelta(days=days_ahead))
    
    # Aplicar filtro de status (concluído/pendente)
    if not include_completed:
        query = query.filter(Revision.is_completed == False)
    
    # Ordenar por data
    upcoming_revisions = query.order_by(Revision.scheduled_date).all()
    
    # Preparar dados para retorno (formato plano para facilitar consumo pelo frontend)
    result = []
    for revision in upcoming_revisions:
        topic = Topic.query.get(revision.topic_id)
        
        # Criar um dicionário plano com todos os campos necessários
        revision_dict = revision.to_dict()
        revision_dict['topic_name'] = topic.name if topic else 'Tópico desconhecido'
        revision_dict['topic_group'] = topic.group_name if topic else ''
        revision_dict['topic_description'] = topic.description if topic else ''
        
        result.append(revision_dict)
    
    return jsonify({
        'upcoming_revisions': result
    }), 200
