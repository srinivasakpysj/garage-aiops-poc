from datetime import datetime,timezone,timedelta
from typing import Literal
from fastapi import FastAPI,Depends,HTTPException,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select,func,desc,or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .database import get_db
from .config import settings
from .models import Team,Server,Incident,IncidentEvent,AIAnalysis,Recommendation,Notification,AuditLog
from .schemas import TeamOut,ServerOut,IncidentOut,IncidentStatusUpdate,EventOut,AnalysisOut,RecommendationOut,RecommendationUpdate,NotificationOut,AuditOut,IncidentPage,Overview
app=FastAPI(title="GARAGE AIOps API",version="2.0.0",description="Persistent infrastructure operations REST API")
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=False,allow_methods=["GET","POST","PATCH","OPTIONS"],allow_headers=["*"])
@app.get("/health/live",tags=["health"])
def live():return {"status":"alive","timestamp":datetime.now(timezone.utc)}
@app.get("/health/ready",tags=["health"])
def ready(db:Session=Depends(get_db)):
    try:db.execute(select(1));return {"status":"ready","database":"connected"}
    except SQLAlchemyError as e:raise HTTPException(503,"Database is not ready") from e
@app.get("/api/v1/dashboard/overview",response_model=Overview,tags=["dashboard"])
def overview(window:Literal["1h","6h","24h","7d","30d"]="24h",db:Session=Depends(get_db)):
    servers=db.scalars(select(Server)).all();active=db.scalars(select(Incident).where(Incident.status!="Resolved")).all()
    counts={n:sum(s.status==n for s in servers) for n in ["Healthy","Warning","Critical","Unreachable"]}
    delta={"1h":timedelta(hours=1),"6h":timedelta(hours=6),"24h":timedelta(hours=24),"7d":timedelta(days=7),"30d":timedelta(days=30)}[window]
    events=db.scalars(select(IncidentEvent).where(IncidentEvent.created_at>=datetime.now(timezone.utc)-delta).order_by(desc(IncidentEvent.created_at)).limit(8)).all()
    bytype=[]
    for name in ["CPU Usage","Memory Usage","Disk Space","Other"]:
        vals=[i for i in active if (name=="Other" and i.issue_type not in ["CPU Usage","Memory Usage"] and not i.issue_type.startswith("Disk Space")) or (name=="Disk Space" and i.issue_type.startswith("Disk Space")) or i.issue_type==name]
        bytype.append({"type":name,"critical":sum(i.severity=="Critical" for i in vals),"warning":sum(i.severity in ["Warning","High"] for i in vals),"total":len(vals)})
    teams=db.scalars(select(Team).order_by(Team.name)).all()
    unread=db.scalar(select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))) or 0
    total=len(servers)
    return {"total_servers":total,"healthy":counts["Healthy"],"warning":counts["Warning"],"critical":counts["Critical"],"unreachable":counts["Unreachable"],"health_percent":round(counts["Healthy"]/total*100,1) if total else 0,"active_incidents":len(active),"server_health":[{"name":k,"value":v} for k,v in counts.items()],"incidents_by_type":bytype,"incidents_by_team":[{"team":t.name,"value":sum(i.team_id==t.id for i in active)} for t in teams],"recent_activity":events,"unread_notifications":unread}
@app.get("/api/v1/servers",response_model=list[ServerOut],tags=["servers"])
def servers(q:str|None=None,status:str|None=None,environment:str|None=None,limit:int=Query(100,ge=1,le=500),offset:int=Query(0,ge=0),db:Session=Depends(get_db)):
    st=select(Server)
    if q:st=st.where(or_(Server.hostname.ilike(f"%{q.strip()}%"),Server.os_name.ilike(f"%{q.strip()}%")))
    if status:st=st.where(Server.status==status)
    if environment:st=st.where(Server.environment==environment)
    return db.scalars(st.order_by(Server.hostname).offset(offset).limit(limit)).all()
