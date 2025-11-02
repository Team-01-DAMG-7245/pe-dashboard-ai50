"""
Lab 7: RAG Pipeline Dashboard
Generates investor dashboards using vector DB retrieval
"""

import os
from typing import Dict
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb

app = FastAPI(title="PE Dashboard API - RAG Pipeline")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use EXISTING vector database instead of creating new one
chroma_client = chromadb.PersistentClient(path="data/vector_db")
collection = chroma_client.get_collection("ai50_companies")
print(f"Connected to existing collection with {collection.count()} chunks")

# Import the embedding model for searches
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class DashboardRequest(BaseModel):
    company_id: str
    top_k: int = 10

class DashboardResponse(BaseModel):
    company_id: str
    dashboard: str
    chunks_used: int

def load_dashboard_prompt() -> str:
    """Load the dashboard system prompt"""
    with open("src/prompts/dashboard_system.md", "r") as f:
        return f.read()

@app.post("/dashboard/rag", response_model=DashboardResponse)
async def generate_rag_dashboard(request: DashboardRequest):
    """
    Generate dashboard using RAG pipeline
    """
    
    try:
        # Retrieve relevant chunks for the company
        queries = [
            "company overview business model products",
            "funding investment valuation raised", 
            "leadership team CEO founder executives",
            "growth revenue customers metrics",
            "market sentiment news visibility",
            "risks challenges competition"
        ]
        
        all_chunks = []
        for query in queries:
            # Generate embedding for query
            query_embedding = embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=2,
                where={"company_id": request.company_id}
            )
            
            if results['documents'] and results['documents'][0]:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    all_chunks.append({
                        'text': doc,
                        'metadata': meta
                    })
        
        # Deduplicate
        seen = set()
        unique_chunks = []
        for chunk in all_chunks:
            if chunk['text'] not in seen:
                seen.add(chunk['text'])
                unique_chunks.append(chunk)
        
        unique_chunks = unique_chunks[:request.top_k]
        
        # Combine chunks into context
        context = "\n\n".join([chunk['text'] for chunk in unique_chunks])
        
        # Load dashboard prompt
        system_prompt = load_dashboard_prompt()
        
        # Create user prompt
        user_prompt = f"""
        Company: {request.company_id}
        
        Context from scraped data:
        {context}
        
        Generate the 8-section investor dashboard. Remember:
        - Use ONLY the provided data
        - Say "Not disclosed." when information is missing
        - Include all 8 sections in order
        - Always end with "## Disclosure Gaps" section
        """
        
        # Generate dashboard
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        dashboard = response.choices[0].message.content
        
        return DashboardResponse(
            company_id=request.company_id,
            dashboard=dashboard,
            chunks_used=len(unique_chunks)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "RAG Dashboard API - Lab 7", "endpoint": "/dashboard/rag"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)