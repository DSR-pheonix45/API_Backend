from consultant_agent import ConsultantAgent
from auditor_agent import AuditorAgent
from tax_agent import TaxAgent

class AgentFactory:
    """Factory for creating agent instances"""
    
    @staticmethod
    def get_agent(agent_name):
        """Get an agent instance by name"""
        if agent_name == "Dabby Consultant":
            return ConsultantAgent()
        elif agent_name == "Auditor Agent":
            return AuditorAgent()
        elif agent_name == "Tax Agent":
            return TaxAgent()
        else:
            # Default to consultant agent
            return ConsultantAgent()
