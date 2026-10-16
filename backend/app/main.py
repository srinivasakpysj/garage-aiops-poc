from datetime import datetime,timezone
from fastapi import FastAPI,Depends,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base,engine,get_db
from app.models import Server,Incident,Activity
app=FastAPI(title="Garage AIOps API",version="0.2.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)
class IncidentCreate(BaseModel):
    source:str="manual"; title:str=Field(min_length=3,max_length=240); host_name:str
    issue_type:str="Other"; current_value:str="N/A"; threshold:str="N/A"; severity:str="warning"; team:str="Infrastructure"; status:str="open"; summary:str=""
class IncidentUpdate(BaseModel):
    status:str|None=None; team:str|None=None; summary:str|None=None
def as_incident(i):
    return {"incident_key":i.incident_key,"source":i.source,"title":i.title,"host_name":i.host_name,"issue_type":i.issue_type,"current_value":i.current_value,"threshold":i.threshold,"severity":i.severity,"team":i.team,"status":i.status,"summary":i.summary,"detected_at":i.detected_at,"updated_at":i.updated_at}
@app.get("/health")
def health(): return {"status":"ok","service":"garage-aiops-api","version":app.version}
@app.get("/api/v1/dashboard/summary")
def summary(db:Session=Depends(get_db)):
    count=lambda model,condition=None: db.scalar(select(func.count(model.id)).where(condition) if condition is not None else select(func.count(model.id))) or 0
    total=count(Server); healthy=count(Server,Server.status=="healthy"); warning=count(Server,Server.status=="warning"); critical=count(Server,Server.status=="critical"); unreachable=count(Server,Server.status=="unreachable")
    active=db.scalars(select(Incident).where(Incident.status!="resolved").order_by(Incident.detected_at.desc())).all()
    typ={}; teams={}
    for i in active:
        typ.setdefault(i.issue_type,{"critical":0,"warning":0,"total":0})
        typ[i.issue_type]["critical" if i.severity=="critical" else "warning"]+=1; typ[i.issue_type]["total"]+=1
        teams[i.team]=teams.get(i.team,0)+1
    return {"total_servers":total,"healthy":healthy,"warning":warning,"critical":critical,"unreachable":unreachable,"active_incidents":len(active),"health_percent":round(healthy*100/total,1) if total else 0,"incidents_by_type":[{"type":k,**v} for k,v in typ.items()],"incidents_by_team":[{"team":k,"count":v} for k,v in teams.items()],"data_mode":"demo_seeded" if any(i.source=="demo" for i in active) else "database"}
@app.get("/api/v1/servers")
def servers(limit:int=Query(50,ge=1,le=500),status:str|None=None,db:Session=Depends(get_db)):
    q=select(Server).order_by(Server.hostname).limit(limit)
    if status: q=select(Server).where(Server.status==status).order_by(Server.hostname).limit(limit)
    return [{"id":s.id,"hostname":s.hostname,"environment":s.environment,"team":s.team,"status":s.status,"cpu_percent":s.cpu_percent,"memory_percent":s.memory_percent,"disk_percent":s.disk_percent,"last_seen":s.last_seen} for s in db.scalars(q).all()]
@app.get("/api/v1/incidents")
def incidents(limit:int=Query(50,ge=1,le=200),status:str|None=None,db:Session=Depends(get_db)):
    q=select(Incident).order_by(Incident.detected_at.desc()).limit(limit)
    if status: q=select(Incident).where(Incident.status==status).order_by(Incident.detected_at.desc()).limit(limit)
    return [as_incident(i) for i in db.scalars(q).all()]
@app.post("/api/v1/incidents",status_code=201)
def create_incident(p:IncidentCreate,db:Session=Depends(get_db)):
    n=(db.scalar(select(func.count(Incident.id))) or 0)+1
    i=Incident(incident_key=f"INC-POC-{n:04d}",**p.model_dump()); db.add(i); db.flush()
    db.add(Activity(incident_key=i.incident_key,event="Incident created",detail=f"{i.incident_key} - {i.host_name}")); db.commit(); db.refresh(i); return as_incident(i)
@app.patch("/api/v1/incidents/{key}")
def update_incident(key:str,p:IncidentUpdate,db:Session=Depends(get_db)):
    i=db.scalar(select(Incident).where(Incident.incident_key==key))
    if not i: raise HTTPException(404,"Incident not found")
    for k,v in p.model_dump(exclude_unset=True).items():
        if v is not None: setattr(i,k,v)
    i.updated_at=datetime.now(timezone.utc); db.add(Activity(incident_key=key,event="Incident updated",detail=f"{key} status: {i.status}")); db.commit(); db.refresh(i); return as_incident(i)
@app.get("/api/v1/activity")
def activity(limit:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    return [{"id":a.id,"incident_key":a.incident_key,"event":a.event,"detail":a.detail,"occurred_at":a.occurred_at} for a in db.scalars(select(Activity).order_by(Activity.occurred_at.desc()).limit(limit)).all()]
@app.get("/api/v1/insights/current")
def insight(db:Session=Depends(get_db)):
    i=db.scalar(select(Incident).where(Incident.status!="resolved",Incident.severity=="critical").order_by(Incident.detected_at.desc()))
    if not i:return {"available":False,"mode":"rule_based_poc","title":"No critical incident","summary":"No open critical incidents recorded.","possible_causes":[],"recommended_actions":[]}
    return {"available":True,"mode":"rule_based_poc","incident_key":i.incident_key,"host_name":i.host_name,"title":i.title,"summary":i.summary,"possible_causes":["Resource consumption increased","Recent application or configuration change","Workload or connection growth"],"recommended_actions":["Inspect top resource-consuming processes","Review application and system logs","Compare current metrics with the previous 30 minutes","Validate recent changes before considering a controlled restart"],"safety_note":"Advisory only; no automated remediation is executed."}
