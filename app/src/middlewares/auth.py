from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config.logger import logger_api
import os
from src.config.api_response import api_response

security = HTTPBearer()
EXPECTED_TOKEN = os.getenv("DOCKY_TOKEN")

def require_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
	if EXPECTED_TOKEN is None:
		logger_api.error("Jeton non fourni coté serveur")
		raise HTTPException(status_code=500, detail="🔐 Jeton d'authentification non défini côté serveur.")
	if credentials.credentials != EXPECTED_TOKEN:
		logger_api.error("Token invalide")
		return api_response("INVALID_TOKEN", raise_exception=True)
