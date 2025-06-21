# Praticante App Render

Aplicativo de estudos para praticantes de prático, pronto para deploy no Render.

## 🚀 Deploy no Render
1. Crie um Web Service no Render apontando para este repositório
2. Configure:
   - **Pasta Raiz**: `praticante_app`
   - **Comando de Build**: `pip install -r requirements.txt`
   - **Comando de Inicialização**: `gunicorn src.app:create_app --bind 0.0.0.0:$PORT`
3. Defina as variáveis de ambiente na seção "Environment" do Render:
   - `FLASK_SECRET_KEY` (obrigatória) - Chave secreta para a aplicação Flask
     - *Sugestão*: Gere uma chave com `openssl rand -hex 32`
   - `PYTHON_VERSION` (recomendado) - `3.11.7`
   - `DATABASE_DIR` (opcional) - Pasta do banco de dados:
     - `./instance` (padrão recomendado, persiste entre reinicializações)
     - `/tmp/data` (apenas para testes, dados temporários)
     - `/var/data` (requer disco persistente configurado)

## ✅ Executando localmente
1. Crie um arquivo `.env` na raiz do projeto com:
```bash
FLASK_SECRET_KEY=sua_chave_secreta_aqui
PORT=5000
# DATABASE_DIR=./instance  # recomendado para desenvolvimento
