#!/bin/bash

# Script de deploy para AWS EC2

echo "Instalando dependências..."
sudo apt-get update
sudo apt-get install -y python3.12 python3-pip postgresql-client nginx

echo "Instalando dependências Python..."
pip3 install -r requirements.txt

echo "Configurando variáveis de ambiente..."
export DATABASE_URL="${DATABASE_URL}"
export SECRET_KEY="${SECRET_KEY}"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"

echo "Iniciando aplicação..."
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --daemon

echo "Deploy concluído!"
