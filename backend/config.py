import os

MOCK_MODE = True
VALID_LOG_TYPES = {"error", "access", "request"}
MAX_LOG_LINES = 500

SERVER_MAPPING = {
    "local": "192.168.1.10",
    "dev": "192.168.1.11",
    "stage": "192.168.1.12"
}

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://host.docker.internal:1234/v1")
SSH_USER = os.getenv("SSH_USER", "admin")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa")
