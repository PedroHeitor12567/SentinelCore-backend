from uuid import UUID

from fastapi import APIRouter
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import CurrentUserId
from sentinelcore.modules.sessions.api.dependencies import (
    ListSessionsUseCaseDep,
    RevokeSessionUseCaseDep,
)
from sentinelcore.modules.sessions.api.schemas.session_response import SessionResponse
from sentinelcore.modules.sessions.application.dtos.input.list_sessions_input import (
    ListSessionsInput,
)
from sentinelcore.modules.sessions.application.dtos.input.revoke_session_input import (
    RevokeSessionInput,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    current_user_id: CurrentUserId, use_case: ListSessionsUseCaseDep
) -> list[SessionResponse]:
    outputs = await use_case.execute(ListSessionsInput(user_id=current_user_id))
    return [SessionResponse.from_output(output) for output in outputs]


@router.post("/{session_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: UUID, current_user_id: CurrentUserId, use_case: RevokeSessionUseCaseDep
) -> None:
    await use_case.execute(RevokeSessionInput(user_id=current_user_id, session_id=session_id))
