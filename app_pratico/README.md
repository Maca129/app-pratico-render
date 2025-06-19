# Praticante App Render

Aplicativo de estudos para praticante de prático, pronto para deploy no Render.

## 🚀 Deploy no Render
1. Crie um Web Service no Render apontando para este repositório
2. Configure:
   - **Root Directory**: `praticante_app`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.main:app --bind 0.0.0.0:$PORT`
3. Adicione um disco persistente:
   - **Mount Path**: `/var/data`
4. Defina as variáveis de ambiente na seção "Environment" do Render:
   - `FLASK_SECRET_KEY` (obrigatória) - Chave secreta para a aplicação Flask
     - *Sugestão*: Gere uma chave com `openssl rand -hex 32`
   - `PORT` (opcional) - O Render define automaticamente, mas a variável deve existir
   - `DATABASE_DIR` (opcional) - Diretório do banco de dados (padrão: `/var/data`)

## ✅ Rodar localmente
1. Crie um arquivo `.env` na raiz do projeto com:
```bash
FLASK_SECRET_KEY=sua_chave_secreta_aqui
PORT=5000
# DATABASE_DIR=./data  # descomente para mudar o diretório
