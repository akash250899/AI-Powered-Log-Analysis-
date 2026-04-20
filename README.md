# AI Log Analyzer

A FastAPI-based log analysis system that uses local AI models (via LM Studio) to analyze server error logs. The system compresses logs using the Drain3 algorithm before sending to the LLM to stay within context limits.

## Project Structure

```
LogMonitoring/
├── backend/
│   ├── main.py           # FastAPI application & endpoints
│   ├── engine.py        # Log retrieval, compression & AI analysis
│   ├── config.py       # Configuration settings
│   ├── requirements.txt
│   └── mock_logs/      # Sample log files for testing
│       ├── error.log
│       ├── access.log
│       └── request.log
├── static/             # Frontend UI
│   ├── index.html
│   ├── css/style.css
│   └── js/main.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- LM Studio (for local AI inference)
- SSH access to target servers (for production mode)

### Setup

1. **Start LM Studio**
   - Download `qwen2.5-coder-7b-instruct` or similar model
   - Set context length to 4096 or higher
   - Start server on port 1234 (default)

2. **Run the application**

   ```bash
   docker-compose up --build
   ```

3. **Access the UI**

   Open `http://localhost:8000` in your browser

4. **Test with Mock Mode**

   ```bash
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{"server_id": "Local Author", "ip_address": "192.168.1.10", "port": 22, "log_type": "error"}'
   ```

## Configuration

Edit `backend/config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| MOCK_MODE | Use mock logs instead of SSH | `True` |
| MAX_LOG_LINES | Log lines to fetch | `500` |
| LM_STUDIO_URL | AI endpoint | `http://host.docker.internal:1234/v1` |
| SSH_USER | SSH username | `admin` |
| SSH_KEY_PATH | Private key path | `~/.ssh/id_rsa` |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve UI |
| `/servers` | GET | List available servers |
| `/analyze` | POST | Analyze logs |

## Limitations

- **Context Window**: LLM context limit restricts log size - system uses Drain3 compression to reduce tokens
- **SSH Access**: Requires passwordless SSH key authentication to target servers
- **Local Only**: Uses local LM Studio; no cloud AI integration
- **Log Types**: Only supports `error`, `access`, `request` log types
- **No Persistence**: Analysis is not saved to database