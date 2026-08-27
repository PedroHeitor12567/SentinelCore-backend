from enum import StrEnum


class AuditEventType(StrEnum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PASSWORD_CHANGED = "password_changed"
    PERMISSION_CHANGED = "permission_changed"
    USER_CREATED = "user_created"
    SESSION_REVOKED = "session_revoked"
    SENSITIVE_OPERATION = "sensitive_operation"
