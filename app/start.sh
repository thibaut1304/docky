#!/bin/bash

export PYTHONPATH=/src
export PATH="$HOME/.local/bin:$PATH"

DOCKER_CONFIG_FILE="conf/docker_hosts.json"

if [ -f "/tmp/ssh/id_rsa" ]; then
	mkdir -p ~/.ssh
	cp /tmp/ssh/id_rsa ~/.ssh/id_rsa
	chmod 600 ~/.ssh/id_rsa
	eval "$(ssh-agent -s)"
	ssh-add ~/.ssh/id_rsa
	# ssh -o StrictHostKeyChecking=no "${SSH_USER}@${SSH_HOTE}" "echo 'Connexion SSH OK'" # -> Test dans docker.py !
fi

if [ -f "$DOCKER_CONFIG_FILE" ]; then
	echo "🔍 Préparation des connexions SSH aux hôtes distants..."

       #jq -c 'to_entries[]' "$DOCKER_CONFIG_FILE" | while read -r entry; do
       mapfile -t entries < <(jq -c 'to_entries[]' "$DOCKER_CONFIG_FILE")
       for entry in "${entries[@]}"; do
		name=$(echo "$entry" | jq -r '.key')
		host_type=$(echo "$entry" | jq -r '.value.type')
		host_ip=$(echo "$entry" | jq -r '.value.host')
		user=$(echo "$entry" | jq -r '.value.user')

		if [ "$host_type" = "ssh" ]; then
			echo "📡 Connexion test à $user@$host_ip..."
			if ssh -o StrictHostKeyChecking=no "$user@$host_ip" "echo '✅ SSH OK pour $host_ip'"; then
				echo "✅ Connexion SSH réussie pour $host_ip"
			else
				echo "❌ SSH échoué vers $host_ip"

				#  Supprimer cette entrée du fichier JSON =--> gerée dans docker.py
				# tmpfile=$(mktemp)
				# jq "del(.[$i])" "$DOCKER_CONFIG_FILE" > "$tmpfile" && mv "$tmpfile" "$DOCKER_CONFIG_FILE"
				# break
			fi
		fi
	done
else
	echo "❌ Fichier $DOCKER_CONFIG_FILE introuvable"
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
		--ssl-certfile $SSL_CERT_PATH \
		--workers 1
fi
