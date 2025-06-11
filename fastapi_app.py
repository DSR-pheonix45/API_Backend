"""
FastAPI application for HF DABBY system
Provides REST API endpoints for agent interactions and file analysis
"""

import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import aiofiles

from agent_factory import AgentFactory
from file_handler import FileHandler
from scheduler import TaskScheduler
from load_balancer import LoadBalancer

# Add this near the top of your file
import os

# Update Redis URL to use environment variable
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Update port configuration
PORT = int(os.getenv('PORT', 8000))

# Initialize FastAPI app
app = FastAPI(
    title="HF DABBY API",
    description="FastAPI integration for HF DABBY financial analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
file_handler = FileHandler()
task_scheduler = TaskScheduler()
load_balancer = LoadBalancer()

# In-memory storage (in production, use Redis or database)
sessions = {}
uploaded_files_store = {}

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    agent_type: Optional[str] = "Dabby Consultant"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_type: str
    timestamp: datetime

class FileAnalysisRequest(BaseModel):
    session_id: str
    agent_type: Optional[str] = "Auditor Agent"

class FileAnalysisResponse(BaseModel):
    analysis: str
    file_name: str
    session_id: str
    agent_type: str
    timestamp: datetime

class TaskRequest(BaseModel):
    task_type: str
    session_id: str
    agent_type: str
    schedule_time: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    agents_available: List[str]
    active_sessions: int

# Dependency to get agent
async def get_agent(agent_type: str = "Dabby Consultant"):
    """Get agent instance using load balancer"""
    try:
        agent = load_balancer.get_agent(agent_type)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")

# Dependency to get or create session
async def get_session(session_id: str):
    """Get or create session"""
    if session_id not in sessions:
        sessions[session_id] = {
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "agent_type": "Dabby Consultant",
            "files": []
        }
    else:
        sessions[session_id]["last_activity"] = datetime.now()
    return sessions[session_id]

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        agents_available=["Dabby Consultant", "Auditor Agent", "Tax Agent"],
        active_sessions=len(sessions)
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        agents_available=["Dabby Consultant", "Auditor Agent", "Tax Agent"],
        active_sessions=len(sessions)
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent = Depends(get_agent),
    session = Depends(get_session)
):
    """Chat with an agent"""
    try:
        # Get agent based on request
        if request.agent_type != "Dabby Consultant":
            agent = load_balancer.get_agent(request.agent_type)
        
        # Process chat message
        response = agent.chat(request.message, request.session_id)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            agent_type=request.agent_type,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: str = "default",
    session = Depends(get_session)
):
    """Upload files for analysis"""
    try:
        uploaded_file_info = []
        
        # Initialize session file storage
        if session_id not in uploaded_files_store:
            uploaded_files_store[session_id] = []
        
        for file in files:
            # Create temporary file
            file_id = str(uuid.uuid4())
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
            
            # Save file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Store file info
            file_info = {
                "id": file_id,
                "name": file.filename,
                "path": file_path,
                "size": len(content),
                "uploaded_at": datetime.now().isoformat()
            }
            
            uploaded_files_store[session_id].append(file_info)
            uploaded_file_info.append(file_info)
            session["files"].append(file_info)
        
        return {
            "message": f"Successfully uploaded {len(files)} files",
            "files": uploaded_file_info,
            "session_id": session_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/analyze", response_model=FileAnalysisResponse)
async def analyze_file(
    request: FileAnalysisRequest,
    agent = Depends(get_agent),
    session = Depends(get_session)
):
    """Analyze uploaded files"""
    try:
        if request.session_id not in uploaded_files_store:
            raise HTTPException(status_code=404, detail="No files found for session")
        
        files = uploaded_files_store[request.session_id]
        if not files:
            raise HTTPException(status_code=404, detail="No files uploaded in this session")
        
        # Get agent for analysis
        agent = load_balancer.get_agent(request.agent_type)
        
        # Analyze all files (or you can modify to analyze specific file)
        analysis_results = []
        for file_info in files:
            analysis = agent.analyze_file(
                file_info["name"], 
                file_info["path"], 
                request.session_id
            )
            analysis_results.append({
                "file": file_info["name"],
                "analysis": analysis
            })
        
        # Combine analyses if multiple files
        if len(analysis_results) > 1:
            combined_analysis = "\n\n".join([
                f"**{result['file']}:**\n{result['analysis']}" 
                for result in analysis_results
            ])
        else:
            combined_analysis = analysis_results[0]["analysis"]
        
        return FileAnalysisResponse(
            analysis=combined_analysis,
            file_name=", ".join([f["name"] for f in files]),
            session_id=request.session_id,
            agent_type=request.agent_type,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.post("/schedule-task")
async def schedule_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Schedule a task for execution"""
    try:
        task_id = task_scheduler.schedule_task(
            task_type=request.task_type,
            session_id=request.session_id,
            agent_type=request.agent_type,
            schedule_time=request.schedule_time,
            parameters=request.parameters
        )
        
        return {
            "message": "Task scheduled successfully",
            "task_id": task_id,
            "task_type": request.task_type,
            "agent_type": request.agent_type,
            "session_id": request.session_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task scheduling failed: {str(e)}")

@app.get("/tasks/{session_id}")
async def get_tasks(session_id: str):
    """Get scheduled tasks for a session"""
    try:
        tasks = task_scheduler.get_tasks_by_session(session_id)
        return {"session_id": session_id, "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@app.get("/sessions")
async def get_sessions():
    """Get all active sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "created_at": info["created_at"].isoformat(),
                "last_activity": info["last_activity"].isoformat(),
                "agent_type": info["agent_type"],
                "file_count": len(info["files"])
            }
            for sid, info in sessions.items()
        ]
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its data"""
    try:
        if session_id in sessions:
            # Clean up uploaded files
            if session_id in uploaded_files_store:
                for file_info in uploaded_files_store[session_id]:
                    try:
                        os.remove(file_info["path"])
                    except:
                        pass
                del uploaded_files_store[session_id]
            
            del sessions[session_id]
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.get("/agents")
async def get_available_agents():
    """Get list of available agents"""
    return {
        "agents": [
            {
                "name": "Dabby Consultant",
                "description": "General financial consulting and analysis",
                "type": "consultant"
            },
            {
                "name": "Auditor Agent",
                "description": "Specialized auditing and compliance analysis",
                "type": "auditor"
            },
            {
                "name": "Tax Agent",
                "description": "Tax compliance and optimization analysis",
                "type": "tax"
            }
        ]
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("HF DABBY FastAPI server starting...")
    task_scheduler.start()
    print("Task scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("HF DABBY FastAPI server shutting down...")
    task_scheduler.stop()
    print("Task scheduler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=PORT,
        reload=os.getenv('ENVIRONMENT', 'development') == 'development'
    )
