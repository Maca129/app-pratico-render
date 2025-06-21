# Praticante App (Render)

## 🚀 Deploy
1. Conecte seu repositório no Render
2. Adicione um banco PostgreSQL (opcional)
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.app:application --bind 0.0.0.0:$PORT`
4. Variáveis de ambiente:
   - `FLASK_SECRET_KEY` (obrigatória)
   - `DATABASE_URL` (auto-configurada com PostgreSQL)

## 💻 Local Development
```bash
# Crie um .env com:
FLASK_SECRET_KEY=chave_temporaria
PORT=5000

# Instale dependências
pip install -r requirements.txt

# Execute
python src/app.py
