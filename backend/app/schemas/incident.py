from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["information", "warning", "average", "high", "disaster"]
IncidentStatus = Literal["open", "acknowledged", "in_progress", "pending_verification", "resolved", "reopened"]


class IncidentCreate(BaseModel):
    source: str = Field(default="manual", max_length=40)
    external_event_id: str | None = Field(default=None, max_length=128)
    host_name: str | None = Field(default=None, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    severity: Severity = "warning"
    status: IncidentStatus = "open"
    summary: str | None = None
    assigned_team: str | None = Field(default=None, max_length=120)


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    external_event_id: str | None
    host_name: str | None
    title: str
    severity: str
    status: str
    summary: str | None
    assigned_team: str | None
    detected_at: datetime
    created_at: datetime
    updated_at: datetime
