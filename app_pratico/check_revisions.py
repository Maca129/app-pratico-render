import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.main import app
from src.models.topic import Topic, Revision
from src.models.user import db, User
import json
from datetime import datetime, timedelta

# Script para inspecionar revisões no banco de dados
print("Inspecionando revisões no banco de dados...")

# Usar o caminho do banco de dados atualizado
home_dir = os.path.expanduser("~")
db_file = os.path.join(home_dir, "praticante_app.db")
print(f"Usando banco de dados em: {db_file}")

# Verificar se o arquivo existe
if os.path.exists(db_file):
    print(f"Arquivo do banco de dados encontrado: {db_file}")
    print(f"Tamanho: {os.path.getsize(db_file)} bytes")
else:
    print(f"ERRO: Arquivo do banco de dados não encontrado: {db_file}")

# Configurar o caminho do banco de dados no app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
print(f"URI do banco de dados configurada: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Listar todos os usuários
    users = User.query.all()
    print(f"Total de usuários: {len(users)}")
    for user in users:
        print(f"Usuário ID: {user.id}, Nome: {user.username}, Email: {user.email}")

    # Listar todos os tópicos
    topics = Topic.query.all()
    print(f"\nTotal de tópicos: {len(topics)}")
    for topic in topics:
        print(f"Tópico ID: {topic.id}, Nome: {topic.name}, Usuário: {topic.user_id}, Grupo: {topic.group_name}")

    # Listar todas as revisões
    revisions = Revision.query.all()
    print(f"\nTotal de revisões: {len(revisions)}")
    for revision in revisions:
        print(f"Revisão ID: {revision.id}, Tópico: {revision.topic_id}, Data: {revision.scheduled_date}, Número: {revision.revision_number}, Concluída: {revision.is_completed}")

    # Verificar se há revisões para cada tópico
    print("\nRevisões por tópico:")
    for topic in topics:
        topic_revisions = Revision.query.filter_by(topic_id=topic.id).all()
        print(f"Tópico {topic.id} ({topic.name}): {len(topic_revisions)} revisões")
        
        # Mostrar detalhes das revisões deste tópico
        if topic_revisions:
            for rev in topic_revisions:
                print(f"  - Revisão {rev.id}: {rev.scheduled_date}, Número: {rev.revision_number}, Concluída: {rev.is_completed}, Notificar: {rev.notify}, Cor: {rev.color}")
        else:
            print("  - Nenhuma revisão encontrada")

    # Verificar revisões próximas (para hoje e futuras)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    upcoming_revisions = Revision.query.filter(
        Revision.scheduled_date >= today,
        Revision.is_completed == False
    ).order_by(Revision.scheduled_date).all()
    
    print(f"\nRevisões próximas (a partir de hoje): {len(upcoming_revisions)}")
    for rev in upcoming_revisions:
        topic = Topic.query.get(rev.topic_id)
        topic_name = topic.name if topic else "Tópico desconhecido"
        print(f"  - Revisão {rev.id}: {rev.scheduled_date}, Tópico: {topic_name}, Número: {rev.revision_number}")

print("\nInspeção concluída!")
