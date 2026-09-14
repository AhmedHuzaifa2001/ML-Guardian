import sys
from pathlib import Path

# Add backend directory to path so we can run this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from agents.llm_setup import llm
import logfire

class FairnessAudit(BaseModel):
    bias_risks: list[str] = Field(description="List of potential bias or fairness risks in this ML use case.")
    privacy_risks: list[str] = Field(description="List of data privacy risks (e.g., PII leakage, GDPR issues).")
    mitigation_strategies: list[str] = Field(description="Actionable steps the user must take to make the model safe and fair.")
    risk_level: str = Field(description="Overall risk level: LOW, MEDIUM, or HIGH.")

def audit_ml_plan(context: str, ml_recommendation: dict) -> dict:
    """
    Acts as an AI Ethics & Compliance Officer. Audits the ML plan for bias and privacy issues.
    """
    
    parser = JsonOutputParser(pydantic_object=FairnessAudit)
    
    system_prompt = """
    You are the Responsible AI Agent for ML-Guardian. You are an expert in AI Ethics, Data Privacy, and Algorithmic Fairness.
    Review the user's ML problem and the proposed ML models. Identify potential biases, privacy leaks (like PII), and suggest mitigations.
    Be strict but helpful.
    
    Format Instructions:
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "User's Problem: {context}\n\nProposed ML Approach: {ml_recommendation}")
    ])
    
    chain = prompt | llm | parser
    
    with logfire.span("Responsible AI Agent: Auditing ML Plan for '{context}'", context=context):
        logfire.info("Asking Groq to perform ethics and privacy audit...")
        audit_result = chain.invoke({
            "context": context,
            "ml_recommendation": ml_recommendation,
            "format_instructions": parser.get_format_instructions()
        })
        logfire.info("Audit complete. Risk Level: {risk}", risk=audit_result.get("risk_level"))
        
    return audit_result

if __name__ == "__main__":
    # Test the Responsible AI Agent directly
    test_context = "I want to predict if a job applicant should be hired based on their CV, age, gender, and past salary."
    test_ml = {"recommended_models": ["Random Forest", "Logistic Regression"]}
    
    print("Auditing Context:", test_context)
    result = audit_ml_plan(test_context, test_ml)
    print("\nAudit Result:", result)
