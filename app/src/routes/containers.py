from src.config.docker import docker_clients
from src.config.logger import logger_api
from docker import DockerClient
from fastapi import APIRouter
from src.config.api_response import api_response

api = APIRouter(prefix="/containers")

def get_containers_info(client: DockerClient, hide: list[str] = [], container_name: str = None) -> list[dict]:
	""" Récupère les informations des conteneurs pour un client Docker donné """
	try:
		containers = client.containers.list(all=True)
		result = []
		for c in containers:
			if container_name and c.name != container_name:
				continue
			if c.status != "running":
				continue
			containers_info = {
				"id": c.short_id,
				"name": c.name,
				"status": c.status,
				"image": c.image.tags[0] if c.image.tags else "N/A",
				"ports": c.ports
			}

			for field in hide:
				containers_info.pop(field, None)
			result.append(containers_info)
		return result
	except Exception as e:
		return {"error": str(e)}

@api.get("")
@api.get("/", include_in_schema=False)
def list_all_containers():
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONATINERS",{
		host: get_containers_info(client)
		for host, client in docker_clients.items()
	})

@api.get("/name")
@api.get("/name/", include_in_schema=False)
def list_containers_names_only():
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONATINERS",{
		host: get_containers_info(client, ["id", "status", "image", "ports"])
		for host, client in docker_clients.items()
	})

@api.get("/{container}")
@api.get("/{container}/", include_in_schema=False)
def get_container_by_name(container: str):
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONATINERS",{
		host: get_containers_info(client, container_name=container)
		for host, client in docker_clients.items()
	})
