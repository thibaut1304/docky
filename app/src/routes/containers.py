from src.config.docker import client_local, client_distant

from docker import DockerClient
from fastapi import APIRouter

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
    return {
        "hote_local": get_containers_info(client_local),
        "hote_distant": get_containers_info(client_distant)
    }