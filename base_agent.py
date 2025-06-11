from abc import ABC, abstractmethod
from file_handler import FileHandler
from llm_service import LLMService

class BaseAgent(ABC):
    """Base class for all agent implementations"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.file_handler = FileHandler()
        self.conversation_history = {}
    
    @property
    @abstractmethod
    def system_prompt(self):
        """Return the system prompt for this agent"""
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Return the name of this agent"""
        pass
    
    def analyze_file(self, file_name, file_path, session_id):
        """Analyze a file and return insights"""
        file_content = self.file_handler.process_file(file_path)
        
        if "Error" in file_content or "not found" in file_content:
            return file_content
        
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add file content to conversation
        file_message = f"Please analyze this file: {file_content[:5000]}..."
        self.conversation_history[session_id].append({
            "role": "user",
            "content": file_message
        })
        
        # Get response from LLM
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history[session_id]
        response = self.llm_service.get_chat_response(messages)
        
        # Add response to conversation history
        self.conversation_history[session_id].append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def chat(self, message, session_id):
        """Process a chat message and return a response"""
        if not message.strip():
            return "Please provide a message."
            
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add user message to conversation history
        self.conversation_history[session_id].append({
            "role": "user",
            "content": message
        })
        
        # Get response from LLM
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history[session_id]
        response = self.llm_service.get_chat_response(messages)
        
        # Add response to conversation history
        self.conversation_history[session_id].append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def clear_history(self, session_id):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            self.conversation_history[session_id] = []
