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

class MLRecommendation(BaseModel):
    recommended_models: list[str] = Field(description="List of 2-3 recommended ML models")
    reasoning: str = Field(description="Why these models are a good fit for the dataset")
    preprocessing_steps: list[str] = Field(description="Important preprocessing steps (e.g., scaling, encoding)")
    potential_challenges: str = Field(description="Any pitfalls the user should watch out for (e.g., overfitting, imbalanced classes)")

def analyze_ml_problem(context: str) -> dict:
    """
    Acts as an ML expert to recommend algorithms and preprocessing steps based on the user's context.
    """
    
    parser = JsonOutputParser(pydantic_object=MLRecommendation)
    
    system_prompt = """
    You are the ML Analysis Agent for ML-Guardian. You are an expert Data Scientist.
    Based on the user's description of their dataset or problem, recommend the best machine learning approach.
    
    Format Instructions:
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Here is the user's problem: {context}")
    ])
    
    chain = prompt | llm | parser
    
    with logfire.span("ML Analyst Agent: Generating Recommendations", context=context):
        logfire.info("Asking Groq to analyze ML problem...")
        recommendation = chain.invoke({
            "context": context,
            "format_instructions": parser.get_format_instructions()
        })
        logfire.info("Analysis complete. Recommended models: {models}", models=recommendation.get("recommended_models"))
        
    return recommendation

if __name__ == "__main__":
    # Test the ML Analyst directly
    test_context = "I have a dataset of customer transactions. I want to predict if they will churn. The data has missing values and mixed text/numbers."
    print("Analyzing:", test_context)
    result = analyze_ml_problem(test_context)
    print("\nResult:", result)
