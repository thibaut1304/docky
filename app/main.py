from src.config.env import load_environment
load_environment()

from src import create_app
app = create_app()

if __name__ == "__main__":
    print("Le main a ete appele")
