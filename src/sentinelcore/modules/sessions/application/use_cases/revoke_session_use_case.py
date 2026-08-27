from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.session_repository import (
    SessionRepository,
)
from sentinelcore.modules.sessions.application.dtos.input.revoke_session_input import (
    RevokeSessionInput,
)
from sentinelcore.modules.sessions.domain.errors.session_not_found_error import SessionNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class RevokeSessionUseCase(UseCase[RevokeSessionInput, None]):
    def __init__(
        self,
        session_repository: SessionRepository,
        clock: Clock,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._session_repository = session_repository
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: RevokeSessionInput) -> None:
        session = await self._session_repository.get_by_id(input_data.session_id)
        if session is None or session.user_id != input_data.user_id:
            raise SessionNotFoundError(f"Session {input_data.session_id} not found")

        if not session.is_revoked:
            session.revoke(at=self._clock.now())
            await self._session_repository.update(session)

            await self._audit_log_repository.add(
                AuditLog.record(
                    event_type=AuditEventType.SESSION_REVOKED,
                    actor_id=input_data.user_id,
                    target_id=session.id,
                    metadata={"session_id": str(session.id)},
                )
            )

            await self._unit_of_work.commit()
