class CheckToolBaseError(Exception):
    """Base exception for all CheckTool errors"""
    pass

class ConfigurationError(CheckToolBaseError):
    pass

class TaskError(CheckToolBaseError):
    pass

class ValidationError(CheckToolBaseError):
    pass
