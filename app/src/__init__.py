
from fastapi import FastAPI, Request

from src.config.version import API_VERSION, API_FULL_VERSION, API_MAJOR_VERSION
from src.config.version import API_DOC, TEST_MODE
from src.routes.containers import api as route_containers

def create_app() -> FastAPI:
    api_prefix = f"/api-docker/{API_MAJOR_VERSION}"
    app = FastAPI(
        title="Docky's API",
        version=API_FULL_VERSION,
        root_path=api_prefix,
        redoc_url=None,
        description="Api for get status docker and another...",
        docs_url="/doc" if API_DOC else None,
        redirect_slashes=True
    )
    app.include_router(route_containers)
    return app


