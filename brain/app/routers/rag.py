from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import aiofiles
import tempfile
import os
import requests
from urllib.parse import urlparse
import logging
from ..models.schemas import RAGIngestRequest, RAGQueryRequest, RAGQueryResponse, RAGSearchResult
from ..deps import get_embedder, get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter()

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file"""
    content_type = file.content_type or ""
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        if content_type.startswith("text/") or file.filename.endswith((".txt", ".md", ".py", ".js", ".json")):
            # Plain text files
            text = content.decode("utf-8", errors="ignore")
        elif content_type == "application/pdf" or file.filename.endswith(".pdf"):
            # PDF files (requires PyPDF2 or similar)
            try:
                import PyPDF2
                with open(tmp_file_path, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                raise HTTPException(status_code=400, detail="PDF processing not available. Install PyPDF2.")
        else:
            # Fallback to plain text
            text = content.decode("utf-8", errors="ignore")
        
        return text
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

async def extract_text_from_url(url: str) -> str:
    """Extract text from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "").lower()
        
        if "text/html" in content_type:
            # HTML content (requires BeautifulSoup)
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, "html.parser")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = " ".join(chunk for chunk in chunks if chunk)
            except ImportError:
                raise HTTPException(status_code=400, detail="HTML processing not available. Install BeautifulSoup4.")
        else:
            # Plain text
            text = response.text
        
        return text
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from URL: {str(e)}")

def semantic_chunk(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into semantic chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        if chunk.strip():
            chunks.append(chunk.strip())
    
    return chunks

@router.post("/ingest")
async def ingest_content(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    source: Optional[str] = Form(None)
):
    """Ingest content into RAG system"""
    try:
        # Extract text from various sources
        if file:
            content = await extract_text_from_file(file)
            source = source or file.filename
        elif url:
            content = await extract_text_from_url(url)
            source = source or urlparse(url).netloc
        elif text:
            content = text
            source = source or "direct_input"
        else:
            raise HTTPException(status_code=400, detail="No content provided")
        
        # Split into chunks
        chunks = semantic_chunk(content)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No content to ingest")
        
        # Get embedder and vector store
        embedder = get_embedder()
        store = get_vector_store()
        
        # Generate embeddings
        embeddings = await embedder.encode(chunks)
        
        # Create metadata
        metadata = []
        for i, chunk in enumerate(chunks):
            meta = {
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            }
            metadata.append(meta)
        
        # Store in vector database
        count = await store.upsert(chunks, embeddings, metadata)
        
        return {
            "ingested": count,
            "source": source,
            "chunks": len(chunks),
            "total_characters": len(content)
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """Query RAG system with context retrieval"""
    try:
        # Get embedder and vector store
        embedder = get_embedder()
        store = get_vector_store()
        
        # Generate query embedding
        query_embedding = await embedder.encode([request.query])
        
        # Search for relevant chunks
        search_results = await store.search(query_embedding[0], request.k)
        
        # Format context
        context_parts = []
        references = []
        
        for result in search_results:
            context_parts.append(f"Source: {result.get('source', 'unknown')}\n{result.get('text', '')}")
            
            references.append(RAGSearchResult(
                content=result.get("text", ""),
                source=result.get("source", "unknown"),
                score=result.get("score", 0.0),
                metadata=result.get("metadata", {})
            ))
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Call LLM with context (simplified - could route to local/cloud)
        answer = await call_llm_with_context(request.query, context, request.route_hint)
        
        return RAGQueryResponse(
            answer=answer,
            references=references,
            context_used=context[:500] + "..." if len(context) > 500 else context,
            model_used="local_default"  # Would be dynamic based on routing
        )
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

async def call_llm_with_context(query: str, context: str, route_hint: Optional[str] = None) -> str:
    """Call LLM with retrieved context (simplified implementation)"""
    # This is a simplified implementation
    # In practice, this would route to Ollama or OpenRouter based on policy
    
    prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {query}

Answer based only on the provided context. If the context doesn't contain enough information, say so."""
    
    # For now, return a mock response
    # In practice, this would make actual API calls
    return f"Based on the provided context, here's my response to: {query}\n\n[This is a mock response - implement actual LLM calling logic]"

@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        store = get_vector_store()
        return store.get_stats()
    except Exception as e:
        logger.error(f"RAG stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get RAG stats: {str(e)}")