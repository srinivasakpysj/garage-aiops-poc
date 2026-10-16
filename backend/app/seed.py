from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.database import Base,engine,SessionLocal
from app.models import Server,Incident,Activity
def seed():
    Base.metadata.create_all(bind=engine); db=SessionLocal()
    try:
        if not db.scalar(select(Server.id).limit(1)):
            for i in range(1,351):
                status="critical" if i<=3 else "warning" if i<=10 else "healthy"
                db.add(Server(hostname=f"SRV-PRD-{i:03d}",environment="Production" if i<281 else "Non-Production",team=["Application","Database","Infrastructure","Middleware"][i%4],status=status,cpu_percent=20+i%70,memory_percent=94 if i<=3 else 30+i%60,disk_percent=96 if i==2 else 30+i%65))
        if not db.scalar(select(Incident.id).limit(1)):
            now=datetime.now(timezone.utc)
            rows=[
            ("INC-0012","APP-PRD-023","Memory Usage","94%","90%","critical","Application","open","Memory usage exceeded configured threshold."),
            ("INC-0011","DB-PRD-011","Disk Space (/var)","96%","90%","critical","Database","open","Filesystem usage is critically high."),
            ("INC-0010","WEB-PRD-101","CPU Usage","92%","90%","high","Application","in_progress","CPU utilization remains high."),
            ("INC-0009","APP-PRD-045","Disk Space (/opt)","91%","90%","high","Application","open","Disk usage is above threshold."),
            ("INC-0008","MID-PRD-007","Memory Usage","93%","90%","high","Middleware","in_progress","Memory utilization is increasing."),
            ("INC-0007","DB-PRD-022","CPU Usage","88%","85%","warning","Database","acknowledged","CPU warning threshold exceeded."),
            ("INC-0006","APP-PRD-017","Disk Space (/log)","87%","85%","warning","Application","open","Log filesystem usage is high."),
            ("INC-0005","WEB-PRD-088","Memory Usage","86%","85%","warning","Application","open","Memory usage crossed warning threshold.")]
            for n,row in enumerate(rows):
                key,host,issue,val,threshold,sev,team,status,summary=row
                db.add(Incident(incident_key=key,source="demo",title=f"{issue} threshold exceeded",host_name=host,issue_type=issue,current_value=val,threshold=threshold,severity=sev,team=team,status=status,summary=summary,detected_at=now-timedelta(minutes=n*15)))
            for n,(key,event,detail) in enumerate([("INC-0012","New incident detected","INC-0012 - APP-PRD-023"),("INC-0007","Incident acknowledged","INC-0007 - DB-PRD-022"),("INC-0004","Incident resolved","INC-0004 - WEB-PRD-056"),("INC-0011","Rule-based analysis completed","INC-0011 - DB-PRD-011"),("INC-0009","Team notification queued","INC-0009 - APP-PRD-045")]):
                db.add(Activity(incident_key=key,event=event,detail=detail,occurred_at=now-timedelta(minutes=n*30)))
        db.commit(); print("Tables ready; demo data inserted if tables were empty.")
    finally: db.close()
if __name__=="__main__": seed()
