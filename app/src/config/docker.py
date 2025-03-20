import docker
import os
from dotenv import load_dotenv

load_dotenv()

SSH_HOTE= os.getenv("SSH_HOTE")
SSH_USER= os.getenv("SSH_USER")

client_distant = docker.DockerClient(base_url=f"ssh://{SSH_USER}@{SSH_HOTE}")
client_local = docker.from_env()