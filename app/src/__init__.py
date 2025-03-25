
from fastapi import FastAPI, Request, Depends

from src.middlewares.auth import require_token
from src.config.version import API_VERSION, API_FULL_VERSION, API_MAJOR_VERSION
from src.config.version import API_DOC, TEST_MODE
from src.routes.containers import api as route_containers
from src.routes.status import api as route_status
from src.config.limiter import limiter
from src.middlewares.handler import not_found, internal_server_error, ratelimit_error_handler
from slowapi.errors import RateLimitExceeded
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from slowapi.middleware import SlowAPIMiddleware

security = HTTPBearer()

def create_app() -> FastAPI:
	api_prefix = f"/api/docky/{API_MAJOR_VERSION}"
	app = FastAPI(
		title="Docky's API",
		openapi_url="/docky/openapi.json",
		version=API_FULL_VERSION,
		root_path=api_prefix,
		redoc_url=None,
		description="Api for get status docker and another...",
		docs_url="/doc" if API_DOC else None,
		redirect_slashes=True
	)
	# Schema de sécurité pour le token
	def custom_openapi():
		if app.openapi_schema:
			return app.openapi_schema
		openapi_schema = get_openapi(
			title=app.title,
			version=app.version,
			description=app.description,
			routes=app.routes,
		)
		openapi_schema["servers"] = [{"url": api_prefix}]
		openapi_schema["components"]["securitySchemes"] = {
			"HTTPBearer": {
				"type": "http",
				"scheme": "bearer"
			}
		}
		app.openapi_schema = openapi_schema
		return app.openapi_schema

	app.openapi = custom_openapi

	app.state.limiter = limiter
	app.add_middleware(SlowAPIMiddleware)

	app.add_exception_handler(RateLimitExceeded, ratelimit_error_handler) #429
	app.add_exception_handler(404, not_found)
	app.add_exception_handler(500, internal_server_error)

	app.include_router(route_status)
	app.include_router(route_containers, dependencies=[Depends(require_token)])
	return app


