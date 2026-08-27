from dataclasses import dataclass


@dataclass(frozen=True)
class ListAuditLogsInput:
    limit: int = 100
    offset: int = 0
