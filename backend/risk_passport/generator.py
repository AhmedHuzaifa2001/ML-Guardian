import sys
from pathlib import Path

# Add backend directory to path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from datetime import datetime

class MLRiskPassportGenerator:
    """
    Takes the raw output from the LangGraph workflow and formats it into the 
    official 'ML Risk Passport' structure required by the frontend UI.
    """
    
    @staticmethod
    def generate_passport(workflow_result: dict, user_name: str) -> dict:
        """
        Transforms the raw LangGraph state dictionary into a clean UI-ready format.
        """
        intent = workflow_result.get("intent", "UNKNOWN")
        
        # Base structure of the passport
        passport = {
            "passport_id": f"MRP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_for": user_name,
            "timestamp": datetime.now().isoformat(),
            "query_intent": intent,
            "status": "success",
            "content": {}
        }
        
        # 1. Handle Model Recommendation Path
        if intent == "MODEL_RECOMMENDATION" and "ml_recommendation" in workflow_result:
            ml_data = workflow_result["ml_recommendation"]
            passport["content"]["recommendations"] = {
                "models": ml_data.get("recommended_models", []),
                "reasoning": ml_data.get("reasoning", ""),
                "preprocessing": ml_data.get("preprocessing_steps", []),
                "challenges": ml_data.get("potential_challenges", "")
            }
            
            # Attach Risk Audit if it exists
            if "risk_audit" in workflow_result:
                audit_data = workflow_result["risk_audit"]
                passport["content"]["risk_assessment"] = {
                    "level": audit_data.get("risk_level", "UNKNOWN"),
                    "bias_risks": audit_data.get("bias_risks", []),
                    "privacy_risks": audit_data.get("privacy_risks", []),
                    "mitigations": audit_data.get("mitigation_strategies", [])
                }
                
        # 2. Handle Concept Explanation Path
        elif intent == "ML_CONCEPT_EXPLANATION" and "explanation" in workflow_result:
            exp_data = workflow_result["explanation"]
            passport["content"]["education"] = {
                "explanation": exp_data.get("explanation", ""),
                "sources": exp_data.get("sources_used", [])
            }
            
        # 3. Handle Direct Risk Analysis Path
        elif intent == "RISK_ANALYSIS" and "risk_audit" in workflow_result:
            audit_data = workflow_result["risk_audit"]
            passport["content"]["risk_assessment"] = {
                "level": audit_data.get("risk_level", "UNKNOWN"),
                "bias_risks": audit_data.get("bias_risks", []),
                "privacy_risks": audit_data.get("privacy_risks", []),
                "mitigations": audit_data.get("mitigation_strategies", [])
            }
            
        # 4. Handle General Chat or Fallback
        else:
            passport["content"]["general"] = {
                "response": workflow_result.get("response", "I could not process this request properly.")
            }
            
        return passport

# Singleton instance
passport_generator = MLRiskPassportGenerator()
