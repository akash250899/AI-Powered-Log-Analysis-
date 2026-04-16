# Log Monitoring System

A FastAPI-based log analysis system that uses local AI models (via LM Studio) to analyze server logs.

## Project Structure

```
LogMonitoring/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── mock_logs/       # Sample log files
│       ├── error.log
│       ├── access.log
│       └── request.log
├── docker-compose.yml    # Docker orchestration
└── README.md          # This file
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- LM Studio (for local AI inference)

### Setup

1. **Start LM Studio**
   - Open LM Studio
   - Download and load `qwen2.5-coder-7b-instruct` model
   - Start server on port 1234

2. **Run the backend**

   ```bash
   docker-compose up --build
   ```

3. **Test the API**

   ```bash
   # Get servers
   curl http://localhost:8000/servers

   # Analyze logs
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{"server_id": "srv1", "port": 22, "log_type": "error"}'
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/servers` | GET | List available servers |
| `/analyze` | POST | Analyze logs using AI |

## Configuration

- **LM_STUDIO_URL**: AI endpoint (default: `http://localhost:1234/v1`)
- **MOCK_MODE**: Use mock log files (default: `True`)
- **MAX_LOG_LINES**: Max log lines to send to AI (default: 500)