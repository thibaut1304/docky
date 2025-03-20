import os
import re
from dotenv import load_dotenv
load_dotenv()


API_DOC = os.getenv("API_DOC", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

def get_api_version():
    api_version = os.getenv("API_VERSION", "1.0.0")

    if not api_version.startswith("v"):
        api_version = f"v{api_version}"

    match_major = re.match(r"v?(\d+)", api_version)
    api_major_version = f"v{match_major.group(1)}" if match_major else "v1"

    match_full = re.match(r"v?(\d+\.\d+\.\d+|\d+\.\d+|\d+)", api_version)
    api_full_version = match_full.group(1) if match_full else "1.0.0"

    return api_version, api_full_version, api_major_version

API_VERSION, API_FULL_VERSION, API_MAJOR_VERSION = get_api_version()
