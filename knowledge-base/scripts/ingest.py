import os
import sys
import uuid
from pathlib import Path

# Add the backend directory to Python's path so we can import from rag and config
backend_dir = str(Path(__file__).resolve().parent.parent.parent / "backend")
sys.path.append(backend_dir)

from rag.vector_store import knowledge_base

# Directory where the raw text documents are stored
DOCS_DIR = Path(__file__).resolve().parent.parent / "documents"

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Split a long text document into smaller chunks with some overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_documents():
    """Read all .txt files from the documents folder and load them into ChromaDB."""
    print("Starting document ingestion...")
    
    if not DOCS_DIR.exists():
        print(f"Directory not found: {DOCS_DIR}")
        return

    txt_files = list(DOCS_DIR.glob("*.txt"))
    if not txt_files:
        print("No .txt files found in the documents folder.")
        return

    for file_path in txt_files:
        print(f"Processing: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Chunk the document
        chunks = chunk_text(content)
        
        # 2. Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            # Save the source filename so the AI can cite it later!
            metadatas.append({"source": file_path.name, "chunk_index": i})
            ids.append(f"{file_path.name}_{i}_{uuid.uuid4().hex[:6]}")
            
        # 3. Add to vector database
        knowledge_base.add_documents(documents=documents, metadatas=metadatas, ids=ids)
        print(f"  -> Added {len(chunks)} chunks.")

    print("Ingestion complete! The knowledge base is updated.")

if __name__ == "__main__":
    ingest_documents()
