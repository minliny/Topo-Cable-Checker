from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: Dict[str, Any]
    raw_output: str

class ILLMGateway(ABC):
    """
    Abstract port for LLM model invocation.
    Application layer depends on this interface to avoid hardcoding specific LLM providers.
    """
    
    @abstractmethod
    def generate_structured_rule_draft(self, system_prompt: str, user_input: str) -> LLMResponse:
        """
        Takes a system prompt and user input, and returns a structured JSON-like response.
        """
        pass
