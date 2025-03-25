from src.config.docker import docker_clients
from src.config.logger import logger_api
from docker import DockerClient
from fastapi import APIRouter, Query
from src.config.api_response import api_response

api = APIRouter(prefix="/containers")

from datetime import datetime, timezone
import humanize

def get_containers_spec_info(client: DockerClient, hide: list[str] = [], container_name: str = None) -> list[dict]:
	try:
		containers = client.containers.list(all=True)
		result = []

		for c in containers:
			if container_name and c.name != container_name:
				continue

			try:
				stats = c.stats(stream=False)

				# Calcul CPU
				cpu_delta = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0) - \
				            stats.get("precpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)

				system_delta = stats.get("cpu_stats", {}).get("system_cpu_usage", 0) - \
				               stats.get("precpu_stats", {}).get("system_cpu_usage", 0)

				percpu_len = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) if "cpu_stats" in stats and "cpu_usage" in stats["cpu_stats"] else 0

				cpu_percent = 0.0
				if system_delta > 0 and cpu_delta > 0 and percpu_len > 0:
					cpu_percent = (cpu_delta / system_delta) * 100 * percpu_len

				# Mémoire
				mem_usage = stats.get("memory_stats", {}).get("usage", 0)
				mem_limit = stats.get("memory_stats", {}).get("limit", 1)  # éviter division par 0
				mem_percent = (mem_usage / mem_limit) * 100

			except Exception as e:
				cpu_percent = 0.0
				mem_usage = 0
				mem_limit = 1
				mem_percent = 0.0

			# Uptime
			try:
				started = c.attrs["State"]["StartedAt"].rstrip("Z")
				if "." in started:
					base, micro = started.split(".")
					micro = micro[:6]
					started = f"{base}.{micro}"
				started_dt = datetime.strptime(started, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
				uptime = humanize.naturaldelta(datetime.now(timezone.utc) - started_dt)
			except Exception:
				uptime = "N/A"

			containers_info = {
				"status": c.status,
				"uptime": uptime,
				"cpu_percent": round(cpu_percent, 2),
				"memory": {
					"limit_mb": round(mem_limit / 1024 / 1024, 2),
					"percent": round(mem_percent, 2)
				},
				"restarts": c.attrs.get("RestartCount", 0),
			}

			for field in hide:
				containers_info.pop(field, None)

			result.append(containers_info)

		return result

	except Exception as e:
		return {"error": str(e)}


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
	return api_response("LIST_CONTAINERS",{
		host: get_containers_info(client)
		for host, client in docker_clients.items()
	})

@api.get("/name")
@api.get("/name/", include_in_schema=False)
def list_containers_names_only():
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONTAINERS",{
		host: get_containers_info(client, ["id", "status", "image", "ports"])
		for host, client in docker_clients.items()
	})

@api.get("/{container}")
@api.get("/{container}/", include_in_schema=False)
def get_container_by_name(container: str):
	""" Récupère les conteneurs du local et du serveur distant """
	return api_response("LIST_CONTAINERS",{
		host: get_containers_info(client, container_name=container)
		for host, client in docker_clients.items()
	})

@api.get("/metrics/{container}")
@api.get("/metrics/{conatiner}/", include_in_schema=False)
def get_container_metrics(container: str, hide: list[str] = Query(default=[])):
	""" Retorune les metrics d'un container specifique"""
	return api_response("LIST_CONTAINERS", {
		host: get_containers_spec_info(client, hide=hide, container_name=container)
		for host, client in docker_clients.items()
	})
