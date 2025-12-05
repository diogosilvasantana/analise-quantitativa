import os
import shutil
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.scripts.auditor_agent import AuditorAgent

router = APIRouter(prefix="/audit", tags=["Audit"])
agent = AuditorAgent()

# Configuration
BACKUP_DIR = os.path.join(os.getcwd(), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# Target Files to Audit (Hardcoded for safety/simplicity)
TARGET_FILES = [
    "scripts/bridge_core/flow_monitor.py",
    "scripts/bridge_core/investing_client.py",
    "frontend-v2/src/app/page.tsx",
    "frontend-v2/src/components/dashboard/IndicesPanel.tsx",
    "frontend-v2/src/components/dashboard/QuantPanel.tsx",
    "frontend-v2/src/app/globals.css",
]

class FixRequest(BaseModel):
    file_path: str
    fixed_code: str

class RollbackRequest(BaseModel):
    file_path: str
    backup_id: str

@router.get("/run")
async def run_audit():
    """
    Triggers the AI Auditor to analyze critical files.
    """
    # Resolve absolute paths
    abs_paths = [os.path.abspath(f) for f in TARGET_FILES if os.path.exists(os.path.abspath(f))]
    
    if not abs_paths:
        return {"status": "error", "message": "No target files found."}
        
    issues = agent.analyze_codebase(abs_paths)
    return issues

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
