import os
import shutil
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
# from src.scripts.auditor_agent import AuditorAgent

router = APIRouter(prefix="/audit", tags=["Audit"])
# agent = AuditorAgent()

# Configuration
BACKUP_DIR = os.path.join(os.getcwd(), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# Target Directories to Audit
TARGET_DIRS = [
    "scripts/bridge_core",
    "backend/src",
    "frontend-v2/src/app",
    "frontend-v2/src/components"
]

class FixRequest(BaseModel):
    file_path: str
    fixed_code: str

class RollbackRequest(BaseModel):
    file_path: str
    backup_id: str

import httpx
import json

@router.get("/run")
async def run_audit():
    """
    Triggers the AI Auditor (running in ai-service) to analyze critical files.
    """
    async def proxy_generator():
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream("POST", "http://ai-service:8001/audit/run", json={"file_paths": []}) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield json.dumps({"status": "error", "message": f"AI Service Error: {error_text.decode()}"}).encode()
                        return

                    async for chunk in response.aiter_bytes():
                        yield chunk
        except Exception as e:
            yield json.dumps({"status": "error", "message": f"Failed to connect to AI Service: {str(e)}"}).encode()

    from fastapi.responses import StreamingResponse
    return StreamingResponse(proxy_generator(), media_type="application/x-ndjson")

@router.post("/fix")
async def apply_fix(request: FixRequest):
    """
    Applies a fix to a file, creating a backup first.
    """
    file_path = os.path.abspath(request.file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        # 1. Create Backup
        timestamp = int(time.time())
        filename = os.path.basename(file_path)
        backup_id = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_id)
        
        shutil.copy2(file_path, backup_path)
        
        # 2. Apply Fix
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.fixed_code)
            
        return {
            "status": "success", 
            "message": "Fix applied successfully", 
            "backup_id": backup_id,
            "backup_path": backup_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply fix: {str(e)}")

@router.post("/rollback")
async def rollback_fix(request: RollbackRequest):
    """
    Restores a file from a backup.
    """
    file_path = os.path.abspath(request.file_path)
    backup_path = os.path.join(BACKUP_DIR, request.backup_id)
    
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=404, detail="Backup file not found")
        
    try:
        # Restore
        shutil.copy2(backup_path, file_path)
        
        return {"status": "success", "message": "Rollback successful"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rollback: {str(e)}")
