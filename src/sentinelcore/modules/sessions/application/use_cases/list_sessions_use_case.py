from sentinelcore.modules.authentication.application.ports.session_repository import (
    SessionRepository,
)
from sentinelcore.modules.sessions.application.dtos.input.list_sessions_input import (
    ListSessionsInput,
)
from sentinelcore.modules.sessions.application.dtos.output.session_output import SessionOutput
from sentinelcore.shared.application.use_case import UseCase


class ListSessionsUseCase(UseCase[ListSessionsInput, list[SessionOutput]]):
    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    async def execute(self, input_data: ListSessionsInput) -> list[SessionOutput]:
        sessions = await self._session_repository.list_by_user_id(input_data.user_id)
        return [SessionOutput.from_session(session) for session in sessions]
