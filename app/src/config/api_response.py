from src.config.responses_code import SUCCESS_MESSAGES, ERROR_MESSAGES
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def api_response(status_key, extra_data=None, raise_exception: bool = False):
	"""
	Génère une réponse API standardisée avec un type et un message.

	:param status_key: Clé du message à retourner (ex: "USER_CREATED", "INVALID_TOKEN").
	:param extra_data: Dictionnaire optionnel contenant des données supplémentaires à renvoyer.
	:param for_abort pour iverser le code de la reponse au return
	:return: Tuple (dict, HTTP code)
	"""
	response_dict = SUCCESS_MESSAGES.get(status_key, ERROR_MESSAGES.get(status_key))
	if not response_dict:
		response_dict = {"code": 500, "response": {"type": "Internal Error", "message": "An unexpected error occurred"}}

	code = response_dict["code"]
	response = response_dict["response"]

	if extra_data and isinstance(extra_data, dict):
		response.update(extra_data)
	if raise_exception:
		raise HTTPException(status_code=code, detail=response)
	return JSONResponse(status_code=code, content=response)
