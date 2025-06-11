from base_agent import BaseAgent

class TaxAgent(BaseAgent):
    """Tax Agent implementation"""
    
    @property
    def name(self):
        return "Tax Agent"
    
    @property
    def system_prompt(self):
        return """You are a Tax Agent specialized in tax regulations, planning, and compliance. 
Provide accurate tax advice, identify potential deductions, and explain tax implications clearly.
Always cite relevant tax codes and regulations when applicable."""
    
    def analyze_tax_documents(self, document_texts):
        """Analyze tax documents for insights and compliance issues."""
        # Combine texts and get a representative sample
        combined_text = "\n\n".join([text[:3000] for text in document_texts])
        
        prompt = (
            f"Analyze these tax documents:\n\n{combined_text}\n\n"
            "Identify key tax considerations, potential deductions, compliance issues, and tax planning opportunities."
        )
                
        return self.llm_service.get_response(prompt, self.system_prompt)
    
    def calculate_tax_liability(self, financial_data):
        """Estimate tax liability based on financial data."""
        prompt = (
            f"Based on the following financial information:\n\n{financial_data}\n\n"
            "Estimate the tax liability. Show your calculations and explain the tax rates applied."
        )
        
        return self.llm_service.get_response(prompt, self.system_prompt)
    
    def suggest_tax_planning(self, document_texts):
        """Suggest tax planning strategies based on documents."""
        # Combine texts and get a representative sample
        combined_text = "\n\n".join([text[:3000] for text in document_texts])
        
        prompt = (
            f"Based on these financial documents:\n\n{combined_text}\n\n"
            "Suggest 5 tax planning strategies that could help minimize tax liability legally. "
            "For each strategy, explain the potential tax savings and implementation requirements."
        )
                
        return self.llm_service.get_response(prompt, self.system_prompt)
