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

import requests

# ...

@router.get("/run")
async def run_audit():
    """
    Triggers the AI Auditor (running in ai-service) to analyze critical files.
    """
    project_root = os.getcwd() # In backend container, this is /app (which is backend/src?? No, check Dockerfile)
    # Backend Dockerfile: WORKDIR /app. Volumes: ./backend/src:/app/src.
    # So os.getcwd() is /app.
    # But we want paths relative to the REAL project root (e:\projetos\ai-trader-pro).
    # The backend container sees:
    # /app/src/...
    # /app/scripts/... (mounted)
    
    # We need to construct paths that ai-service can understand.
    # ai-service has /app/project_root mounted to ./.
    
    # Let's list the files we want to audit, relative to the REPO ROOT.
    # We know the structure:
    # scripts/bridge_core/...
    # backend/src/...
    # frontend-v2/src/...
    
    files_to_audit = []
    
    # 1. Scripts (Mounted at /app/scripts in Backend)
    if os.path.exists("/app/scripts"):
        for root, _, files in os.walk("/app/scripts"):
            for file in files:
                if file.endswith(".py"):
                    # /app/scripts/bridge_core/flow.py -> scripts/bridge_core/flow.py
                    rel_path = os.path.relpath(os.path.join(root, file), "/app")
                    files_to_audit.append(rel_path)

    # 2. Backend Src (Mounted at /app/src)
    if os.path.exists("/app/src"):
        for root, _, files in os.walk("/app/src"):
            for file in files:
                if file.endswith(".py"):
                    # /app/src/main.py -> backend/src/main.py (Wait, /app/src maps to backend/src)
                    # So rel_path from /app is src/main.py. We need to prepend backend/
                    rel = os.path.relpath(os.path.join(root, file), "/app/src")
                    files_to_audit.append(f"backend/src/{rel}")

    # 3. Frontend (Not mounted in Backend! We can't walk it from here if we don't mount it)
    # We need to mount frontend-v2 to backend if we want backend to discover files?
    # OR, we just tell ai-service "Audit these directories" and let IT discover them.
    # YES. That's much better.
    
    # Let's change the API. Instead of sending file list, we send "scan_request".
    # But the user might want specific files.
    # For now, let's just ask ai-service to scan the default directories.
    
    try:
        # Stream the response from ai-service
        req = requests.post(
            "http://ai-service:8001/audit/run", 
            json={"file_paths": []}, # Empty list = scan defaults
            stream=True
        )
        
        if req.status_code != 200:
             return {"status": "error", "message": f"AI Service Error: {req.text}"}

        # Generator to yield chunks
        def proxy_generator():
            for chunk in req.iter_content(chunk_size=None):
                yield chunk

        from fastapi.responses import StreamingResponse
        return StreamingResponse(proxy_generator(), media_type="application/x-ndjson")

    except Exception as e:
        return {"status": "error", "message": f"Failed to connect to AI Service: {str(e)}"}

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
