from fastapi import APIRouter, HTTPException
import paho.mqtt.client as mqtt
from pydantic import BaseModel
from typing import Optional, Dict, List
import time, json, os, re
from datetime import timedelta

api = APIRouter(prefix="/infos")

"""
FastAPI application exposing Mosquitto and Zigbee2MQTT information
=================================================================

Endpoints
---------
- **GET /info/mosquitto/{broker_id}** – version, uptime, clients actifs.
- **GET /info/z2m/{broker_id}** – version, commit, réseau, coordinateur **et nombre d'appareils**.

Configuration
-------------
Les brokers sont déclarés dans le dictionnaire `BROKERS` (fin du fichier) ;
chaque entrée peut être surchargée via les variables d’environnement :

* `MQTT_<PORT>_HOST` (ex. `MQTT_1884_HOST`)
* `MQTT_<PORT>_USER`
* `MQTT_<PORT>_PASS`

L’API n’utilise **pas** WebSocket, uniquement TCP brut.
* `MQTT_<PORT>_HOST` (ex. `MQTT_1884_HOST`)
* `MQTT_<PORT>_USER`
* `MQTT_<PORT>_PASS`

L’API n’utilise **pas** WebSocket, uniquement TCP brut.
"""

class BrokerConfig(BaseModel):
	"""Paramètres de connexion à un broker MQTT."""

	host: str
	port: int
	username: Optional[str] = None
	password: Optional[str] = None

def _connect_client(cfg: BrokerConfig) -> mqtt.Client:
	client = mqtt.Client()
	if cfg.username:
		client.username_pw_set(cfg.username, cfg.password)
	client.connect(cfg.host, cfg.port, keepalive=30)
	return client

def collect_sys_stats(cfg: BrokerConfig, topics: List[str], timeout: float = 1.5) -> Dict[str, str]:
	"""Souscrit à une liste de topics `$SYS` et retourne le premier payload reçu."""

	data: Dict[str, str] = {}
	client = _connect_client(cfg)

	def _on_message(_, __, msg: mqtt.MQTTMessage):
		data[msg.topic] = msg.payload.decode()

	client.on_message = _on_message
	for t in topics:
		client.subscribe(t)

	client.loop_start()
	time.sleep(timeout)
	client.loop_stop()
	client.disconnect()
	return data


def get_z2m_info(cfg: BrokerConfig, timeout: float = 2.0) -> Dict:
	"""Récupère le JSON `zigbee2mqtt/bridge/info` (retained) + rafraîchissement instantané."""

	payload: Dict = {}
	client = _connect_client(cfg)

	def _on_message(_, __, msg: mqtt.MQTTMessage):
		nonlocal payload
		try:
			payload = json.loads(msg.payload.decode())
		except json.JSONDecodeError:
			pass

	client.on_message = _on_message
	client.subscribe("zigbee2mqtt/bridge/info")

	# Demande de rafraîchissement immédiat
	client.publish("zigbee2mqtt/bridge/request/info", "{}")

	client.loop_start()
	time.sleep(timeout)
	client.loop_stop()
	client.disconnect()
	return payload


def get_z2m_device_count(cfg: BrokerConfig, timeout: float = 2.0) -> int:
	"""Retourne le nombre d'appareils Zigbee connus de Zigbee2MQTT."""

	count: int = 0
	client = _connect_client(cfg)

	def _on_message(_, __, msg: mqtt.MQTTMessage):
		nonlocal count
		try:
			devices = json.loads(msg.payload.decode())
			if isinstance(devices, list):
				count = len(devices)
		except Exception:
			pass

	client.on_message = _on_message
	client.subscribe("zigbee2mqtt/bridge/devices")
	client.publish("zigbee2mqtt/bridge/request/devices", "{}")  # refresh

	client.loop_start()
	time.sleep(timeout)
	client.loop_stop()
	client.disconnect()
	return count

def cfg_or_404(broker_id: str) -> BrokerConfig:
	try:
		return BROKERS[broker_id]
	except KeyError:
		raise HTTPException(status_code=404, detail=f"Broker inconnu: {broker_id}") from None



routes_mosquitto = "/mosquitto/{broker_id}"
@api.get(f"{routes_mosquitto}")
@api.get(f"{routes_mosquitto}/", include_in_schema=False)
def mosquitto_info(broker_id: str):
	"""Retourne quelques métriques clés du broker Mosquitto."""

	cfg = cfg_or_404(broker_id)
	mapping = {
		"$SYS/broker/version": "version",
		"$SYS/broker/uptime": "uptime",
		"$SYS/broker/clients/active": "active_clients",
	}

	raw = collect_sys_stats(cfg, list(mapping.keys()))
	response =  {mapping[k]: v for k, v in raw.items()}

	""" On decremete de 1 active cliente pour la connection API"""
	if "active_clients" in response:
		try:
			active = max(int(response["active_clients"]) - 1, 0)
			response["active_clients"] = active
		except ValueError:
			pass  # on laisse tel quel si la conversion échoue
	if "uptime" in response:
		try:
			seconds = int(str(response["uptime"]).split()[0])
			days, rem  = divmod(seconds, 86400)
			hours, rem = divmod(rem, 3600)
			minutes, _ = divmod(rem, 60)
			if days == 0:
				response["uptime"] = f"{hours}h {minutes}m"
			else:
				response["uptime"] = f"{days}j {hours}h"
		except (ValueError, IndexError, KeyError):
			pass
	if "version" in response:
		try:
			match = re.search(r"(\d+\.\d+\.\d+)", str(response["version"]))
			if match:
				response["version"] = match.group(1)
		except KeyError:
			pass
	return response

routes_z2m = "/z2m/{broker_id}"
@api.get(f"{routes_z2m}")
@api.get(f"{routes_z2m}/", include_in_schema=False)
def zigbee2mqtt_info(broker_id: str):
	"""Renvoie la version et quelques infos générales sur Zigbee2MQTT."""

	cfg = cfg_or_404(broker_id)
	info = get_z2m_info(cfg)
	if not info:
		raise HTTPException(status_code=504, detail="Aucune donnée reçue de Zigbee2MQTT")

	wanted = ("version", "commit", "network", "coordinator")
	result =  {k: info.get(k) for k in wanted if k in info}
	result["device_count"] = get_z2m_device_count(cfg)
	return result


# -----------------------------------------------------------------------------
# Déclaration des brokers (modifiable via variables d'environnement)
# -----------------------------------------------------------------------------

BROKERS: Dict[str, BrokerConfig] = {
	# Mosquitto 1884 (avec auth)
	"1884": BrokerConfig(
		host=os.getenv("MQTT_1884_HOST", "localhost"),
		port=1884,
		username=os.getenv("MQTT_1884_USER"),
		password=os.getenv("MQTT_1884_PASS"),
	),
	# Mosquitto 1885 (sans auth + z2m)
	"1885": BrokerConfig(
		host=os.getenv("MQTT_1885_HOST", "localhost"),
		port=1885,
	),
}



