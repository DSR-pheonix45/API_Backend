# HF DABBY - Financial Analysis System with FastAPI Integration

A comprehensive financial analysis system featuring multiple specialized AI agents (Auditor, Tax, and Consultant) with FastAPI backend, task scheduling, and load balancing capabilities.

## 📁 Project Structure

```
HF DABBY/
├── Core Application Files
│   ├── main.py                 # Gradio interface application
│   ├── fastapi_app.py         # FastAPI REST API application
│   └── start.py               # Unified startup script
│
├── Agent System
│   ├── base_agent.py          # Base agent class
│   ├── agent_factory.py       # Agent factory pattern
│   ├── auditor_agent.py       # Specialized auditor agent
│   ├── tax_agent.py           # Specialized tax agent
│   ├── consultant_agent.py    # General consultant agent
│   └── company_info.py        # Company information handling
│
├── Infrastructure
│   ├── scheduler.py           # Task scheduling system
│   ├── load_balancer.py       # Load balancing system
│   ├── celery_config.py       # Celery configuration
│   ├── celery_tasks.py        # Background task definitions
│   ├── file_handler.py        # File processing utilities
│   └── llm_service.py         # LLM service interface
│
├── Deployment
│   ├── docker-compose.yml     # Docker orchestration
│   ├── Dockerfile             # FastAPI container
│   ├── Dockerfile.gradio      # Gradio container
│   ├── nginx.conf             # Nginx load balancer config
│   └── run_app.bat            # Windows startup script
│
├── Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── .vscode/              # VS Code settings and tasks
│
└── Documentation
    └── README.md              # This file
```

## 🌟 Features

### Core Features
- **Multiple AI Agents**: Specialized agents for auditing, tax analysis, and financial consulting
- **Document Analysis**: Support for PDF, DOCX, Excel, CSV, and text files
- **Real-time Chat Interface**: Interactive Gradio-based UI
- **Audit Report Generation**: Professional audit reports in multiple formats

### New FastAPI Integration
- **REST API Endpoints**: Complete RESTful API for all agent interactions
- **Asynchronous Processing**: Efficient handling of concurrent requests
- **Load Balancing**: Intelligent distribution of requests across agent instances
- **Task Scheduling**: Background task execution with Celery and APScheduler
- **Real-time Monitoring**: Health checks and performance metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                   │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Instance 1  │  FastAPI Instance 2  │  Gradio UI   │
├─────────────────────────────────────────────────────────────┤
│                        Redis Cache                         │
├─────────────────────────────────────────────────────────────┤
│  Celery Workers  │  Task Scheduler  │  Background Tasks    │
├─────────────────────────────────────────────────────────────┤
│       Agent Pool (Auditor, Tax, Consultant Agents)        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis Server
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hf-dabby
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start the system**

   **Option A: Using the startup script (Recommended)**
   ```bash
   # Development mode
   python start.py --mode dev

   # Production mode
   python start.py --mode prod --workers 4
   ```

   **Option B: Using batch file (Windows)**
   ```cmd
   # Development mode
   run_app.bat dev

   # Production mode
   run_app.bat prod

   # Docker deployment
   run_app.bat docker
   ```

   **Option C: Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Access URLs

- **Gradio Interface**: http://localhost:7860
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555 (Docker only)

## 📖 API Documentation

### Authentication
The API currently supports public access. For production, implement authentication middleware.

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Chat with Agent
```http
POST /chat
Content-Type: application/json

{
  "message": "Analyze the financial data",
  "session_id": "unique-session-id",
  "agent_type": "Auditor Agent"
}
```

#### Upload Files
```http
POST /upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.xlsx]
session_id: "unique-session-id"
```

#### Analyze Files
```http
POST /analyze
Content-Type: application/json

{
  "session_id": "unique-session-id",
  "agent_type": "Auditor Agent"
}
```

#### Schedule Task
```http
POST /schedule-task
Content-Type: application/json

{
  "task_type": "audit_report",
  "session_id": "unique-session-id",
  "agent_type": "Auditor Agent",
  "schedule_time": "2025-06-12T10:00:00Z",
  "parameters": {
    "audit_type": "financial"
  }
}
```

