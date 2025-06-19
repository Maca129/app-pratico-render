import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Script para testar a API de revisões usando a instância Flask já em execução
print("Testando API de revisões usando a instância existente...")

# Definir URL base para a instância já em execução
base_url = "https://5000-iq8pz5hfqdw2p3yd2craq-837f80fa.manusvm.computer"
print(f"URL base: {base_url}")

# Testar login para obter sessão
print("\nTestando login...")
login_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword"
}

try:
    # Testar primeiro o endpoint de registro para garantir que o usuário existe
    print("Tentando registrar usuário (caso não exista)...")
    register_response = requests.post(f"{base_url}/api/auth/register", json=login_data)
    print(f"Status do registro: {register_response.status_code}")
    print(f"Resposta do registro: {register_response.text}")
    
    # Agora tentar login
    print("\nTentando login...")
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
