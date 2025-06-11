"""
Simplified FastAPI application for testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="HF DABBY API - Simple Test",
    description="Simplified API for testing",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    agent_type: Optional[str] = "Test Agent"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_type: str
    timestamp: datetime

# Simple in-memory storage
sessions = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "version": "0.1.0",
        "timestamp": datetime.now(),
        "agents_available": ["Test Agent", "Auditor Agent", "Tax Agent"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    # Store message in session
    if request.session_id not in sessions:
        sessions[request.session_id] = []
    
    sessions[request.session_id].append(request.message)
    
    # Simple response based on agent type
    if request.agent_type == "Auditor Agent":
        response = f"As an Auditor Agent, I've analyzed your request: '{request.message}'. To provide a comprehensive financial audit, I would need specific financial statements, transaction records, and compliance requirements."
    elif request.agent_type == "Tax Agent":
        response = f"As a Tax Agent, I've reviewed your query: '{request.message}'. For proper tax analysis, I would need income statements, expense records, and applicable tax regulations."
    else:
        response = f"Received your message: '{request.message}'. This is a test response from {request.agent_type}."
    
    return ChatResponse(
        response=response,
        session_id=request.session_id,
        agent_type=request.agent_type,
        timestamp=datetime.now()
    )

@app.get("/agents")
async def get_available_agents():
    """Get list of available agents"""
    return {
        "agents": [
            {
                "name": "Test Agent",
                "description": "Simple test agent for API testing",
                "type": "test"
            },
            {
                "name": "Auditor Agent",
                "description": "Specialized in financial auditing and compliance",
                "type": "auditor"
            },
            {
                "name": "Tax Agent",
                "description": "Specialized in tax analysis and planning",
                "type": "tax"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )