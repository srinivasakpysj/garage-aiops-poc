from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Boolean, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
def utcnow(): return datetime.now(timezone.utc)
class Team(Base):
    __tablename__="teams"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True,nullable=False)
    description:Mapped[str]=mapped_column(String(500),default="",nullable=False)
    email:Mapped[str|None]=mapped_column(String(255))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    servers:Mapped[list["Server"]]=relationship(back_populates="team")
    incidents:Mapped[list["Incident"]]=relationship(back_populates="team")
class Server(Base):
    __tablename__="servers"
    id:Mapped[int]=mapped_column(primary_key=True)
    hostname:Mapped[str]=mapped_column(String(120),unique=True,nullable=False,index=True)
    environment:Mapped[str]=mapped_column(String(30),default="Production")
    os_name:Mapped[str]=mapped_column(String(100),default="Linux")
    ip_address:Mapped[str|None]=mapped_column(String(45))
    team_id:Mapped[int|None]=mapped_column(ForeignKey("teams.id",ondelete="SET NULL"))
    status:Mapped[str]=mapped_column(String(24),default="Healthy",index=True)
    cpu_percent:Mapped[float]=mapped_column(Float,default=0)
    memory_percent:Mapped[float]=mapped_column(Float,default=0)
    disk_percent:Mapped[float]=mapped_column(Float,default=0)
    last_seen_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    team:Mapped[Team|None]=relationship(back_populates="servers")
class Incident(Base):
    __tablename__="incidents"
    __table_args__=(Index("ix_incidents_detected_at","detected_at"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    incident_key:Mapped[str]=mapped_column(String(32),unique=True,nullable=False,index=True)
    server_id:Mapped[int|None]=mapped_column(ForeignKey("servers.id",ondelete="SET NULL"))
    server_name:Mapped[str]=mapped_column(String(120),nullable=False)
    issue_type:Mapped[str]=mapped_column(String(80),nullable=False)
    current_value:Mapped[float]=mapped_column(Float,nullable=False)
    threshold:Mapped[float]=mapped_column(Float,nullable=False)
    severity:Mapped[str]=mapped_column(String(20),nullable=False,index=True)
    team_id:Mapped[int|None]=mapped_column(ForeignKey("teams.id",ondelete="SET NULL"))
    team_name:Mapped[str]=mapped_column(String(100),nullable=False)
    status:Mapped[str]=mapped_column(String(24),default="Open",index=True)
    summary:Mapped[str]=mapped_column(Text,default="")
    detected_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,onupdate=utcnow)
    team:Mapped[Team|None]=relationship(back_populates="incidents")
    events:Mapped[list["IncidentEvent"]]=relationship(back_populates="incident",cascade="all, delete-orphan")
    analyses:Mapped[list["AIAnalysis"]]=relationship(back_populates="incident",cascade="all, delete-orphan")
class IncidentEvent(Base):
    __tablename__="incident_events"
    id:Mapped[int]=mapped_column(primary_key=True)
    incident_id:Mapped[int]=mapped_column(ForeignKey("incidents.id",ondelete="CASCADE"),index=True)
    event_type:Mapped[str]=mapped_column(String(50),nullable=False)
    message:Mapped[str]=mapped_column(Text,nullable=False)
    actor:Mapped[str]=mapped_column(String(120),default="system")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    incident:Mapped[Incident]=relationship(back_populates="events")
class AIAnalysis(Base):
    __tablename__="ai_analyses"
    id:Mapped[int]=mapped_column(primary_key=True)
    incident_id:Mapped[int]=mapped_column(ForeignKey("incidents.id",ondelete="CASCADE"),index=True)
    provider:Mapped[str]=mapped_column(String(80),default="demo")
    model_name:Mapped[str]=mapped_column(String(120),default="demo-rules-v1")
    summary:Mapped[str]=mapped_column(Text,nullable=False)
    possible_causes:Mapped[list]=mapped_column(JSON,default=list)
    metrics:Mapped[dict]=mapped_column(JSON,default=dict)
    confidence:Mapped[float]=mapped_column(Float,default=0.5)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    incident:Mapped[Incident]=relationship(back_populates="analyses")
    recommendations:Mapped[list["Recommendation"]]=relationship(back_populates="analysis",cascade="all, delete-orphan")
class Recommendation(Base):
    __tablename__="recommendations"
    id:Mapped[int]=mapped_column(primary_key=True)
    analysis_id:Mapped[int]=mapped_column(ForeignKey("ai_analyses.id",ondelete="CASCADE"),index=True)
    title:Mapped[str]=mapped_column(String(200),nullable=False)
    description:Mapped[str]=mapped_column(Text,nullable=False)
    priority:Mapped[str]=mapped_column(String(20),default="Medium")
    status:Mapped[str]=mapped_column(String(24),default="Pending")
    requires_approval:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    analysis:Mapped[AIAnalysis]=relationship(back_populates="recommendations")
class Notification(Base):
    __tablename__="notifications"
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String(200),nullable=False)
    message:Mapped[str]=mapped_column(Text,nullable=False)
    severity:Mapped[str]=mapped_column(String(20),default="Info")
    is_read:Mapped[bool]=mapped_column(Boolean,default=False,index=True)
    incident_id:Mapped[int|None]=mapped_column(ForeignKey("incidents.id",ondelete="SET NULL"))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class AuditLog(Base):
    __tablename__="audit_logs"
    id:Mapped[int]=mapped_column(primary_key=True)
    actor:Mapped[str]=mapped_column(String(120),default="system")
    action:Mapped[str]=mapped_column(String(100),nullable=False)
    entity_type:Mapped[str]=mapped_column(String(80),nullable=False)
    entity_id:Mapped[str]=mapped_column(String(80),nullable=False)
    details:Mapped[dict]=mapped_column(JSON,default=dict)
    ip_address:Mapped[str|None]=mapped_column(String(45))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
