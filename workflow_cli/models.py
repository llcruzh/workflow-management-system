from dataclasses import dataclass
from typing import Literal

Status = Literal["todo", "in_progress", "done"]

@dataclass(frozen=True)
class Task:
    id: int
    title: str
    description: str
    status: Status
    priority: int
    created_at: str
    updated_at: str
