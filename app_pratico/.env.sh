#!/bin/bash
# Script para configuração automática

echo "FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
echo "DATABASE_URL=sqlite:///instance/praticante_app.db" >> .env
echo "# Configurações para produção no Render:" >> .env
echo "# RENDER_EXTERNAL_HOSTNAME=seu-app.onrender.com" >> .env