@app.get("/api/v1/servers/{server_id}",response_model=ServerOut,tags=["servers"])
def server(server_id:int,db:Session=Depends(get_db)):
    x=db.get(Server,server_id)
    if not x:raise HTTPException(404,"Server not found")
    return x
@app.get("/api/v1/teams",response_model=list[TeamOut],tags=["teams"])
def teams(db:Session=Depends(get_db)):return db.scalars(select(Team).order_by(Team.name)).all()
@app.get("/api/v1/teams/{team_id}",response_model=TeamOut,tags=["teams"])
def team(team_id:int,db:Session=Depends(get_db)):
    x=db.get(Team,team_id)
    if not x:raise HTTPException(404,"Team not found")
    return x
@app.get("/api/v1/incidents",response_model=IncidentPage,tags=["incidents"])
def incidents(q:str|None=None,severity:str|None=None,status:str|None=None,team_id:int|None=None,window:Literal["1h","6h","24h","7d","30d","all"]="all",limit:int=Query(100,ge=1,le=500),offset:int=Query(0,ge=0),db:Session=Depends(get_db)):
    st=select(Incident)
    if q:
        term=f"%{q.strip()}%";st=st.where(or_(Incident.incident_key.ilike(term),Incident.server_name.ilike(term),Incident.issue_type.ilike(term),Incident.team_name.ilike(term)))
    if severity:st=st.where(Incident.severity==severity)
    if status:st=st.where(Incident.status==status)
    if team_id:st=st.where(Incident.team_id==team_id)
    if window!="all":
        d={"1h":timedelta(hours=1),"6h":timedelta(hours=6),"24h":timedelta(hours=24),"7d":timedelta(days=7),"30d":timedelta(days=30)}[window]
        st=st.where(Incident.detected_at>=datetime.now(timezone.utc)-d)
    total=db.scalar(select(func.count()).select_from(st.subquery())) or 0
    return {"items":db.scalars(st.order_by(desc(Incident.detected_at)).offset(offset).limit(limit)).all(),"meta":{"total":total,"limit":limit,"offset":offset}}
@app.get("/api/v1/incidents/{incident_id}",response_model=IncidentOut,tags=["incidents"])
def incident(incident_id:int,db:Session=Depends(get_db)):
    x=db.get(Incident,incident_id)
    if not x:raise HTTPException(404,"Incident not found")
    return x
@app.get("/api/v1/incidents/{incident_id}/events",response_model=list[EventOut],tags=["incidents"])
def events(incident_id:int,db:Session=Depends(get_db)):
    if not db.get(Incident,incident_id):raise HTTPException(404,"Incident not found")
    return db.scalars(select(IncidentEvent).where(IncidentEvent.incident_id==incident_id).order_by(desc(IncidentEvent.created_at))).all()
@app.patch("/api/v1/incidents/{incident_id}/status",response_model=IncidentOut,tags=["incidents"])
def incident_status(incident_id:int,payload:IncidentStatusUpdate,request:Request,db:Session=Depends(get_db)):
    x=db.get(Incident,incident_id)
    if not x:raise HTTPException(404,"Incident not found")
    old=x.status
    if old==payload.status:return x
    x.status=payload.status;x.updated_at=datetime.now(timezone.utc)
    db.add(IncidentEvent(incident_id=x.id,event_type="status_changed",message=payload.note or f"Status changed from {old} to {payload.status}",actor=payload.actor))
    db.add(AuditLog(actor=payload.actor,action="incident.status_changed",entity_type="incident",entity_id=str(x.id),details={"from":old,"to":payload.status,"incident_key":x.incident_key},ip_address=request.client.host if request.client else None))
    db.commit();db.refresh(x);return x
