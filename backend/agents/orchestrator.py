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

# Define the expected JSON output format using Pydantic
class OrchestratorDecision(BaseModel):
    intent: str = Field(
        description="The primary intent of the user. Must be one of: MODEL_RECOMMENDATION, ML_CONCEPT_EXPLANATION, RISK_ANALYSIS, GENERAL_CHAT"
    )
    needs_retrieval: bool = Field(
        description="True if the system needs to search the knowledge base for documentation or research to answer this."
    )
    needs_ml_analysis: bool = Field(
        description="True if the user is asking for ML algorithms, preprocessing, or dataset advice."
    )
    extracted_context: str = Field(
        description="A brief summary of what the user is trying to achieve."
    )

def route_query(user_query: str, **kwargs) -> dict:
    """
    Analyzes the user's query and decides which agents need to be activated.
    Accepts kwargs like 'chat_history' for context.
    Returns a structured JSON decision.
    """
    
    # Set up the parser to force the LLM to output valid JSON
    parser = JsonOutputParser(pydantic_object=OrchestratorDecision)
    
    system_prompt = """
    You are the Orchestrator Agent for ML-Guardian, a specialized AI for Machine Learning.
    Your job is to analyze the user's input and route it to the correct sub-agents.
    
    Categorize the intent into exactly one of these:
    - MODEL_RECOMMENDATION (User wants advice on what ML model/algorithm to use)
    - ML_CONCEPT_EXPLANATION (User is asking how an ML concept works)
    - RISK_ANALYSIS (User is asking about bias, fairness, or privacy in ML)
    - GENERAL_CHAT (Greetings, casual talk, unrelated to ML, or follow-up questions asking about previous chat history)
    
    Previous Conversation History (for context on follow-up questions):
    {chat_history}
    
    Format Instructions:
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    # Create the LangChain chain: Prompt -> Groq LLM -> JSON Parser
    chain = prompt | llm | parser
    
    import logfire
    from langchain_core.exceptions import OutputParserException
    
    # Run the chain inside a Logfire span to track it visually
    with logfire.span("Orchestrator Agent: Analyzing Intent for query '{query}'", query=user_query):
        try:
            # We get chat_history from kwargs, or empty string if not provided
            decision = chain.invoke({
                "query": user_query,
                "chat_history": kwargs.get("chat_history", ""),
                "format_instructions": parser.get_format_instructions()
            })
            logfire.info("Orchestrator routed successfully: {intent}", intent=decision.get("intent"))
        except OutputParserException:
            # LLM refused to process (e.g., violent/harmful content)
            # Return a safe default that routes to GENERAL_CHAT
            logfire.warn("LLM refused to classify intent — likely harmful content. Defaulting to GENERAL_CHAT.")
            decision = {
                "intent": "GENERAL_CHAT",
                "needs_retrieval": False,
                "needs_ml_analysis": False,
                "extracted_context": "The LLM flagged this query as potentially harmful."
            }
    
    return decision

# Quick test if you run this file directly
if __name__ == "__main__":
    test_query = "I have a dataset of customer transactions. I want to predict if they will churn. What should I use?"
    print("User:", test_query)
    print("Orchestrator Decision:", route_query(test_query))
