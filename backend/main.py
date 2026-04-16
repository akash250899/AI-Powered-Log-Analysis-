import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

MOCK_MODE = True
VALID_LOG_TYPES = {"error", "access", "request"}
MAX_LOG_LINES = 500  # Limit lines to stay within token limits

app = FastAPI(title="Log Analysis POC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Client configuration
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
# Most local endpoints like LM Studio just need a dummy key
client = OpenAI(base_url=LM_STUDIO_URL, api_key="dummy-key")

class Server(BaseModel):
    id: str
    name: str
    ip: str

class AnalyzeRequest(BaseModel):
    server_id: str
    port: int
    log_type: str

class AnalyzeResponse(BaseModel):
    analysis: str
    raw_logs: str

@app.get("/")
async def root():
    return {"message": "Log Analysis API is running", "docs": "/docs"}

@app.get("/servers", response_model=List[Server])
async def get_servers():
    return [
        {"id": "srv1", "name": "Frontend Web Server", "ip": "192.168.1.10"},
        {"id": "srv2", "name": "Backend API Server", "ip": "192.168.1.11"},
        {"id": "srv3", "name": "Database Server", "ip": "192.168.1.12"},
    ]

def get_logs(server_id: str, port: int, log_type: str) -> str:
    if log_type not in VALID_LOG_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid log type. Valid types are: {', '.join(VALID_LOG_TYPES)}"
        )
    
    if MOCK_MODE:
        log_file_path = os.path.join("mock_logs", f"{log_type}.log")
        if not os.path.exists(log_file_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Mock log file not found for {log_type}"
            )
        
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-MAX_LOG_LINES:])
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error reading mock file: {str(e)}"
            )
    else:
        # TODO: Production Logic - Paramiko SSH Connection
        # Implement SSH logic here to connect to the target server based on server_id.
        # Example setup for later:
        # import paramiko
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(hostname=server_ip, port=port, username='user', key_filename='path/to/key')
        # stdin, stdout, stderr = ssh.exec_command(f'tail -n {MAX_LOG_LINES} /var/log/{log_type}.log')
        # return stdout.read().decode('utf-8')
        pass
        
    return ""

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_logs(request: AnalyzeRequest):
    # Retrieve logs
    raw_logs = get_logs(request.server_id, request.port, request.log_type)
    
    if not raw_logs.strip():
        raise HTTPException(status_code=404, detail="No log entries found for the requested type.")

    # Call AI
    system_prompt = "Analyze these logs and identify issues, root causes, and fixes."
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_logs}
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        analysis_result = response.choices[0].message.content
    except Exception as e:
         raise HTTPException(
             status_code=502, 
             detail=f"Failed to connect to AI engine or process request: {str(e)}"
         )

    return {"analysis": analysis_result, "raw_logs": raw_logs}
