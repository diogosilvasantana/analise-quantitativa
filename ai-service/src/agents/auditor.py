import os
import json
import logging
from typing import List, Dict, Any
import anthropic

# Configure Logging
logger = logging.getLogger("AuditorAgent")
logger.setLevel(logging.INFO)

class AuditorAgent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found. Auditor will not work.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def analyze_codebase(self, file_paths: List[str]):
        """
        Reads critical files and sends them to Claude for analysis in batches.
        Yields progress updates and final results.
        """
        if not self.client:
            yield {
                "status": "error",
                "message": "ANTHROPIC_API_KEY not set."
            }
            return

        BATCH_SIZE = 1
        all_issues = []
        total_files = len(file_paths)
        processed_count = 0

        # Helper to chunk list
        def chunked(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        import time

        for batch_paths in chunked(file_paths, BATCH_SIZE):
            # Yield progress
            for path in batch_paths:
                processed_count += 1
                yield {
                    "status": "progress",
                    "current": processed_count,
                    "total": total_files,
                    "file": path
                }
            
            logger.info(f"Analyzing batch: {batch_paths}")
            
            # 1. Read Files
            code_context = ""
            batch_file_map = {}
            
            for path in batch_paths:
                try:
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            code_context += f"\n--- FILE: {path} ---\n{content}\n"
                            batch_file_map[path] = content
                    else:
                        logger.warning(f"File not found: {path}")
                except Exception as e:
                    logger.error(f"Error reading {path}: {e}")

            if not code_context:
                continue

            # 2. Construct Prompt
            prompt = f"""
            You are a Senior Software Architect, Quant Trader, and UX Expert auditing a trading system.
            Your goal is to find issues in the following categories:
            1. LOGIC: Trading logic errors, inverted signals, math errors.
            2. SECURITY: Vulnerabilities, risky code, missing validations.
            3. UX: User Experience issues, confusing texts, bad flow.
            4. VISUAL: UI/Design improvements, color mismatches, responsiveness.
            5. OPTIMIZATION: Performance improvements, code cleanup.

            Analyze the following code:
            {code_context}

            RETURN ONLY A JSON ARRAY with the following structure for each issue found:
            [
              {{
                "id": "unique_short_id",
                "file_path": "path/to/file.py",
                "category": "LOGIC" | "SECURITY" | "UX" | "VISUAL" | "OPTIMIZATION",
                "severity": "CRITICAL" | "WARNING" | "INFO",
                "title": "Short Title of the Issue",
                "description": "Detailed explanation of why this is wrong.",
                "fixed_code": "The FULL content of the file with the fix applied."
              }}
            ]
            
            IMPORTANT: 
            1. Return ONLY valid JSON. No markdown formatting.
            2. DO NOT include 'original_code' in the JSON. I will read it from disk.
            3. In 'fixed_code', return the COMPLETE file content.
            4. Be creative with UX/Visual suggestions.
            """

            # 3. Call Claude
            try:
                time.sleep(2)
                
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8192,
                    temperature=0,
                    system="You are an expert code auditor. Output strict JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                response_text = message.content[0].text
                
                try:
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    start_idx = response_text.find('[')
                    end_idx = response_text.rfind(']')
                    
                    if start_idx != -1 and end_idx != -1:
                        response_text = response_text[start_idx:end_idx+1]
                    
                    batch_issues = json.loads(response_text.strip())
                    
                    for issue in batch_issues:
                        path = issue.get("file_path")
                        if path in batch_file_map:
                            issue["original_code"] = batch_file_map[path]
                        else:
                            issue["original_code"] = ""

                    all_issues.extend(batch_issues)

                except json.JSONDecodeError as e:
                    logger.error(f"JSON Parse Error in batch: {e}")
                    continue

            except Exception as e:
                logger.error(f"Error calling Claude for batch: {e}")
                continue
                
        # Final Yield
        yield {
            "status": "complete",
            "issues": all_issues
        }
