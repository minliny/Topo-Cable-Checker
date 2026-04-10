from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import warnings

@dataclass
class LLMResponse:
    content: Dict[str, Any]
    raw_output: str

class ILLMGateway(ABC):
    """
    DEPRECATED: This interface is part of the legacy internal AI generation pipeline.
    The system is moving away from embedded AI calls. 
    Use external AI tools to generate rule JSONs based on exported Rule Authoring Specs instead.
    """
    def __init__(self):
        warnings.warn("ILLMGateway is deprecated and should not be used in the mainline system.", DeprecationWarning, stacklevel=2)

    @abstractmethod
    def generate_structured_rule_draft(
        self,
        system_instruction: str,
        user_input: str,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        pass
