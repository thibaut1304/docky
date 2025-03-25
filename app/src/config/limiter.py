# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],
)
