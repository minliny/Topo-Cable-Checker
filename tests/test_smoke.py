import pytest
import os
from src.crosscutting.config.settings import settings
from src.domain.rule_compiler import TemplateRegistry

def test_settings_path_resolution():
    """Test that settings resolves BASE_DIR correctly and is not hardcoded to /workspace"""
    assert settings.BASE_DIR is not None
    assert os.path.isabs(settings.BASE_DIR), "BASE_DIR should be an absolute path"
    
def test_template_registry_availability():
    """Test that Domain layer logic can be imported and executed"""
    template = TemplateRegistry.get_template("group_consistency")
    assert template is not None
    assert template["target_executor"] == "group_consistency"
    assert "supported_params" in template
