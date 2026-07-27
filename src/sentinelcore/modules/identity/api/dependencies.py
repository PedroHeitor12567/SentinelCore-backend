from typing import Annotated

from fastapi import Depends

from sentinelcore.core.dependencies import UoW
from sentinelcore.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from sentinelcore.modules.identity.application.use_cases.activate_user_use_case import ActivateUserUseCase
from sentinelcore.modules.identity.application.use_cases.create_user_use_case import CreateUserUseCase
from sentinelcore.modules.identity.application.use_cases.deactive_user_use_case import DeactiveUserUseCase
from sentinelcore.modules.identity.application.use_cases.get_user_use_case import GetUserUseCase
from sentinelcore.modules.identity.application.ports.password_hasher import PasswordHasher
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.infrastructure.repository.sql_alchemy_user_repository import SqlAlchemyUserRepository

_password_hasher = Argon2PasswordHasher()


def get_user_repository(unit_of_work: UoW) -> UserRepository:
    return SqlAlchemyUserRepository(unit_of_work.session)


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]


def get_create_user_use_case(
    user_repository: UserRepositoryDep,
    password_hasher: PasswordHasherDep,
    unit_of_work: UoW,
) -> CreateUserUseCase:
    return CreateUserUseCase(user_repository, password_hasher, unit_of_work)


def get_activate_user_use_case(
    user_repository: UserRepositoryDep,
    unit_of_work: UoW,
) -> ActivateUserUseCase:
    return ActivateUserUseCase(user_repository, unit_of_work)


def get_deactivate_user_use_case(
    user_repository: UserRepositoryDep,
    unit_of_work: UoW,
) -> DeactiveUserUseCase:
    return DeactiveUserUseCase(user_repository, unit_of_work)


def get_get_user_use_case(user_repository: UserRepositoryDep) -> GetUserUseCase:
    return GetUserUseCase(user_repository)


CreateUserUseCaseDep = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
ActivateUserUseCaseDep = Annotated[ActivateUserUseCase, Depends(get_activate_user_use_case)]
DeactivateUserUseCaseDep = Annotated[DeactiveUserUseCase, Depends(get_deactivate_user_use_case)]
GetUserUseCaseDep = Annotated[GetUserUseCase, Depends(get_get_user_use_case)]
