#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from main import app, db

if __name__ == '__main__':
    with app.app_context():
        # Buscar usuário
        user = User.query.filter_by(username='testuser').first()
        if user:
            print(f"Usuário encontrado: {user.username}")
            print(f"Email: {user.email}")
            print(f"Hash da senha: {user.password_hash}")
            
            # Testar verificação de senha
            is_valid = check_password_hash(user.password_hash, 'testpass')
            print(f"Senha 'testpass' é válida: {is_valid}")
            
            # Gerar novo hash para comparação
            new_hash = generate_password_hash('testpass')
            print(f"Novo hash gerado: {new_hash}")
            
            # Testar novo hash
            is_new_valid = check_password_hash(new_hash, 'testpass')
            print(f"Novo hash é válido: {is_new_valid}")
        else:
            print("Usuário não encontrado!")

