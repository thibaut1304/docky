#!/bin/bash

ENV_FILE=".env"
CERTS_DIR="certs"
CERT_NAME="docky"
CERT_PATH="./$CERTS_DIR"
DAYS_VALID=5

USER_ID=$(id -u)
GROUP_ID=$(id -g)

DOCKER_GID=$(getent group docker | cut -d: -f3)

ENV_FILE=".env"

update_env_var() {
    local key=$1
    local value=$2
    if grep -q "^$key=" "$ENV_FILE"; then
        sed -i "s|^$key=.*|$key=$value|" "$ENV_FILE"
    else
        echo "$key=$value" >> "$ENV_FILE"
    fi
}

if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

update_env_var "USER_ID" "$USER_ID"
update_env_var "GROUP_ID" "$GROUP_ID"
update_env_var "DOCKER_GID" "$DOCKER_GID"

if [ ! -d "$CERT_PATH" ]; then
    mkdir -p "$CERT_PATH" || { echo "❌ Erreur : Impossible de créer $CERT_PATH"; exit 1; }
fi

CERT_FILE="$CERT_PATH/$CERT_NAME.crt"
KEY_FILE="$CERT_PATH/$CERT_NAME.key"
REGEN_CERT=false

if [ -f "$CERT_FILE" ]; then
    echo "🔍 Vérification de l'expiration du certificat..."
    EXPIRATION_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    EXPIRATION_TIMESTAMP=$(date -d "$EXPIRATION_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)

    if [ "$CURRENT_TIMESTAMP" -ge "$EXPIRATION_TIMESTAMP" ]; then
        echo "⚠️ Le certificat est expiré ! Il sera régénéré."
        REGEN_CERT=true
    else
        echo "✅ Le certificat est toujours valide jusqu'à : $EXPIRATION_DATE"
    fi
else
    echo "❌ Certificat introuvable. Il sera généré."
    REGEN_CERT=true
fi

if [ "$REGEN_CERT" = true ]; then
    echo "🔐 Génération du certificat auto-signé pour $CERT_NAME..."

    openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:4096 \
        -keyout "$KEY_FILE" -out "$CERT_FILE" \
        -subj "/CN=localhost" || { echo "❌ Erreur : Échec de la génération du certificat SSL"; exit 1; }

    echo "✅ Certificat généré avec succès :"
    echo "   - Clé privée : $KEY_FILE"
    echo "   - Certificat : $CERT_FILE"
fi

update_env_var "SSL_CERT_PATH" "$CERT_PATH/$CERT_NAME.crt"
update_env_var "SSL_KEY_PATH" "$CERT_PATH/$CERT_NAME.key"

docker-compose down && docker-compose up --build -d
