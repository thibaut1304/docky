from fastapi import APIRouter, Request
from src.config.logger import logger_api
from src.config.version import API_FULL_VERSION
from src.config.api_response import api_response
from src.config.limiter import limiter

api = APIRouter(prefix="/status")

@api.get("")
@api.get("/", include_in_schema=False)
@limiter.limit("5/minute")
def get_status(request: Request):
	""" Retourne le status de l'API Docky"""

	return api_response("STATUS_OK", {"api_version": API_FULL_VERSION})
