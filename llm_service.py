import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    """Service for interacting with LLM APIs"""
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=self.api_key)
        self.response_cache = {}  # Simple cache for performance
    
    def get_response(self, prompt, system_message, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7):
        """Get a response from the LLM with caching for performance."""
        # Create a unique key for caching based on parameters
        cache_key = f"{prompt[:100]}_{model}_{system_message}"
            
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
            
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
            )
            response = chat_completion.choices[0].message.content
            self.response_cache[cache_key] = response  # Store the response in cache
            return response
        except Exception as e:
            error_msg = f"Error calling LLM API: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_chat_response(self, messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens = 2048):
        """Get a response for a chat conversation."""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            error_msg = f"Error calling LLM API: {str(e)}"
            print(error_msg)
            return error_msg
