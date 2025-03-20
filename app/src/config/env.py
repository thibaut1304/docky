import os
from dotenv import load_dotenv

def load_environment():
    """Charge .env selon l'environnement"""
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    def is_running_in_docker():
        try:
            with open("/proc/1/cgroup", "rt") as f:
                return "docker" in f.read() or "containerd" in f.read()
        except FileNotFoundError:
            return False

    if not is_running_in_docker():
        dotenv_path = os.path.join(BASE_DIR, "..", "..", "..", ".env")
        load_dotenv(dotenv_path)
    else:
        load_dotenv()

load_environment()