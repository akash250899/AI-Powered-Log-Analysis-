import os
import paramiko
from fastapi import HTTPException
from openai import OpenAI
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

import config

client = OpenAI(base_url=config.LM_STUDIO_URL, api_key="dummy-key")

def get_raw_logs(ip_address: str, port: int, log_type: str) -> str:
    """Retrieve logs either via local mock files or remote SSH."""
    if log_type not in config.VALID_LOG_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid log type. Valid types are: {', '.join(config.VALID_LOG_TYPES)}"
        )
    
    if config.MOCK_MODE:
        log_file_path = os.path.join("mock_logs", f"{log_type}.log")
        if not os.path.exists(log_file_path):
            raise HTTPException(status_code=404, detail=f"Mock log file not found for {log_type}")
        
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-config.MAX_LOG_LINES:])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading mock file: {str(e)}")
    else:
        # Connect directly using ip_address passed from frontend
        server_ip = ip_address
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            private_key = paramiko.RSAKey.from_private_key_file('/app/mock_aem_key')
            ssh.connect(
                hostname=server_ip, 
                port=port, 
                username='aemuser', 
                pkey=private_key, 
                timeout=10
            )
            command = f"tail -n 2000 /mnt/crx/author/crx-quickstart/logs/{log_type}.log"
            stdin, stdout, stderr = ssh.exec_command(command, timeout=15)
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                err_msg = stderr.read().decode('utf-8').strip()
                if "No such file" in err_msg:
                    raise HTTPException(status_code=404, detail=f"Log file not found on remote server: {err_msg}")
                raise HTTPException(status_code=502, detail=f"SSH execution failed: {err_msg}")
                
            return stdout.read().decode('utf-8')
            
        except paramiko.AuthenticationException:
            raise HTTPException(status_code=502, detail="SSH authentication failed (check configuration).")
        except paramiko.SSHException as e:
            raise HTTPException(status_code=502, detail=f"SSH connection error: {str(e)}")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=502, detail=f"Unexpected SSH error: {str(e)}")
        finally:
            ssh.close()

def compress_logs(raw_logs_str: str) -> str:
    """Cluster raw log lines using the Drain3 algorithm to save context tokens."""
    miner_config = TemplateMinerConfig()
    miner_config.load("")
    miner_config.profiling_enabled = False
    miner = TemplateMiner(config=miner_config)
    
    lines = raw_logs_str.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            miner.add_log_message(line)
        except Exception:
            continue

    errors_and_warns = []
    infos = []
    
    for cluster in miner.drain.clusters:
        template = cluster.get_template()
        record = f"[Count: {cluster.size}] {template}"
        
        if any(kw in template.upper() for kw in ["ERROR", "WARN", "EXCEPTION", "FAIL", "CRITICAL"]):
            errors_and_warns.append(record)
        else:
            infos.append(record)
            
    summary_lines = []
    summary_lines.append("--- CRITICAL/ERROR/WARN CLUSTERS ---")
    summary_lines.extend(errors_and_warns if errors_and_warns else ["None detected."])
    summary_lines.append("\n--- INFO CLUSTERS ---")
    summary_lines.extend(infos)
        
    return "\n".join(summary_lines)

def get_ai_analysis(compressed_logs: str) -> str:
    """Send clustered logs to the local LLM endpoint for analysis."""
    if len(compressed_logs) > 4000:
        compressed_logs = compressed_logs[:4000] + "\n...[TRUNCATED DUE TO CONTEXT LIMIT]"

    system_prompt = "Analyze these compressed log clusters and identify issues, root causes, and fixes."
    
    try:
        response = client.chat.completions.create(
            model="qwen2.5-coder-7b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": compressed_logs}
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
         raise HTTPException(
             status_code=502, 
             detail=f"Failed to connect to AI engine or process request: {str(e)}"
         )
