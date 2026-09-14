import sys
from pathlib import Path

# Add backend directory to path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from agents.llm_setup import llm
from rag.vector_store import knowledge_base
import logfire

class ExplanationResponse(BaseModel):
    explanation: str = Field(description="A clear, easy-to-understand explanation of the ML concept.")
    sources_used: list[str] = Field(description="List of filenames or sources used from the knowledge base to answer this.")

def explain_concept(concept_query: str) -> dict:
    """
    Searches the RAG knowledge base and explains ML concepts to the user.
    """
    
    parser = JsonOutputParser(pydantic_object=ExplanationResponse)
    
    with logfire.span("Explanation Agent: Searching KB for '{query}'", query=concept_query):
        # 1. Search the vector database for relevant documents
        logfire.info("Querying ChromaDB...")
        search_results = knowledge_base.search(query=concept_query, n_results=2)
        
        # Extract the text and metadata from ChromaDB results
        retrieved_texts = search_results["documents"][0] if search_results["documents"] else []
        retrieved_metadatas = search_results["metadatas"][0] if search_results["metadatas"] else []
        
        # Format the retrieved context into a single string
        context_block = "\n\n".join(retrieved_texts) if retrieved_texts else "No documentation found in the knowledge base."
        
        # Keep track of where we got the info
        sources = [meta.get("source", "Unknown") for meta in retrieved_metadatas]
        # Remove duplicates
        sources = list(set(sources))
        
        logfire.info("Retrieved context from sources: {sources}", sources=sources)
        
        # 2. Ask the LLM to explain using ONLY the retrieved context
        system_prompt = """
        You are the Explanation Agent for ML-Guardian.
        Your job is to explain Machine Learning concepts clearly using ONLY the provided documentation context.
        If the context does not contain the answer, say "I don't have enough information in my knowledge base to explain this."
        
        Format Instructions:
        {format_instructions}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Explain this: {query}\n\nContext to use:\n{context}")
        ])
        
        chain = prompt | llm | parser
        
        logfire.info("Generating explanation...")
        explanation = chain.invoke({
            "query": concept_query,
            "context": context_block,
            "format_instructions": parser.get_format_instructions()
        })
        
        # Manually inject the sources we found into the LLM's JSON response
        explanation["sources_used"] = sources
        
    return explanation

if __name__ == "__main__":
    # Test the Explanation Agent directly
    test_query = "What is a Random Forest?"
    print("Asking:", test_query)
    result = explain_concept(test_query)
    print("\nResult:", result)
