import docker
import json
from pathlib import Path
from src.config.logger import logger_api

DOCKER_HOSTS_FILE = Path(__file__).resolve().parent.parent.parent / "conf/docker_hosts.json"

docker_clients = {}

# def load_docker_clients():
# 	if not DOCKER_HOSTS_FILE.exists() or DOCKER_HOSTS_FILE.stat().st_size == 0:
# 		logger_api.warning("Fichier docker_hosts.json vide ou manquant.")
# 		with open(DOCKER_HOSTS_FILE, "w") as f:
# 			json.dump({}, f, indent=4)

# 	try:
# 		with open(DOCKER_HOSTS_FILE, "r") as f:
# 			hosts = json.load(f)
# 	except json.JSONDecodeError:
# 		logger_api.warning("Erreur de parsing du fichier json docker_hosts")
# 		hosts = {}
# 		with open(DOCKER_HOSTS_FILE, "w") as f:
# 			json.dump(hosts, f, indent=4)

# 	for name, info in hosts.items():
# 		try:
# 			if info["type"] == "local":
# 				client = docker.from_env()
# 			elif info["type"] == "ssh":
# 				user = info["user"]
# 				host = info["host"]
# 				client = docker.DockerClient(base_url=f"ssh://{user}@{host}")
# 			else:
# 				continue
# 			client.ping()	# Test de ping pour s'assurer que la connection ssh est ok sinon expect
# 			docker_clients[name] = client
# 			logger_api.info(f"[DOCKER] Connextion réussis avec {name}")
# 		except Exception as e:
# 			logger_api.error(f"[DOCKER] Ehec de la connection avec {name} : {e}")

try:
	with open(DOCKER_HOSTS_FILE, "r") as f:
		DOCKER_HOSTS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
	logger_api.warning("Fichier docker_hosts.json manquant ou invalide.")
	DOCKER_HOSTS = {}
	
def get_docker_client(host_name: str) -> docker.DockerClient:


	info = DOCKER_HOSTS.get(host_name)
	if not info:
		raise ValueError(f"Hôte Docker non trouvé : {host_name}")
	try:
		if info["type"] == "local":
			client = docker.from_env()
		elif info["type"] == "ssh":
			client = docker.DockerClient(base_url=f"ssh://{info['user']}@{info['host']}")
		else:
			raise ValueError(f"Type d'hôte invalide pour {host_name}")

		# Vérifie la connexion
		client.ping()
		return client
	except Exception as e:
		raise ConnectionError(f"Échec de la connexion avec {host_name} : {e}")

# load_docker_clients()
