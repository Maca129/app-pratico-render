
# Praticante App Render

Aplicativo de estudos para praticante de prático, pronto para deploy no Render.

## 🚀 Deploy no Render
1. Crie um Web Service no Render apontando para este repositório.
2. Configure:
   - Root Directory: `praticante_app`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.main:app`
3. Adicione um disco persistente:
   - Mount Path: `/var/data`
4. Defina a variável de ambiente opcional `FLASK_SECRET_KEY`.

## ✅ Rodar localmente
```bash
pip install -r requirements.txt
python src/main.py
```
