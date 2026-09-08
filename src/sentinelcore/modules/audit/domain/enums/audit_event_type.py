from enum import StrEnum


class AuditEventType(StrEnum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_REFRESHED = "token_refreshed"
    PASSWORD_CHANGED = "password_changed"
    PERMISSION_CHANGED = "permission_changed"
    USER_CREATED = "user_created"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    SESSION_REVOKED = "session_revoked"
    SENSITIVE_OPERATION = "sensitive_operation"
    ROLE_CREATED = "role_created"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_UNASSIGNED = "role_unassigned"
    PERMISSION_CREATED = "permission_created"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
