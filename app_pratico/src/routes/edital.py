from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.topic import Topic, Revision
from src.models.study import StudySession, QuestionRecord, EditalItem, EditalProgress
from src.models.notification import Notification, NotificationPreference
import logging
import os
import re

edital_bp = Blueprint('edital', __name__)
logger = logging.getLogger(__name__)

@edital_bp.route('/import', methods=['POST'])
def import_edital():
    """Importar conteúdo do edital do arquivo de texto"""
    if 'user_id' not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    # Verificar se já existem itens do edital
    existing_items = EditalItem.query.count()
    if existing_items > 0:
        return jsonify({"error": "Edital já foi importado anteriormente"}), 400
    
    try:
        # Caminho para o arquivo do edital
        edital_file_path = '/home/ubuntu/edital_pratico_2012.txt'
        
        if not os.path.exists(edital_file_path):
            return jsonify({"error": "Arquivo do edital não encontrado"}), 404
        
        # Ler o conteúdo do arquivo
        with open(edital_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Processar o conteúdo e extrair seções
        sections = []
        current_section = None
        current_subsection = None
        current_content = []
        order_index = 0
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Pular linhas vazias
            if not line:
                continue
            
            # Detectar cabeçalhos de seção (em maiúsculas ou com numeração)
            if line.isupper() or re.match(r'^\d+\.', line):
                # Salvar seção anterior, se existir
                if current_section:
                    sections.append({
                        'section': current_section,
                        'subsection': current_subsection,
                        'content': '\n'.join(current_content),
                        'order_index': order_index
                    })
                    order_index += 1
                
                current_section = line
                current_subsection = None
                current_content = []
            
            # Detectar subseções (com letras ou números)
            elif re.match(r'^[a-z\d]\)', line) or re.match(r'^[a-z\d]\.\d', line):
                # Salvar subseção anterior, se existir
                if current_section and current_content:
                    sections.append({
                        'section': current_section,
                        'subsection': current_subsection,
                        'content': '\n'.join(current_content),
                        'order_index': order_index
                    })
                    order_index += 1
                
                current_subsection = line
                current_content = []
            
            # Conteúdo normal
            else:
                current_content.append(line)
        
        # Adicionar a última seção
        if current_section and current_content:
            sections.append({
                'section': current_section,
                'subsection': current_subsection,
                'content': '\n'.join(current_content),
                'order_index': order_index
            })
        
        # Inserir seções no banco de dados
        for section_data in sections:
            edital_item = EditalItem(
                section=section_data['section'],
                subsection=section_data['subsection'],
                content=section_data['content'],
                order_index=section_data['order_index']
            )
            db.session.add(edital_item)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Edital importado com sucesso. {len(sections)} itens criados."
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar edital: {str(e)}")
        return jsonify({"error": f"Erro ao importar edital: {str(e)}"}), 500

@edital_bp.route('/', methods=['GET'])
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
    
    # Obter seções únicas para navegação
    sections = db.session.query(EditalItem.section).distinct().all()
    sections = [s[0] for s in sections]
    
    return jsonify({
        "items": [item.to_dict() for item in items],
        "sections": sections
    })

@edital_bp.route('/progress', methods=['GET'])
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
    
    # Calcular estatísticas de progresso
    total_items = len(edital_items)
    studied_items = sum(1 for item in result if item['is_studied'])
    progress_percentage = (studied_items / total_items * 100) if total_items > 0 else 0
    
    # Agrupar por nível de confiança
    confidence_stats = {
        'Baixo': sum(1 for item in result if item['is_studied'] and item['confidence_level'] == 'Baixo'),
        'Médio': sum(1 for item in result if item['is_studied'] and item['confidence_level'] == 'Médio'),
        'Alto': sum(1 for item in result if item['is_studied'] and item['confidence_level'] == 'Alto')
    }
    
    return jsonify({
        "items": result,
        "stats": {
            "total_items": total_items,
            "studied_items": studied_items,
            "progress_percentage": progress_percentage,
            "confidence_stats": confidence_stats
        }
    })

@edital_bp.route('/mark', methods=['POST'])
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
    elif not progress.is_studied:
        progress.study_date = None
    
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
