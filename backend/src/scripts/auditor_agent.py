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

    def analyze_codebase(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Reads critical files and sends them to Claude for analysis.
        """
        if not self.client:
            return [{
                "id": "error", 
                "title": "API Key Missing", 
                "description": "ANTHROPIC_API_KEY not set.", 
                "severity": "CRITICAL",
                "category": "SECURITY",
                "original_code": "",
                "fixed_code": ""
            }]



        # 1. Read Files
        code_context = ""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        code_context += f"\n--- FILE: {path} ---\n{content}\n"
                else:
                    logger.warning(f"File not found: {path}")
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")

        if not code_context:
            return []

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
            "original_code": "The FULL content of the file as it is now.",
            "fixed_code": "The FULL content of the file with the fix applied."
          }}
        ]
        
        IMPORTANT: 
        1. Return ONLY valid JSON. No markdown formatting.
        2. In 'fixed_code', return the COMPLETE file content.
        3. Be creative with UX/Visual suggestions if you see room for improvement (e.g., "Make this text larger", "Add a loading spinner").
        """

        # 3. Call Claude
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0,
                system="You are an expert code auditor. Output strict JSON.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 4. Parse Response
            response_text = message.content[0].text
            # Clean up potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                
            issues = json.loads(response_text.strip())
            return issues

        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return [{
                "id": "api_error", 
                "title": "Analysis Failed", 
                "description": str(e), 
                "severity": "CRITICAL",
                "category": "SECURITY",
                "original_code": "",
                "fixed_code": ""
            }]
