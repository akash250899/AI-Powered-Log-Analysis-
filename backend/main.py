from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
import engine

app = FastAPI(title="Log Analysis POC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        {"id": k, "name": f"{k.upper()} Server", "ip": v} 
        for k, v in config.SERVER_MAPPING.items()
    ]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_logs(request: AnalyzeRequest):
    # 1. Fetch
    raw_logs = engine.get_raw_logs(request.server_id, request.port, request.log_type)
    
    if not raw_logs.strip():
        raise HTTPException(status_code=404, detail="No log entries found for the requested type.")

    # 2. Compress
    compressed_logs = engine.compress_logs(raw_logs)

    # 3. Analyze
    analysis_result = engine.get_ai_analysis(compressed_logs)

    # Return
    return {"analysis": analysis_result, "raw_logs": compressed_logs}
