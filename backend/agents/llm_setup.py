from langchain_groq import ChatGroq
from config import settings
import logfire

# Initialize Logfire
logfire.configure()
logfire.instrument_openai()

def get_llm():
    """
    Initialize and return the Groq LLM instance.
    This will be shared across all agents in the system.
    """
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    return llm

# Global LLM instance to be imported by agents
llm = get_llm()
