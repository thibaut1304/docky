#!/bin/bash

export PYTHONPATH=/src
export PATH="$HOME/.local/bin:$PATH"


echo "✅ Lancement avec l'utilisateur : $(whoami) (UID: $(id -u), GID: $(id -g))"
echo "✅ PYTHONPATH: $PYTHONPATH"
echo "✅ PWD: $PWD"
echo "✅ SSH_USER: ${SSH_USER}"
echo "✅ SSH_HOTE: ${SSH_HOTE}"

if [ -f "/tmp/ssh/id_rsa" ]; then
    mkdir -p ~/.ssh
    cp /tmp/ssh/id_rsa ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
    ssh -o StrictHostKeyChecking=no "${SSH_USER}@${SSH_HOTE}" "echo 'Connexion SSH OK'"
fi

if [ "$(echo "$API_DOC" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
    echo "📘 Mode Swagger activé, lancement de Flask directement..."
    python main.py
    exec uvicorn main:app --host 0.0.0.0 --port 5002 \
        --ssl-keyfile  $SSL_KEY_PATH \
        --ssl-certfile $SSL_CERT_PATH \
        --reload
else
    echo "🚀 Mode production activé, lancement avec Uvicorn (optimisé pour FastAPI)..."
    exec uvicorn main:app --host 0.0.0.0 --port 5002 \
        --ssl-keyfile  $SSL_KEY_PATH \
        --ssl-certfile $SSL_KEY_PATH \
        --workers 2
fi