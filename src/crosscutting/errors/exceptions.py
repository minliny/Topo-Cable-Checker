"""
P0-2/P0-5: Extended Exception Hierarchy with Error Codes

Provides structured error types with unique error codes for:
- Persistence errors (corruption, recovery, backup)
- Domain errors (rule compilation, validation)
- Infrastructure errors (configuration, IO)

Each exception carries an error_code for machine-readable identification.
"""

import uuid
from typing import Optional, Dict, Any


class ErrorCode:
    """Centralized error code registry."""
    # Persistence errors (P1xxx)
    PERSISTENCE_CORRUPTION = "P1001"
    PERSISTENCE_WRITE_FAILED = "P1002"
    PERSISTENCE_READ_FAILED = "P1003"
    PERSISTENCE_RECOVERY_FAILED = "P1004"
    PERSISTENCE_BACKUP_FAILED = "P1005"
    PERSISTENCE_NOT_FOUND = "P1006"
    PERSISTENCE_SCHEMA_MIGRATION = "P1007"  # P1.1-3: Schema migration error
    PERSISTENCE_SCHEMA_INCOMPATIBLE = "P1008"  # P1.1-3: Unsupported schema version

    # Domain errors (D2xxx)
    DOMAIN_RULE_COMPILE = "D2001"
    DOMAIN_RULE_VALIDATION = "D2002"
    DOMAIN_RULE_EXECUTION = "D2003"
    DOMAIN_BASELINE_NOT_FOUND = "D2004"
    DOMAIN_VERSION_NOT_FOUND = "D2005"

    # Infrastructure errors (I3xxx)
    INFRA_CONFIGURATION = "I3001"
    INFRA_IO = "I3002"

    # Application errors (A4xxx)
    APP_PUBLISH_BLOCKED = "A4001"
    APP_PUBLISH_FAILED = "A4002"
    APP_ROLLBACK_FAILED = "A4003"

    # Unexpected errors
    UNEXPECTED = "X9000"


class CheckToolBaseError(Exception):
    """Base exception for all CheckTool errors."""
    def __init__(self, message: str, error_code: str = ErrorCode.UNEXPECTED, 
                 details: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.request_id = request_id
        super().__init__(f"[{error_code}] {message}")


class PersistenceError(CheckToolBaseError):
    """Base for all persistence-layer errors."""
    def __init__(self, message: str, error_code: str = ErrorCode.PERSISTENCE_READ_FAILED,
                 details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, error_code, details, **kwargs)


class PersistenceCorruptionError(PersistenceError):
    """JSON file is corrupted and cannot be parsed."""
    def __init__(self, file_path: str, original_error: str, **kwargs):
        super().__init__(
            f"Data file corrupted: {file_path}. Original error: {original_error}",
            error_code=ErrorCode.PERSISTENCE_CORRUPTION,
            details={"file_path": file_path, "original_error": original_error},
            **kwargs
        )
        self.file_path = file_path


class PersistenceRecoveryError(PersistenceError):
    """Corruption detected and recovery also failed."""
    def __init__(self, file_path: str, backup_path: Optional[str], reason: str, **kwargs):
        super().__init__(
            f"Data corruption recovery failed for {file_path}. Reason: {reason}",
            error_code=ErrorCode.PERSISTENCE_RECOVERY_FAILED,
            details={"file_path": file_path, "backup_path": backup_path, "reason": reason},
            **kwargs
        )
        self.file_path = file_path
        self.backup_path = backup_path


class PersistenceSchemaError(PersistenceError):
    """P1.1-3: Schema version incompatibility or migration failure."""
    def __init__(self, file_name: str, schema_version: Optional[str], current_version: str, reason: str, **kwargs):
        super().__init__(
            f"Schema incompatibility in {file_name}: data version={schema_version}, code version={current_version}. {reason}",
            error_code=ErrorCode.PERSISTENCE_SCHEMA_INCOMPATIBLE,
            details={"file_name": file_name, "data_schema_version": schema_version, "code_schema_version": current_version, "reason": reason},
            **kwargs
        )
        self.file_name = file_name
        self.data_schema_version = schema_version


class DomainError(CheckToolBaseError):
    """Base for all domain-layer errors."""
    def __init__(self, message: str, error_code: str = ErrorCode.DOMAIN_RULE_VALIDATION,
                 details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, error_code, details, **kwargs)


class ConfigurationError(CheckToolBaseError):
    """Configuration-related error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCode.INFRA_CONFIGURATION, **kwargs)


class TaskError(CheckToolBaseError):
    """Task-related error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCode.INFRA_IO, **kwargs)


class ValidationError(CheckToolBaseError):
    """Validation-related error."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCode.DOMAIN_RULE_VALIDATION, **kwargs)