### Available Agents
- **Dabby Consultant**: General financial consulting and analysis
- **Auditor Agent**: Specialized auditing and compliance analysis
- **Tax Agent**: Tax compliance and optimization analysis

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_WORKERS=4

# Load Balancer Configuration
LB_ALGORITHM=round_robin
LB_MAX_CONNECTIONS_PER_AGENT=10

# File Upload Configuration
MAX_FILE_SIZE=100MB
UPLOAD_DIR=./uploads
```

### Load Balancing Algorithms

Choose from the following algorithms in your configuration:

- `round_robin`: Distributes requests evenly across instances
- `least_connections`: Routes to the instance with fewest active connections
- `weighted_round_robin`: Uses instance weights for distribution
- `response_time`: Routes based on average response times

## 🔧 Advanced Features

### Task Scheduling

The system supports both immediate and scheduled task execution:

1. **Immediate Tasks**: Executed via FastAPI endpoints
2. **Scheduled Tasks**: Using Celery Beat or APScheduler
3. **Periodic Tasks**: Automated daily, weekly, and monthly reports

### Load Balancing

Multiple load balancing strategies ensure optimal performance:

- **Dynamic Scaling**: Automatic scaling based on load
- **Health Monitoring**: Continuous health checks
- **Circuit Breaker**: Automatic failover for unhealthy instances

### Monitoring

Built-in monitoring capabilities:

- **Health Checks**: Real-time service health monitoring
- **Performance Metrics**: Response times and throughput
- **Task Status**: Background task execution tracking

## 🐳 Docker Deployment

### Single Instance
```bash
docker build -t hf-dabby .
docker run -p 8000:8000 hf-dabby
```

### Full Stack with Docker Compose
```bash
docker-compose up -d
```

This starts:
- Multiple FastAPI instances
- Redis for caching and task queue
- Celery workers and beat scheduler
- Nginx load balancer
- Gradio interface
- Monitoring tools (optional)

## 📊 Monitoring and Debugging

### Logs
- Application logs: Check console output or log files
- Nginx logs: `/var/log/nginx/` (in Docker)
- Celery logs: View in Flower UI or console

### Health Checks
- **FastAPI**: `GET /health`
- **Nginx**: `GET /nginx-health`
- **Redis**: Use Redis CLI `redis-cli ping`

### Performance Monitoring
- Access Celery Flower at http://localhost:5555
- Monitor load balancer stats via custom endpoints
- Use built-in FastAPI metrics endpoints

## 🛠️ Development

### Running in Development Mode
```bash
python start.py --mode dev --services fastapi celery gradio
```

### Running Specific Services
```bash
# Only FastAPI
python start.py --services fastapi

# Only Celery workers
python start.py --services celery

# Only Gradio interface
python start.py --services gradio
```

### Testing
```bash
# Run API tests
pytest tests/

# Test specific endpoints
curl http://localhost:8000/health
```

## 🔒 Security Considerations

For production deployment:

1. **Enable HTTPS**: Configure SSL certificates in Nginx
2. **Add Authentication**: Implement JWT or OAuth2
3. **Rate Limiting**: Configure appropriate rate limits
4. **Environment Variables**: Secure API keys and secrets
5. **Network Security**: Use proper firewall rules

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support:
1. Check the documentation
2. Review common issues in the troubleshooting section
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with Gradio interface
- **v2.0.0**: FastAPI integration, load balancing, and task scheduling

## 🧹 **Clean Project Structure**

This project has been cleaned up to include only essential files. Removed files:
- ~~`app.py`~~ - Replaced by `fastapi_app.py`
- ~~`app_with_sidebar.py`~~ - Deprecated old interface
- ~~`new_app.py`~~ - Deprecated old interface  
- ~~`run_app.py`~~ - Replaced by `start.py`
- ~~`launch_datalis.py`~~ - Deprecated launcher
- ~~`run_datalis.bat`~~ - Replaced by `run_app.bat`
- ~~`test_system.py`~~ - Development-only test file

### Current File Count: **24 essential files**

For detailed information about each file's purpose, see `FILE_GUIDE.md`.