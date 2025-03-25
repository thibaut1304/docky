from src.config.logger import logger_api
from src.config.api_response import api_response
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

def not_found(request: Request, exc):
	logger_api.error(f"Error 404 : {request.url}")
	return api_response("UNKNOWN_COMMAND", raise_exception=False)

def internal_server_error(request: Request, exc):
	logger_api.critical(f"Error 500 : {request.url}")
	return api_response("INTERNAL_SERVER_ERROR", raise_exception=False)


def ratelimit_error_handler(request: Request, exc: RateLimitExceeded):
	"""Bloque temporairement une IP qui dépasse la limite"""
	client_ip = get_remote_address(request)
	logger_api.warning(f"Too many request from : {client_ip}")

	api_response("TOO_MANY_REQUESTS", raise_exception=True)