@app.get("/api/v1/ai-analyses",response_model=list[AnalysisOut],tags=["AI analysis"])
def analyses(incident_id:int|None=None,limit:int=Query(50,ge=1,le=200),db:Session=Depends(get_db)):
    st=select(AIAnalysis).order_by(desc(AIAnalysis.created_at)).limit(limit)
    if incident_id:st=select(AIAnalysis).where(AIAnalysis.incident_id==incident_id).order_by(desc(AIAnalysis.created_at)).limit(limit)
    return db.scalars(st).all()
@app.get("/api/v1/ai-analyses/{analysis_id}",response_model=AnalysisOut,tags=["AI analysis"])
def analysis(analysis_id:int,db:Session=Depends(get_db)):
    x=db.get(AIAnalysis,analysis_id)
    if not x:raise HTTPException(404,"Analysis not found")
    return x
@app.get("/api/v1/recommendations",response_model=list[RecommendationOut],tags=["recommendations"])
def recommendations(status:str|None=None,limit:int=Query(100,ge=1,le=500),db:Session=Depends(get_db)):
    st=select(Recommendation).order_by(desc(Recommendation.created_at)).limit(limit)
    if status:st=select(Recommendation).where(Recommendation.status==status).order_by(desc(Recommendation.created_at)).limit(limit)
    return db.scalars(st).all()
@app.patch("/api/v1/recommendations/{recommendation_id}/status",response_model=RecommendationOut,tags=["recommendations"])
def recommendation_status(recommendation_id:int,payload:RecommendationUpdate,request:Request,db:Session=Depends(get_db)):
    x=db.get(Recommendation,recommendation_id)
    if not x:raise HTTPException(404,"Recommendation not found")
    old=x.status;x.status=payload.status
    db.add(AuditLog(actor=payload.actor,action="recommendation.status_changed",entity_type="recommendation",entity_id=str(x.id),details={"from":old,"to":x.status},ip_address=request.client.host if request.client else None))
    db.commit();db.refresh(x);return x
@app.get("/api/v1/notifications",response_model=list[NotificationOut],tags=["notifications"])
def notifications(unread_only:bool=False,limit:int=Query(100,ge=1,le=500),db:Session=Depends(get_db)):
    st=select(Notification).order_by(desc(Notification.created_at)).limit(limit)
    if unread_only:st=select(Notification).where(Notification.is_read.is_(False)).order_by(desc(Notification.created_at)).limit(limit)
    return db.scalars(st).all()
@app.patch("/api/v1/notifications/{notification_id}/read",response_model=NotificationOut,tags=["notifications"])
def read_notification(notification_id:int,request:Request,db:Session=Depends(get_db)):
    x=db.get(Notification,notification_id)
    if not x:raise HTTPException(404,"Notification not found")
    x.is_read=True;db.add(AuditLog(actor="administrator",action="notification.read",entity_type="notification",entity_id=str(x.id),details={"title":x.title},ip_address=request.client.host if request.client else None))
    db.commit();db.refresh(x);return x
@app.get("/api/v1/audit-logs",response_model=list[AuditOut],tags=["audit"])
def audit_logs(entity_type:str|None=None,limit:int=Query(100,ge=1,le=500),db:Session=Depends(get_db)):
    st=select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    if entity_type:st=select(AuditLog).where(AuditLog.entity_type==entity_type).order_by(desc(AuditLog.created_at)).limit(limit)
    return db.scalars(st).all()
@app.get("/api/v1/integrations",tags=["integrations"])
def integrations():
    return {"items":[{"name":"Zabbix","status":"Not configured","mode":"demo","detail":"Configure the Zabbix API and credentials for live telemetry."},{"name":"PostgreSQL","status":"Configured","mode":"live","detail":"Database connection is managed by DATABASE_URL."},{"name":"AI Service","status":"Not configured","mode":"demo","detail":"Stored demo analysis; no external model is connected."},{"name":"Microsoft Teams","status":"Not configured","mode":"demo","detail":"Configure an approved Teams integration."},{"name":"Email Service","status":"Not configured","mode":"demo","detail":"Configure SMTP or a managed email provider."}]}
