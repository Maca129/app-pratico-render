from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.topic import Topic
from src.models.study import QuestionRecord, StudySession, EditalItem, EditalProgress
import logging

study_bp = Blueprint('study', __name__)
logger = logging.getLogger(__name__)

# Rotas para sessões de estudo
@study_bp.route('/sessions', methods=['GET'])
def get_study_sessions():
    """Obter todas as sessões de estudo do usuário atual"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros de filtro opcionais
    topic_id = request.args.get('topic_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Construir a consulta base
    query = StudySession.query.filter_by(user_id=user_id)
    
    # Aplicar filtros se fornecidos
    if topic_id:
        query = query.filter(StudySession.topic_id == topic_id)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(StudySession.start_time >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(StudySession.start_time <= end_date)
        except ValueError:
            pass
    
    # Ordenar por data de início (mais recentes primeiro)
    sessions = query.order_by(StudySession.start_time.desc()).all()
    
    return jsonify([session.to_dict() for session in sessions])

@study_bp.route('/sessions', methods=['POST'])
def create_study_session():
    """Criar uma nova sessão de estudo"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    # Criar nova sessão de estudo
    study_session = StudySession(
        user_id=user_id,
        topic_id=data.get('topic_id'),
        description=data.get('description')
    )
    
    # Se fornecido, definir horário de início personalizado
    if 'start_time' in data:
        try:
            study_session.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Formato de data inválido para start_time"}), 400
    
    # Se fornecido, definir horário de término e calcular duração
    if 'end_time' in data:
        try:
            study_session.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            study_session.calculate_duration()
        except ValueError:
            return jsonify({"error": "Formato de data inválido para end_time"}), 400
    
    try:
        db.session.add(study_session)
        db.session.commit()
        return jsonify(study_session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar sessão de estudo: {str(e)}")
        return jsonify({"error": "Erro ao criar sessão de estudo"}), 500

@study_bp.route('/sessions/<int:session_id>', methods=['PUT'])
def update_study_session(session_id):
    """Atualizar uma sessão de estudo existente"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Verificar se a sessão existe e pertence ao usuário
    study_session = StudySession.query.filter_by(id=session_id, user_id=user_id).first()
    
    if not study_session:
        return jsonify({"error": "Sessão de estudo não encontrada ou acesso negado"}), 404
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    # Atualizar campos permitidos
    if 'topic_id' in data:
        study_session.topic_id = data['topic_id']
    
    if 'description' in data:
        study_session.description = data['description']
    
    if 'start_time' in data:
        try:
            study_session.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Formato de data inválido para start_time"}), 400
    
    if 'end_time' in data:
        try:
            study_session.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            study_session.calculate_duration()
        except ValueError:
            return jsonify({"error": "Formato de data inválido para end_time"}), 400
    
    try:
        db.session.commit()
        return jsonify(study_session.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar sessão de estudo: {str(e)}")
        return jsonify({"error": "Erro ao atualizar sessão de estudo"}), 500

@study_bp.route('/sessions/<int:session_id>/end', methods=['POST'])
def end_study_session(session_id):
    """Finalizar uma sessão de estudo em andamento"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Verificar se a sessão existe e pertence ao usuário
    study_session = StudySession.query.filter_by(id=session_id, user_id=user_id).first()
    
    if not study_session:
        return jsonify({"error": "Sessão de estudo não encontrada ou acesso negado"}), 404
    
    if study_session.end_time:
        return jsonify({"error": "Esta sessão de estudo já foi finalizada"}), 400
    
    # Finalizar a sessão
    study_session.end_time = datetime.utcnow()
    study_session.calculate_duration()
    
    try:
        db.session.commit()
        return jsonify(study_session.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao finalizar sessão de estudo: {str(e)}")
        return jsonify({"error": "Erro ao finalizar sessão de estudo"}), 500

# Rotas para registros de questões
@study_bp.route('/questions', methods=['GET'])
def get_question_records():
    """Obter todos os registros de questões do usuário atual"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros de filtro opcionais
    topic_id = request.args.get('topic_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    difficulty = request.args.get('difficulty_level')
    
    # Construir a consulta base
    query = QuestionRecord.query.filter_by(user_id=user_id)
    
    # Aplicar filtros se fornecidos
    if topic_id:
        query = query.filter(QuestionRecord.topic_id == topic_id)
    
    if difficulty:
        query = query.filter(QuestionRecord.difficulty_level == difficulty)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(QuestionRecord.date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(QuestionRecord.date <= end_date)
        except ValueError:
            pass
    
    # Ordenar por data (mais recentes primeiro)
    records = query.order_by(QuestionRecord.date.desc()).all()
    
    return jsonify([record.to_dict() for record in records])

@study_bp.route('/questions', methods=['POST'])
def create_question_record():
    """Criar um novo registro de questões"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data or 'total_questions' not in data or 'correct_answers' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    # Calcular respostas erradas se não fornecidas
    if 'wrong_answers' not in data:
        data['wrong_answers'] = data['total_questions'] - data['correct_answers']
    
    # Criar novo registro de questões
    record = QuestionRecord(
        user_id=user_id,
        topic_id=data.get('topic_id'),
        source=data.get('source'),
        specific_topic=data.get('specific_topic'),
        difficulty_level=data.get('difficulty_level'),
        total_questions=data['total_questions'],
        correct_answers=data['correct_answers'],
        wrong_answers=data['wrong_answers'],
        notes=data.get('notes')
    )
    
    # Se fornecido, definir data personalizada
    if 'date' in data:
        try:
            record.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Formato de data inválido"}), 400
    
    # Calcular porcentagem de acertos
    record.calculate_accuracy()
    
    try:
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar registro de questões: {str(e)}")
        return jsonify({"error": "Erro ao criar registro de questões"}), 500

@study_bp.route('/questions/<int:record_id>', methods=['PUT'])
def update_question_record(record_id):
    """Atualizar um registro de questões existente"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Verificar se o registro existe e pertence ao usuário
    record = QuestionRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({"error": "Registro de questões não encontrado ou acesso negado"}), 404
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    # Atualizar campos permitidos
    if 'topic_id' in data:
        record.topic_id = data['topic_id']
    
    if 'source' in data:
        record.source = data['source']
    
    if 'specific_topic' in data:
        record.specific_topic = data['specific_topic']
    
    if 'difficulty_level' in data:
        record.difficulty_level = data['difficulty_level']
    
    if 'total_questions' in data:
        record.total_questions = data['total_questions']
    
    if 'correct_answers' in data:
        record.correct_answers = data['correct_answers']
    
    if 'wrong_answers' in data:
        record.wrong_answers = data['wrong_answers']
    
    if 'notes' in data:
        record.notes = data['notes']
    
    if 'date' in data:
        try:
            record.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Formato de data inválido"}), 400
    
    # Recalcular porcentagem de acertos
    record.calculate_accuracy()
    
    try:
        db.session.commit()
        return jsonify(record.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar registro de questões: {str(e)}")
        return jsonify({"error": "Erro ao atualizar registro de questões"}), 500

@study_bp.route('/questions/stats', methods=['GET'])
def get_question_stats():
    """Obter estatísticas de desempenho em questões para visualização gráfica"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Parâmetros de filtro opcionais
    group_by = request.args.get('group_by', 'topic')  # topic, date, difficulty
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Filtrar por intervalo de datas
    query = QuestionRecord.query.filter_by(user_id=user_id)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(QuestionRecord.date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(QuestionRecord.date <= end_date)
        except ValueError:
            pass
    
    records = query.all()
    
    # Processar estatísticas de acordo com o agrupamento solicitado
    if group_by == 'topic':
        # Agrupar por tópico
        stats = {}
        for record in records:
            topic_name = "Sem tópico"
            if record.topic_id:
                topic = Topic.query.get(record.topic_id)
                if topic:
                    topic_name = topic.name
            
            if topic_name not in stats:
                stats[topic_name] = {
                    'total_questions': 0,
                    'correct_answers': 0,
                    'wrong_answers': 0,
                    'accuracy': 0
                }
            
            stats[topic_name]['total_questions'] += record.total_questions
            stats[topic_name]['correct_answers'] += record.correct_answers
            stats[topic_name]['wrong_answers'] += record.wrong_answers
        
        # Calcular precisão para cada tópico
        for topic_name in stats:
            if stats[topic_name]['total_questions'] > 0:
                stats[topic_name]['accuracy'] = (stats[topic_name]['correct_answers'] / stats[topic_name]['total_questions']) * 100
        
        # Formatar para visualização em gráfico
        chart_data = {
            'labels': list(stats.keys()),
            'datasets': [
                {
                    'label': 'Acertos (%)',
                    'data': [stats[topic]['accuracy'] for topic in stats]
                },
                {
                    'label': 'Total de Questões',
                    'data': [stats[topic]['total_questions'] for topic in stats]
                }
            ]
        }
    
    elif group_by == 'date':
        # Agrupar por mês
        stats = {}
        for record in records:
            month_key = record.date.strftime('%Y-%m')
            month_label = record.date.strftime('%b/%Y')
            
            if month_key not in stats:
                stats[month_key] = {
                    'label': month_label,
                    'total_questions': 0,
                    'correct_answers': 0,
                    'wrong_answers': 0,
                    'accuracy': 0
                }
            
            stats[month_key]['total_questions'] += record.total_questions
            stats[month_key]['correct_answers'] += record.correct_answers
            stats[month_key]['wrong_answers'] += record.wrong_answers
        
        # Calcular precisão para cada mês
        for month_key in stats:
            if stats[month_key]['total_questions'] > 0:
                stats[month_key]['accuracy'] = (stats[month_key]['correct_answers'] / stats[month_key]['total_questions']) * 100
        
        # Ordenar por data
        sorted_months = sorted(stats.keys())
        
        # Formatar para visualização em gráfico
        chart_data = {
            'labels': [stats[month]['label'] for month in sorted_months],
            'datasets': [
                {
                    'label': 'Acertos (%)',
                    'data': [stats[month]['accuracy'] for month in sorted_months]
                },
                {
                    'label': 'Total de Questões',
                    'data': [stats[month]['total_questions'] for month in sorted_months]
                }
            ]
        }
    
    elif group_by == 'difficulty':
        # Agrupar por nível de dificuldade
        stats = {
            'Fácil': {'total_questions': 0, 'correct_answers': 0, 'wrong_answers': 0, 'accuracy': 0},
            'Médio': {'total_questions': 0, 'correct_answers': 0, 'wrong_answers': 0, 'accuracy': 0},
            'Difícil': {'total_questions': 0, 'correct_answers': 0, 'wrong_answers': 0, 'accuracy': 0},
            'Não especificado': {'total_questions': 0, 'correct_answers': 0, 'wrong_answers': 0, 'accuracy': 0}
        }
        
        for record in records:
            difficulty = record.difficulty_level if record.difficulty_level else 'Não especificado'
            
            stats[difficulty]['total_questions'] += record.total_questions
            stats[difficulty]['correct_answers'] += record.correct_answers
            stats[difficulty]['wrong_answers'] += record.wrong_answers
        
        # Calcular precisão para cada nível de dificuldade
        for difficulty in stats:
            if stats[difficulty]['total_questions'] > 0:
                stats[difficulty]['accuracy'] = (stats[difficulty]['correct_answers'] / stats[difficulty]['total_questions']) * 100
        
        # Formatar para visualização em gráfico
        chart_data = {
            'labels': list(stats.keys()),
            'datasets': [
                {
                    'label': 'Acertos (%)',
                    'data': [stats[difficulty]['accuracy'] for difficulty in stats]
                },
                {
                    'label': 'Total de Questões',
                    'data': [stats[difficulty]['total_questions'] for difficulty in stats]
                }
            ]
        }
    
    else:
        return jsonify({"error": "Tipo de agrupamento inválido"}), 400
    
    return jsonify(chart_data)

# Rotas para edital
@study_bp.route('/edital', methods=['GET'])
def get_edital_items():
    """Obter itens do edital"""
    # Parâmetros de filtro opcionais
    section = request.args.get('section')
    
    # Construir a consulta base
    query = EditalItem.query
    
    # Aplicar filtros se fornecidos
    if section:
        query = query.filter(EditalItem.section == section)
    
    # Ordenar por índice
    items = query.order_by(EditalItem.order_index).all()
    
    return jsonify([item.to_dict() for item in items])

@study_bp.route('/edital/progress', methods=['GET'])
def get_edital_progress():
    """Obter progresso do usuário no edital"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # Obter todos os itens do edital
    edital_items = EditalItem.query.order_by(EditalItem.order_index).all()
    
    # Obter progresso do usuário
    progress_records = EditalProgress.query.filter_by(user_id=user_id).all()
    
    # Mapear progresso por item do edital
    progress_map = {record.edital_item_id: record for record in progress_records}
    
    # Construir resposta combinando itens e progresso
    result = []
    for item in edital_items:
        progress = progress_map.get(item.id)
        
        item_data = item.to_dict()
        if progress:
            item_data.update({
                'is_studied': progress.is_studied,
                'study_date': progress.study_date.isoformat() if progress.study_date else None,
                'confidence_level': progress.confidence_level,
                'notes': progress.notes
            })
        else:
            item_data.update({
                'is_studied': False,
                'study_date': None,
                'confidence_level': 'Baixo',
                'notes': None
            })
        
        result.append(item_data)
    
    return jsonify(result)

@study_bp.route('/edital/mark', methods=['POST'])
def mark_edital_item():
    """Marcar um item do edital como estudado"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data or 'edital_item_id' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    
    # Verificar se o item do edital existe
    edital_item = EditalItem.query.get(data['edital_item_id'])
    if not edital_item:
        return jsonify({"error": "Item do edital não encontrado"}), 404
    
    # Verificar se já existe um registro de progresso para este item
    progress = EditalProgress.query.filter_by(
        user_id=user_id,
        edital_item_id=data['edital_item_id']
    ).first()
    
    if not progress:
        # Criar novo registro de progresso
        progress = EditalProgress(
            user_id=user_id,
            edital_item_id=data['edital_item_id']
        )
        db.session.add(progress)
    
    # Atualizar campos
    progress.is_studied = data.get('is_studied', True)
    
    if progress.is_studied and not progress.study_date:
        progress.study_date = datetime.utcnow()
    
    if 'confidence_level' in data:
        progress.confidence_level = data['confidence_level']
    
    if 'notes' in data:
        progress.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify(progress.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao marcar item do edital: {str(e)}")
        return jsonify({"error": "Erro ao marcar item do edital"}), 500

@study_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Obter dados consolidados para o dashboard"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = session['user_id']
    
    # 1. Progresso por grupo de matérias
    topics = Topic.query.filter_by(user_id=user_id).all()
    topics_by_group = {}
    
    for topic in topics:
        if topic.group_id not in topics_by_group:
            topics_by_group[topic.group_id] = {
                'group_id': topic.group_id,
                'group_name': topic.group_name,
                'total': 0,
                'completed': 0,
                'percentage': 0
            }
        
        topics_by_group[topic.group_id]['total'] += 1
        if topic.is_completed:
            topics_by_group[topic.group_id]['completed'] += 1
    
    # Calcular percentuais
    for group_id in topics_by_group:
        if topics_by_group[group_id]['total'] > 0:
            topics_by_group[group_id]['percentage'] = (topics_by_group[group_id]['completed'] / topics_by_group[group_id]['total']) * 100
    
    # 2. Horas estudadas
    study_sessions = StudySession.query.filter_by(user_id=user_id).all()
    total_minutes = sum(session.duration_minutes or 0 for session in study_sessions)
    total_hours = total_minutes / 60
    
    # Horas por grupo
    hours_by_group = {}
    for session in study_sessions:
        if not session.topic_id or not session.duration_minutes:
            continue
        
        topic = Topic.query.get(session.topic_id)
        if not topic:
            continue
        
        if topic.group_id not in hours_by_group:
            hours_by_group[topic.group_id] = {
                'group_name': topic.group_name,
                'minutes': 0
            }
        
        hours_by_group[topic.group_id]['minutes'] += session.duration_minutes
    
    # Converter minutos para horas
    for group_id in hours_by_group:
        hours_by_group[group_id]['hours'] = hours_by_group[group_id]['minutes'] / 60
    
    # 3. Desempenho em questões
    question_records = QuestionRecord.query.filter_by(user_id=user_id).all()
    total_questions = sum(record.total_questions for record in question_records)
    total_correct = sum(record.correct_answers for record in question_records)
    
    overall_accuracy = 0
    if total_questions > 0:
        overall_accuracy = (total_correct / total_questions) * 100
    
    # Desempenho por grupo
    accuracy_by_group = {}
    for record in question_records:
        if not record.topic_id:
            continue
        
        topic = Topic.query.get(record.topic_id)
        if not topic:
            continue
        
        if topic.group_id not in accuracy_by_group:
            accuracy_by_group[topic.group_id] = {
                'group_name': topic.group_name,
                'total_questions': 0,
                'correct_answers': 0,
                'accuracy': 0
            }
        
        accuracy_by_group[topic.group_id]['total_questions'] += record.total_questions
        accuracy_by_group[topic.group_id]['correct_answers'] += record.correct_answers
    
    # Calcular precisão por grupo
    for group_id in accuracy_by_group:
        if accuracy_by_group[group_id]['total_questions'] > 0:
            accuracy_by_group[group_id]['accuracy'] = (
                accuracy_by_group[group_id]['correct_answers'] / 
                accuracy_by_group[group_id]['total_questions']
            ) * 100
    
    # 4. Progresso no edital
    edital_items = EditalItem.query.count()
    studied_items = EditalProgress.query.filter_by(user_id=user_id, is_studied=True).count()
    
    edital_progress = 0
    if edital_items > 0:
        edital_progress = (studied_items / edital_items) * 100
    
    # Consolidar todos os dados
    dashboard_data = {
        'progress_by_group': list(topics_by_group.values()),
        'study_hours': {
            'total_hours': total_hours,
            'by_group': list(hours_by_group.values())
        },
        'question_performance': {
            'total_questions': total_questions,
            'total_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'by_group': list(accuracy_by_group.values())
        },
        'edital_progress': {
            'total_items': edital_items,
            'studied_items': studied_items,
            'percentage': edital_progress
        }
    }
    
    return jsonify(dashboard_data)
