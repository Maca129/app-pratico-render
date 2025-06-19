import sys
import os
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime, timedelta

# Script para atualizar o schema do banco de dados e adicionar revisões de teste
print("Atualizando schema do banco de dados e adicionando revisões de teste...")

# Definir caminho do banco de dados no diretório da aplicação
app_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.environ.get("DATABASE_DIR", "/var/data")
db_file = os.path.join(DATABASE_DIR, "praticante_app.db")

print(f"Usando banco de dados em: {db_file}")

# Remover o arquivo do banco de dados se existir
if os.path.exists(db_file):
    print(f"Removendo banco de dados existente: {db_file}")
    os.remove(db_file)
    print("Banco de dados removido com sucesso.")

# Modificar a configuração do app para usar o novo caminho do banco de dados
from src.main import app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
print(f"URI do banco de dados configurada: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Importar modelos após configurar o URI do banco de dados
from src.models.user import db, User
from src.models.topic import Topic, Revision

with app.app_context():
    # Criar todas as tabelas do zero
    print("Criando todas as tabelas do banco de dados...")
    db.create_all()
    print("Tabelas criadas com sucesso!")
    
    # Garantir que o arquivo do banco de dados tenha permissões de escrita
    if os.path.exists(db_file):
        os.chmod(db_file, 0o666)
        print(f"Permissões de escrita aplicadas ao banco de dados: {db_file}")
    
    # Criar usuário de teste se não existir
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass')
        )
        db.session.add(test_user)
        db.session.commit()
    else:
        print("Usuário de teste já existe")
    user_id = test_user.id
    print(f"Usuário de teste criado com ID: {user_id}")
    
    # Criar tópico de teste
    print("Criando tópicos de teste...")
    test_topic = Topic(
        user_id=user_id,
        group_id=3,
        group_name="Meteorologia e Oceanografia",
        name="Meteorologia Marítima",
        description="Estudo dos fenômenos meteorológicos que afetam a navegação marítima",
        is_completed=False,
        confidence_level="Médio",
        created_at=datetime.utcnow()
    )
    db.session.add(test_topic)
    db.session.commit()
    topic_id = test_topic.id
    print(f"Tópico de teste criado com ID: {topic_id}")
    
    # Criar um segundo tópico de teste
    test_topic2 = Topic(
        user_id=user_id,
        group_id=3,
        group_name="Meteorologia e Oceanografia",
        name="Marés e Correntes Marítimas",
        description="Estudo dos fenômenos de marés e correntes marítimas e sua influência na navegação",
        is_completed=False,
        confidence_level="Médio",
        created_at=datetime.utcnow()
    )
    db.session.add(test_topic2)
    db.session.commit()
    topic_id2 = test_topic2.id
    print(f"Segundo tópico de teste criado com ID: {topic_id2}")
    
    # Criar revisões de teste para o primeiro tópico
    print("Criando revisões de teste para o primeiro tópico...")
    today = datetime.utcnow()
    
    # Revisão 1 - Hoje
    revision1 = Revision(
        topic_id=topic_id,
        scheduled_date=today,
        revision_number=1,
        is_completed=False,
        notes="Primeira revisão",
        notify=True,
        color="#4285f4"
    )
    
    # Revisão 2 - Em 7 dias
    revision2 = Revision(
        topic_id=topic_id,
        scheduled_date=today + timedelta(days=7),
        revision_number=2,
        is_completed=False,
        notes="Segunda revisão",
        notify=True,
        color="#4285f4"
    )
    
    # Revisão 3 - Em 15 dias
    revision3 = Revision(
        topic_id=topic_id,
        scheduled_date=today + timedelta(days=15),
        revision_number=3,
        is_completed=False,
        notes="Terceira revisão",
        notify=True,
        color="#4285f4"
    )
    
    # Criar revisões de teste para o segundo tópico
    print("Criando revisões de teste para o segundo tópico...")
    
    # Revisão 1 - Hoje
    revision4 = Revision(
        topic_id=topic_id2,
        scheduled_date=today,
        revision_number=1,
        is_completed=False,
        notes="Primeira revisão do segundo tópico",
        notify=True,
        color="#34a853"
    )
    
    # Revisão 2 - Em 5 dias
    revision5 = Revision(
        topic_id=topic_id2,
        scheduled_date=today + timedelta(days=5),
        revision_number=2,
        is_completed=False,
        notes="Segunda revisão do segundo tópico",
        notify=True,
        color="#34a853"
    )
    
    db.session.add_all([revision1, revision2, revision3, revision4, revision5])
    db.session.commit()
    print("Revisões de teste criadas com sucesso!")
    
    # Verificar se as revisões foram criadas
    revisions = Revision.query.all()
    print(f"\nTotal de revisões após atualização: {len(revisions)}")
    for revision in revisions:
        print(f"Revisão ID: {revision.id}, Tópico: {revision.topic_id}, Data: {revision.scheduled_date}, Concluída: {revision.is_completed}")

print("\nAtualização concluída!")
