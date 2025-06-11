# HF DABBY - Essential Files Documentation

This document describes the purpose of each essential file in the HF DABBY system.

## Core Application Files

### `main.py`
- **Purpose**: Gradio-based web interface for interactive chat and file analysis
- **Key Features**: File upload, agent selection, chat interface, audit report generation
- **Usage**: `python main.py` to start Gradio interface on port 7860

### `fastapi_app.py`
- **Purpose**: FastAPI REST API server for programmatic access
- **Key Features**: RESTful endpoints, async processing, API documentation
- **Usage**: `uvicorn fastapi_app:app --reload` or via startup script

### `start.py`
- **Purpose**: Unified startup script for development and production
- **Key Features**: Multi-service orchestration, environment detection, process management
- **Usage**: `python start.py --mode dev` or `python start.py --mode prod`

## Agent System

### `base_agent.py`
- **Purpose**: Abstract base class for all agent types
- **Key Features**: Common interface, LLM integration, conversation history
- **Dependencies**: llm_service.py, file_handler.py

### `agent_factory.py`
- **Purpose**: Factory pattern for creating agent instances
- **Key Features**: Centralized agent creation, type mapping
- **Usage**: `AgentFactory.get_agent("Auditor Agent")`

### `auditor_agent.py`
- **Purpose**: Specialized agent for financial auditing tasks
- **Key Features**: Audit framework detection, report generation, compliance checking
- **Inherits**: base_agent.py

### `tax_agent.py`
- **Purpose**: Specialized agent for tax analysis and compliance
- **Key Features**: Tax calculations, compliance checking, optimization suggestions
- **Inherits**: base_agent.py

### `consultant_agent.py`
- **Purpose**: General financial consulting agent
- **Key Features**: General financial advice, analysis, consultation
- **Inherits**: base_agent.py

### `company_info.py`
- **Purpose**: Company information collection and management
- **Key Features**: Gradio UI components for company data entry
- **Integration**: Used by agents for context-aware responses

## Infrastructure

### `scheduler.py`
- **Purpose**: Task scheduling and background job management
- **Key Features**: APScheduler integration, periodic tasks, task monitoring
- **Dependencies**: agent_factory.py

### `load_balancer.py`
- **Purpose**: Intelligent request distribution across agent instances
- **Key Features**: Multiple algorithms, health monitoring, auto-scaling
- **Dependencies**: agent_factory.py

### `celery_config.py`
- **Purpose**: Celery configuration for distributed task processing
- **Key Features**: Redis backend, queue configuration, periodic tasks
- **Dependencies**: Redis server

### `celery_tasks.py`
- **Purpose**: Background task definitions for Celery workers
- **Key Features**: File analysis, report generation, periodic maintenance
- **Dependencies**: celery_config.py, agent_factory.py

### `file_handler.py`
- **Purpose**: File processing and content extraction utilities
- **Key Features**: Multi-format support (PDF, DOCX, Excel, CSV, TXT)
- **Dependencies**: Various file processing libraries

### `llm_service.py`
- **Purpose**: Language model service interface
- **Key Features**: API abstraction, conversation management
- **Dependencies**: External LLM API (Groq)

## Deployment

### `docker-compose.yml`
- **Purpose**: Multi-container orchestration for production deployment
- **Key Features**: FastAPI instances, Redis, Celery workers, Nginx
- **Usage**: `docker-compose up -d`

### `Dockerfile`
- **Purpose**: Container definition for FastAPI application
- **Key Features**: Python 3.11, production-ready configuration
- **Usage**: Built automatically by docker-compose

### `Dockerfile.gradio`
- **Purpose**: Container definition for Gradio interface
- **Key Features**: Separate container for UI components
- **Usage**: Built automatically by docker-compose

### `nginx.conf`
- **Purpose**: Nginx configuration for load balancing and reverse proxy
- **Key Features**: Multiple upstreams, rate limiting, SSL support
- **Usage**: Used automatically in Docker deployment

### `run_app.bat`
- **Purpose**: Windows batch file for easy startup
- **Key Features**: Environment checking, service starting
- **Usage**: `run_app.bat dev` or `run_app.bat prod`

## Configuration

### `requirements.txt`
- **Purpose**: Python package dependencies
- **Key Features**: Complete dependency list with versions
- **Usage**: `pip install -r requirements.txt`

### `.env.example`
- **Purpose**: Environment variables template
- **Key Features**: All configuration options documented
- **Usage**: Copy to `.env` and customize

### `.vscode/`
- **Purpose**: VS Code workspace configuration
- **Key Features**: Debug configs, tasks, settings
- **Contents**: launch.json, tasks.json

## File Dependencies

```
main.py
├── agent_factory.py
├── file_handler.py
└── company_info.py

fastapi_app.py
├── agent_factory.py
├── file_handler.py
├── scheduler.py
└── load_balancer.py

scheduler.py
└── agent_factory.py

load_balancer.py
└── agent_factory.py

celery_tasks.py
├── celery_config.py
└── agent_factory.py

All agents (auditor_agent.py, tax_agent.py, consultant_agent.py)
├── base_agent.py
├── file_handler.py
└── llm_service.py
```

## Essential vs Optional Files

### Essential Files (Cannot be removed)
- `main.py` - Core Gradio interface
- `fastapi_app.py` - Core API server
- `base_agent.py` - Required by all agents
- `agent_factory.py` - Required by all applications
- `auditor_agent.py`, `tax_agent.py`, `consultant_agent.py` - Core agents
- `file_handler.py` - Required for file processing
- `llm_service.py` - Required for AI functionality
- `requirements.txt` - Required for dependencies

### Production Features (Can be simplified for basic use)
- `scheduler.py` - Remove if no background tasks needed
- `load_balancer.py` - Remove if single instance is sufficient
- `celery_config.py`, `celery_tasks.py` - Remove if no distributed processing
- Docker files - Remove if not using containers
- `nginx.conf` - Remove if not using load balancing

### Optional Files
- `company_info.py` - Can be removed if company info not needed
- `start.py` - Can be removed, start services manually
- `run_app.bat` - Windows-specific, not needed on other platforms
- `.vscode/` - IDE-specific, not needed for runtime
