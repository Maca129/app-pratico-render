from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User
import logging
import traceback

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        logger.info("Iniciando processo de registro")
        data = request.get_json()
        logger.debug(f"Dados recebidos: {data}")
        
        # Verificar se os campos necessários estão presentes
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            logger.warning("Dados incompletos no registro")
            return jsonify({'error': 'Dados incompletos'}), 400
        
        logger.info(f"Verificando se usuário já existe: {data['username']}")
        # Verificar se o usuário já existe
        if User.query.filter_by(username=data['username']).first():
            logger.warning(f"Nome de usuário já existe: {data['username']}")
            return jsonify({'error': 'Nome de usuário já existe'}), 400
        
        logger.info(f"Verificando se email já existe: {data['email']}")
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Email já está em uso: {data['email']}")
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Criar novo usuário
        logger.info("Criando novo usuário")
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        # Salvar no banco de dados
        logger.info("Adicionando usuário ao banco de dados")
        db.session.add(new_user)
        
        logger.info("Executando commit")
        db.session.commit()
        logger.info(f"Usuário criado com sucesso: ID={new_user.id}")
        
        # Iniciar sessão
        logger.info("Iniciando sessão do usuário")
        session['user_id'] = new_user.id
        
        logger.info("Retornando resposta de sucesso")
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': new_user.to_dict()
        }), 201
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Erro no registro: {str(e)}\n{error_traceback}")
        db.session.rollback()
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        logger.info("Iniciando processo de login")
        data = request.get_json()
        
        # Verificar se os campos necessários estão presentes
        if not data or not data.get('username') or not data.get('password'):
            logger.warning("Dados incompletos no login")
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(username=data['username']).first()
        logger.info(f"Usuário encontrado: {user is not None}")
        
        if user:
            logger.info(f"Hash da senha do usuário: {user.password_hash}")
            password_check = user.check_password(data['password'])
            logger.info(f"Verificação de senha: {password_check}")
        
        # Verificar se o usuário existe e a senha está correta
        if not user or not user.check_password(data['password']):
            logger.warning("Credenciais inválidas")
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Iniciar sessão
        logger.info(f"Login bem-sucedido para usuário: {user.username}")
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Erro no login: {str(e)}\n{error_traceback}")
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Remover usuário da sessão
        session.pop('user_id', None)
        logger.info("Logout realizado com sucesso")
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Erro no logout: {str(e)}\n{error_traceback}")
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    try:
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                logger.info(f"Usuário autenticado: {user.username}")
                return jsonify({
                    'authenticated': True,
                    'user': user.to_dict()
                }), 200
        
        logger.info("Usuário não autenticado")
        return jsonify({'authenticated': False}), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Erro na verificação de autenticação: {str(e)}\n{error_traceback}")
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500
