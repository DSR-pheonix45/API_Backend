from base_agent import BaseAgent

class ConsultantAgent(BaseAgent):
    """Dabby Consultant Agent implementation"""
    
    @property
    def name(self):
        return "Dabby Consultant"
    
    @property
    def system_prompt(self):
        return """You are Dabby Consultant, an AI assistant specialized in analyzing documents and providing insightful consultations.
When analyzing files, first provide a crisp summary of understanding and form a thesis as a consultant would.
Based on the user's prompt, determine whether to provide:
1. Quick Response: Concise, actionable insights
2. Chain of Thought Analysis: Detailed reasoning with step-by-step analysis
Always conclude with actionable insights, clear opinions, and the basis for those opinions."""
    
    def analyze_prompt(self, prompt):
        """Determine whether to provide a quick response or detailed analysis"""
        complex_indicators = ["analyze", "explain", "compare", "evaluate", "why", "how", "detail"]
        
        for indicator in complex_indicators:
            if indicator in prompt.lower():
                return "Chain of Thought Analysis"
        
        return "Quick Response"
    
    def chat(self, message, session_id):
        """Override chat to include response type determination"""
        if not message.strip():
            return "Please provide a message."
            
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Determine response type
        response_type = self.analyze_prompt(message)
        
        # Add user message to conversation history with instruction
        prompt_with_instruction = f"{message}\n\nPlease provide a {response_type}."
        self.conversation_history[session_id].append({
            "role": "user",
            "content": prompt_with_instruction
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
