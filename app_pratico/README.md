# Praticante App Render

Aplicativo de estudos para praticantes de prático, pronto para deploy no Render.

## 🚀 Deploy no Render
1. Crie um Web Service no Render apontando para este repositório
2. Adicione um banco de dados PostgreSQL no Render (opcional mas recomendado)
3. Configure:
   - **Pasta Raiz**: `praticante_app`
   - **Comando de Build**: `pip install -r requirements.txt`
   - **Comando de Inicialização**: `gunicorn src.app:application --bind 0.0.0.0:$PORT`
4. Defina as variáveis de ambiente na seção "Environment" do Render:
   - `FLASK_SECRET_KEY` (obrigatória) - Chave secreta para a aplicação Flask
     - *Sugestão*: Gere uma chave com `openssl rand -hex 32`
   - `DATABASE_URL` (se estiver usando PostgreSQL no Render - será criada automaticamente)
   - `PYTHON_VERSION` (recomendado) - `3.11.7`

## ✅ Executando localmente
1. Crie um arquivo `.env` na raiz do projeto com:
```bash
FLASK_SECRET_KEY=sua_chave_secreta_aqui
PORT=5000
# Para usar PostgreSQL localmente:
# DATABASE_URL=postgresql://usuario:senha@localhost/nome_do_banco
