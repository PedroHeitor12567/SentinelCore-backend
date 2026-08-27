from datetime import UTC, datetime
from uuid import uuid4

from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType


def test_record_creates_audit_log_with_defaults() -> None:
    audit_log = AuditLog.record(event_type=AuditEventType.LOGIN_SUCCESS)

    assert audit_log.event_type == AuditEventType.LOGIN_SUCCESS
    assert audit_log.actor_id is None
    assert audit_log.target_id is None
    assert audit_log.ip_address is None
    assert audit_log.user_agent is None
    assert audit_log.metadata == {}
    assert isinstance(audit_log.created_at, datetime)
    assert audit_log.created_at.tzinfo == UTC


def test_record_creates_audit_log_with_all_fields() -> None:
    actor_id = uuid4()
    target_id = uuid4()

    audit_log = AuditLog.record(
        event_type=AuditEventType.PERMISSION_CHANGED,
        actor_id=actor_id,
        target_id=target_id,
        ip_address="203.0.113.1",
        user_agent="curl/8.0",
        metadata={"action": "role_assigned"},
    )

    assert audit_log.actor_id == actor_id
    assert audit_log.target_id == target_id
    assert audit_log.ip_address == "203.0.113.1"
    assert audit_log.user_agent == "curl/8.0"
    assert audit_log.metadata == {"action": "role_assigned"}


def test_each_record_call_generates_unique_id() -> None:
    first = AuditLog.record(event_type=AuditEventType.LOGIN_SUCCESS)
    second = AuditLog.record(event_type=AuditEventType.LOGIN_SUCCESS)

    assert first.id != second.id
