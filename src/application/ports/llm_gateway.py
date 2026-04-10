from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: Dict[str, Any]
    raw_output: str

class ILLMGateway(ABC):
    @abstractmethod
    def generate_structured_rule_draft(
        self,
        system_instruction: str,
        user_input: str,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        pass
