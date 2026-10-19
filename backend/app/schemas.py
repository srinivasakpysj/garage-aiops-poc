from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
class ORM(BaseModel): model_config=ConfigDict(from_attributes=True)
class TeamOut(ORM):
    id:int; name:str; description:str; email:str|None; created_at:datetime
class ServerOut(ORM):
    id:int; hostname:str; environment:str; os_name:str; ip_address:str|None; team_id:int|None; status:str; cpu_percent:float; memory_percent:float; disk_percent:float; last_seen_at:datetime|None; created_at:datetime
class IncidentOut(ORM):
    id:int; incident_key:str; server_id:int|None; server_name:str; issue_type:str; current_value:float; threshold:float; severity:str; team_id:int|None; team_name:str; status:str; summary:str; detected_at:datetime; updated_at:datetime
class IncidentStatusUpdate(BaseModel):
    status:Literal["Open","In Progress","Acknowledged","Resolved"]
    actor:str=Field(default="administrator",min_length=1,max_length=120)
    note:str|None=Field(default=None,max_length=1000)
class EventOut(ORM):
    id:int; incident_id:int; event_type:str; message:str; actor:str; created_at:datetime
class AnalysisOut(ORM):
    id:int; incident_id:int; provider:str; model_name:str; summary:str; possible_causes:list[Any]; metrics:dict[str,Any]; confidence:float; created_at:datetime
class RecommendationOut(ORM):
    id:int; analysis_id:int; title:str; description:str; priority:str; status:str; requires_approval:bool; created_at:datetime
class RecommendationUpdate(BaseModel):
    status:Literal["Pending","Accepted","Dismissed","Completed"]
    actor:str=Field(default="administrator",min_length=1,max_length=120)
class NotificationOut(ORM):
    id:int; title:str; message:str; severity:str; is_read:bool; incident_id:int|None; created_at:datetime
class AuditOut(ORM):
    id:int; actor:str; action:str; entity_type:str; entity_id:str; details:dict[str,Any]; ip_address:str|None; created_at:datetime
class PageMeta(BaseModel): total:int; limit:int; offset:int
class IncidentPage(BaseModel): items:list[IncidentOut]; meta:PageMeta
class Overview(BaseModel):
    total_servers:int; healthy:int; warning:int; critical:int; unreachable:int; health_percent:float; active_incidents:int
    server_health:list[dict[str,Any]]; incidents_by_type:list[dict[str,Any]]; incidents_by_team:list[dict[str,Any]]
    recent_activity:list[EventOut]; unread_notifications:int
