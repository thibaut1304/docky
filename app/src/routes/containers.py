from src.config.docker import docker_clients
from src.config.logger import logger_api
from docker import DockerClient
from fastapi import APIRouter
from src.config.api_response import api_response

api = APIRouter(prefix="/containers")

def get_containers_info(client: DockerClient) -> list[dict]:
	""" Récupère les informations des conteneurs pour un client Docker donné """
	try:
		containers = client.containers.list(all=True)
		return [
			{
				"id": c.short_id,
				"name": c.name,
				"status": c.status,
				"image": c.image.tags[0] if c.image.tags else "N/A",
				"ports": c.ports
			}
			for c in containers
		]
	except Exception as e:
		return {"error": str(e)}

@api.get("")
@api.get("/", include_in_schema=False)
def list_containers():
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONATINERS",{
		host: get_containers_info(client)
		for host, client in docker_clients.items()
	})
