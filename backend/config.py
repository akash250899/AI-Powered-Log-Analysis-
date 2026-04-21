import os

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
VALID_LOG_TYPES = {"error", "access", "request"}
MAX_LOG_LINES = 10000

SERVER_MAPPING = {
    "Local Author": "192.168.1.10",
    "Local Publisher": "192.168.1.11",
    "Dev Author": "192.168.1.12",
    "Dev Publisher": "192.168.1.13",
    "Stage Author": "192.168.1.14",
    "Stage Publisher": "192.168.1.15",
}

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://host.docker.internal:1234/v1")
SSH_USER = os.getenv("SSH_USER", "admin")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa")
