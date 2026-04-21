# AI Log Analyzer

A FastAPI-based log analysis system that uses local AI models (via LM Studio) to analyze AEM server error logs. The system compresses logs using the Drain3 algorithm before sending to the LLM to stay within context limits.

## Project Structure

```
LogMonitoring/
├── backend/
│   ├── main.py           # FastAPI application & endpoints
│   ├── engine.py        # Log retrieval, compression & AI analysis
│   ├── config.py        # Configuration settings
│   ├── requirements.txt
│   └── mock_logs/       # Sample log files for testing
│       ├── error.log
│       ├── access.log
│       └── request.log
├── static/              # Frontend UI
│   ├── index.html
│   ├── css/style.css
│   └── js/main.js
├── Dockerfile           # Backend container
├── Dockerfile.mock      # Mock AEM SSH server
├── docker-compose.yml   # Docker orchestration
├── mock_aem_key        # SSH private key for mock server
├── mock_aem_key.pub    # SSH public key for mock server
└── README.md
```

## Features

- **AI-Powered Analysis**: Uses local LLM (via LM Studio) to analyze logs
- **Log Compression**: Drain3 algorithm clusters similar log entries to reduce token usage
- **Dual Mode**: 
  - MOCK_MODE=true: Test with local log files
  - MOCK_MODE=false: Connect to real servers via SSH
- **Multiple Log Types**: Supports error, access, and request logs
- **Multiple Servers**: Pre-configured for 6 AEM environments (Local, Dev, Stage - Author & Publisher)
- **Dockerized**: Easy to set up and run with Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- LM Studio (for local AI inference)
- SSH access to target servers (for production mode)

### Setup

1. **Start LM Studio**
   - Download a model (e.g., `qwen2.5-coder-7b-instruct`)
   - Set context length to 4096 or higher
   - Start server on port 1234 (default)

2. **Run the application**

   ```bash
   docker compose up -d --build
   ```

3. **Access the UI**

   Open `http://localhost:8000` in your browser

### Testing

**Mock Mode (local files):**
```bash
# Set MOCK_MODE=true in docker-compose.yml, then:
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"server_id": "Local Author", "ip_address": "192.168.1.10", "port": 22, "log_type": "error"}'
```

**SSH Mode (real servers):**
```bash
# Set MOCK_MODE=false in docker-compose.yml, then:
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"server_id": "Local Author", "ip_address": "host.docker.internal", "port": 2222, "log_type": "error"}'
```

## Configuration

### Environment Variables (docker-compose.yml)

| Variable | Description | Default |
|----------|-------------|---------|
| MOCK_MODE | Use mock logs instead of SSH | `false` |
| LM_STUDIO_URL | AI endpoint URL | `http://host.docker.internal:1234/v1` |

### Application Settings (backend/config.py)

| Setting | Description | Default |
|---------|-------------|---------|
| MOCK_MODE | Use mock logs instead of SSH | `True` |
| MAX_LOG_LINES | Maximum log lines to process | `10000` |
| VALID_LOG_TYPES | Supported log types | `error`, `access`, `request` |
| SERVER_MAPPING | Server IP mappings | 6 pre-configured servers |
| SSH_USER | SSH username | `admin` |
| SSH_KEY_PATH | Private key path | `~/.ssh/id_rsa` |

### Server Mappings

| Server | IP Address |
|--------|------------|
| Local Author | 192.168.1.10 |
| Local Publisher | 192.168.1.11 |
| Dev Author | 192.168.1.12 |
| Dev Publisher | 192.168.1.13 |
| Stage Author | 192.168.1.14 |
| Stage Publisher | 192.168.1.15 |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve UI |
| `/servers` | GET | List available servers |
| `/analyze` | POST | Analyze logs |

### Analyze Request Body

```json
{
  "server_id": "Local Author",
  "ip_address": "192.168.1.10",
  "port": 22,
  "log_type": "error"
}
```

### Analyze Response

```json
{
  "analysis": "AI-generated analysis of logs...",
  "raw_logs": "Compressed log clusters..."
}
```

## Advantages

- **Privacy-Focused**: All data stays local - logs are processed on your machine, not sent to external cloud services
- **Cost-Effective**: Uses free local AI models via LM Studio - no API costs
- **Fast Iteration**: Quick testing with MOCK_MODE using local log files
- **Scalable**: Drain3 compression allows processing large log files within LLM context limits
- **Easy Setup**: Docker Compose simplifies deployment
- **Realistic Testing**: Mock AEM server simulates real SSH-based log retrieval
- **Flexible**: Can connect to any server with SSH access

## Limitations

- **Context Window**: LLM context limit restricts log size - system uses Drain3 compression to reduce tokens, but very large logs may still exceed limits
- **Local Only**: Uses local LM Studio; no cloud AI integration (can be extended)
- **Log Types**: Only supports `error`, `access`, `request` log types
- **No Persistence**: Analysis is not saved to database - each request is independent
- **Single Log Path**: Currently only supports `/mnt/crx/author/crx-quickstart/logs/` path (AEM-specific)
- **Network**: Mock AEM server requires Docker networking for SSH access

## Troubleshooting

### SSH Connection Issues

If testing with MOCK_MODE=false fails:

1. Verify mock AEM server is running: `docker compose ps`
2. Check SSH port is accessible: `ssh -i mock_aem_key aemuser@localhost -p 2222`
3. Check logs: `docker compose logs mock_aem_server`

### LM Studio Issues

1. Ensure LM Studio is running on port 1234
2. Verify model is loaded and server is started
3. Check LM_STUDIO_URL in docker-compose.yml

### Volume Mount for Logs

Local log files are mounted into the mock AEM server at:
- Host: `backend/mock_logs/`
- Container: `/mnt/crx/author/crx-quickstart/logs/`

Edit local files in `backend/mock_logs/` for instant testing (no rebuild needed).
