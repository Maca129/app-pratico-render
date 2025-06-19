#!/usr/bin/env python3
import sys
import os
sys.path.append('src')

from werkzeug.security import check_password_hash
import sqlite3

# Conectar diretamente ao banco SQLite
conn = sqlite3.connect('praticante_app.db')
cursor = conn.cursor()

# Buscar usuário
cursor.execute("SELECT username, password_hash FROM users WHERE username='testuser'")
result = cursor.fetchone()

if result:
    username, password_hash = result
    print(f"Usuário encontrado: {username}")
    print(f"Hash da senha: {password_hash}")
    
    # Testar verificação de senha
    is_valid = check_password_hash(password_hash, 'testpass')
    print(f"Senha 'testpass' é válida: {is_valid}")
    
    # Testar com senha incorreta
    is_invalid = check_password_hash(password_hash, 'wrongpass')
    print(f"Senha 'wrongpass' é válida: {is_invalid}")
else:
    print("Usuário não encontrado!")

conn.close()

