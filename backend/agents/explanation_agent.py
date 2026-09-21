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
from config import settings
from tavily import TavilyClient
import logfire

class ExplanationResponse(BaseModel):
    explanation: str = Field(description="A clear, easy-to-understand explanation of the ML concept.")
    sources_used: list[str] = Field(description="List of filenames or Web URLs used to answer this.")

def explain_concept(concept_query: str) -> dict:
    """
    Searches the RAG knowledge base AND the live internet (via Tavily) to explain ML concepts.
    """
    
    parser = JsonOutputParser(pydantic_object=ExplanationResponse)
    
    with logfire.span("Explanation Agent: Searching KB and Web for '{query}'", query=concept_query):
        sources = []
        
        # ────────────────────────────────────────────────────────
        # 1. LOCAL SEARCH (ChromaDB)
        # ────────────────────────────────────────────────────────
        logfire.info("Querying local ChromaDB...")
        search_results = knowledge_base.search(query=concept_query, n_results=2)
        
        retrieved_texts = search_results["documents"][0] if search_results["documents"] else []
        retrieved_metadatas = search_results["metadatas"][0] if search_results["metadatas"] else []
        
        local_context = "\n\n".join(retrieved_texts) if retrieved_texts else "No local documentation found."
        
        for meta in retrieved_metadatas:
            sources.append(meta.get("source", "Local Knowledge Base"))
            
        # ────────────────────────────────────────────────────────
        # 2. LIVE WEB SEARCH (Tavily)
        # ────────────────────────────────────────────────────────
        web_context = "No web search performed."
        try:
            if settings.TAVILY_API_KEY:
                logfire.info("Querying Tavily Web Search...")
                tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
                tavily_response = tavily.search(concept_query, search_depth="basic", max_results=2)
                
                web_snippets = []
                for result in tavily_response.get("results", []):
                    web_snippets.append(f"Source: {result['url']}\nContent: {result['content']}")
                    sources.append(result['url'])
                
                if web_snippets:
                    web_context = "\n\n".join(web_snippets)
        except Exception as e:
            logfire.warn(f"Tavily search failed: {e}")
            
        # Remove duplicates
        sources = list(set(sources))
        logfire.info(f"Retrieved context from {len(sources)} total sources (Local + Web).")
        
        # ────────────────────────────────────────────────────────
        # 3. LLM SYNTHESIS
        # ────────────────────────────────────────────────────────
        system_prompt = """
        You are the Explanation Agent for ML-Guardian.
        Your job is to explain Machine Learning concepts clearly using BOTH the local knowledge base and the live web search results.
        Synthesize the information to provide the most accurate, up-to-date answer possible.
        
        Format Instructions:
        {format_instructions}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Explain this: {query}\n\n--- LOCAL KNOWLEDGE ---\n{local_context}\n\n--- LIVE WEB SEARCH ---\n{web_context}")
        ])
        
        chain = prompt | llm | parser
        
        logfire.info("Generating final explanation...")
        explanation = chain.invoke({
            "query": concept_query,
            "local_context": local_context,
            "web_context": web_context,
            "format_instructions": parser.get_format_instructions()
        })
        
        # Manually inject the combined sources into the LLM's JSON response
        explanation["sources_used"] = sources
        
    return explanation

if __name__ == "__main__":
    # Test the Explanation Agent directly
    test_query = "What is the latest version of Llama released by Meta?"
    print("Asking:", test_query)
    result = explain_concept(test_query)
    print("\nResult:", result)
