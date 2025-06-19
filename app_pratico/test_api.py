import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.main import app
from src.models.topic import Topic, Revision
from src.models.user import db, User
import json
from datetime import datetime, timedelta
import requests

# Script para testar a API de revisões
print("Testando API de revisões...")

# Usar o caminho do banco de dados atualizado
home_dir = os.path.expanduser("~")
db_file = os.path.join(home_dir, "praticante_app.db")
print(f"Usando banco de dados em: {db_file}")

# Configurar o caminho do banco de dados no app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
print(f"URI do banco de dados configurada: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Iniciar o servidor Flask em uma thread separada para testar a API
from threading import Thread
import time

def run_flask_app():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Iniciar o servidor Flask
print("Iniciando servidor Flask...")
flask_thread = Thread(target=run_flask_app)
flask_thread.daemon = True
flask_thread.start()

# Aguardar o servidor iniciar
print("Aguardando servidor iniciar...")
time.sleep(2)

# Testar a API de revisões
base_url = "http://localhost:5000"

# Testar login para obter sessão
print("\nTestando login...")
login_data = {
    "email": "test@example.com",
    "password": "testpassword"
}

try:
    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Status do login: {login_response.status_code}")
    print(f"Resposta do login: {login_response.text}")
    
    # Guardar cookies da sessão
    session_cookies = login_response.cookies
    
    # Testar API de revisões próximas
    print("\nTestando API de revisões próximas...")
    revisions_response = requests.get(f"{base_url}/api/topics/upcoming-revisions", cookies=session_cookies)
    print(f"Status da resposta: {revisions_response.status_code}")
    
    if revisions_response.status_code == 200:
        revisions_data = revisions_response.json()
        print(f"Total de revisões retornadas: {len(revisions_data.get('upcoming_revisions', []))}")
        print("Primeiras 3 revisões:")
        for i, rev in enumerate(revisions_data.get('upcoming_revisions', [])[:3]):
            print(f"  {i+1}. Tópico: {rev.get('topic_name')}, Data: {rev.get('scheduled_date')}, Número: {rev.get('revision_number')}")
    else:
        print(f"Erro na resposta: {revisions_response.text}")
    
    # Testar API de tópicos
    print("\nTestando API de tópicos...")
    topics_response = requests.get(f"{base_url}/api/topics/", cookies=session_cookies)
    print(f"Status da resposta: {topics_response.status_code}")
    
    if topics_response.status_code == 200:
        topics_data = topics_response.json()
        print(f"Total de tópicos retornados: {len(topics_data.get('topics', []))}")
        print("Tópicos:")
        for i, topic in enumerate(topics_data.get('topics', [])):
            print(f"  {i+1}. ID: {topic.get('id')}, Nome: {topic.get('name')}, Grupo: {topic.get('group_name')}")
    else:
        print(f"Erro na resposta: {topics_response.text}")
    
except Exception as e:
    print(f"Erro ao testar API: {str(e)}")

print("\nTeste da API concluído!")
