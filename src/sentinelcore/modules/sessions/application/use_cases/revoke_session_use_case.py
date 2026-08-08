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
    ) -> None:
        self._session_repository = session_repository
        self._clock = clock
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: RevokeSessionInput) -> None:
        session = await self._session_repository.get_by_id(input_data.session_id)
        if session is None or session.user_id != input_data.user_id:
            raise SessionNotFoundError(f"Session {input_data.session_id} not found")

        if not session.is_revoked:
            session.revoke(at=self._clock.now())
            await self._session_repository.update(session)
            await self._unit_of_work.commit()
