import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from src.agents.auditor import AuditorAgent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIService")

app = FastAPI(title="AI Trader Pro - AI Service", version="1.0.0")

# Initialize Agents
auditor = AuditorAgent()

class AuditRequest(BaseModel):
    file_paths: List[str]

@app.get("/")
def health_check():
    return {"status": "running", "service": "ai-service"}

from fastapi.responses import StreamingResponse
import json

@app.post("/audit/run")
async def run_audit(request: AuditRequest):
    """
    Runs the Auditor Agent on the provided file paths.
    Returns a stream of progress events (NDJSON).
    """
    logger.info(f"Received audit request for {len(request.file_paths)} files.")
    
    paths_to_scan = []
    project_root = "/app/project_root"
    
    if not request.file_paths:
        # Default Scan: Find all relevant files in project root
        target_dirs = [
            "scripts/bridge_core",
            "backend/src",
            "frontend-v2/src/app",
            "frontend-v2/src/components"
        ]
        
        for rel_dir in target_dirs:
            abs_dir = os.path.join(project_root, rel_dir)
            if not os.path.exists(abs_dir):
                continue
                
            for root, _, files in os.walk(abs_dir):
                for file in files:
                    if file.endswith(('.py', '.tsx', '.ts', '.css')):
                        if "test" in file or "node_modules" in root:
                            continue
                        paths_to_scan.append(os.path.join(root, file))
    else:
        # Use provided paths, prepending project root if needed
        for p in request.file_paths:
            # Assume paths are relative to project root
            paths_to_scan.append(os.path.join(project_root, p))

    # Generator wrapper to serialize to NDJSON
    def event_generator():
        for event in auditor.analyze_codebase(paths_to_scan):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
