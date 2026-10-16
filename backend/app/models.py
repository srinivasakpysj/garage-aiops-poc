from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
def now(): return datetime.now(timezone.utc)
class Server(Base):
    __tablename__="servers"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    hostname: Mapped[str]=mapped_column(String(128),unique=True,index=True)
    environment: Mapped[str]=mapped_column(String(32),default="Production")
    team: Mapped[str]=mapped_column(String(64),default="Infrastructure")
    status: Mapped[str]=mapped_column(String(24),default="healthy",index=True)
    cpu_percent: Mapped[int]=mapped_column(Integer,default=20)
    memory_percent: Mapped[int]=mapped_column(Integer,default=35)
    disk_percent: Mapped[int]=mapped_column(Integer,default=40)
    last_seen: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Incident(Base):
    __tablename__="incidents"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    incident_key: Mapped[str]=mapped_column(String(32),unique=True,index=True)
    source: Mapped[str]=mapped_column(String(32),default="manual")
    title: Mapped[str]=mapped_column(String(240))
    host_name: Mapped[str]=mapped_column(String(128),index=True)
    issue_type: Mapped[str]=mapped_column(String(64),default="Other")
    current_value: Mapped[str]=mapped_column(String(32),default="N/A")
    threshold: Mapped[str]=mapped_column(String(32),default="N/A")
    severity: Mapped[str]=mapped_column(String(24),default="warning",index=True)
    team: Mapped[str]=mapped_column(String(64),default="Infrastructure")
    status: Mapped[str]=mapped_column(String(24),default="open",index=True)
    summary: Mapped[str]=mapped_column(Text,default="")
    detected_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class Activity(Base):
    __tablename__="activity"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    incident_key: Mapped[str]=mapped_column(String(32),default="")
    event: Mapped[str]=mapped_column(String(128))
    detail: Mapped[str]=mapped_column(String(240),default="")
    occurred_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
