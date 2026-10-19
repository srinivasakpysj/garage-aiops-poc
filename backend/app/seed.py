from datetime import datetime,timedelta,timezone
from sqlalchemy import select,func
from .database import SessionLocal
from .models import Team,Server,Incident,IncidentEvent,AIAnalysis,Recommendation,Notification
from .config import settings
TEAM_NAMES=["Application Team","Database Team","Infrastructure Team","Middleware Team","Others"]
ROWS=[
("INC-0012","APP-PRD-023","Memory Usage",94,90,"Critical","Application Team","Open","Memory usage crossed the configured threshold and rose steadily."),
("INC-0011","DB-PRD-011","Disk Space (/var)",96,90,"Critical","Database Team","Open","Filesystem utilization is critically high."),
("INC-0010","WEB-PRD-101","CPU Usage",92,90,"High","Application Team","In Progress","CPU utilization remains above threshold."),
("INC-0009","APP-PRD-045","Disk Space (/opt)",91,90,"High","Application Team","Open","Application volume is nearing capacity."),
("INC-0008","MID-PRD-007","Memory Usage",93,90,"High","Middleware Team","In Progress","Memory pressure detected on middleware host."),
("INC-0007","DB-PRD-022","CPU Usage",88,85,"Warning","Database Team","Acknowledged","CPU usage exceeded warning threshold."),
("INC-0006","APP-PRD-017","Disk Space (/log)",87,85,"Warning","Application Team","Open","Log partition utilization is elevated."),
("INC-0005","WEB-PRD-088","Memory Usage",86,85,"Warning","Application Team","Open","Memory usage is elevated."),
("INC-0004","WEB-PRD-056","CPU Usage",72,85,"Resolved","Application Team","Resolved","CPU returned to normal after service recovery."),
("INC-0003","MID-PRD-003","Disk Space (/data)",82,85,"Warning","Middleware Team","Acknowledged","Data partition is trending upward."),
("INC-0002","DB-PRD-019","Memory Usage",84,85,"Warning","Database Team","In Progress","Memory is approaching threshold."),
("INC-0001","APP-PRD-006","CPU Usage",79,85,"Warning","Application Team","Open","Short CPU spike observed.")]
def seed():
    if not settings.seed_demo_data:return
    db=SessionLocal()
    try:
        if db.scalar(select(func.count()).select_from(Team)):return
        teams={n:Team(name=n,description=f"{n} service ownership",email=None) for n in TEAM_NAMES}
        db.add_all(teams.values());db.flush();now=datetime.now(timezone.utc);servers={}
        required_hosts=list(dict.fromkeys(row[1] for row in ROWS))
        hostnames=required_hosts[:]
        n=1
        while len(hostnames)<350:
            prefix=["APP","DB","WEB","MID","INFRA"][(n-1)%5]
            candidate=f"{prefix}-PRD-{n:03d}"
            if candidate not in hostnames: hostnames.append(candidate)
            n+=1
        for idx,hostname in enumerate(hostnames):
            n=idx+1
            status="Healthy" if n<=340 else "Warning" if n<=347 else "Critical"
            s=Server(hostname=hostname,environment="Production",os_name="RHEL 9" if n%3 else "Amazon Linux 2023",ip_address=f"10.20.{(n-1)//250}.{(n-1)%250+1}",team=teams[TEAM_NAMES[(n-1)%5]],status=status,cpu_percent=float(35+(n*7)%58),memory_percent=float(30+(n*11)%65),disk_percent=float(25+(n*13)%72),last_seen_at=now-timedelta(minutes=n%4))
            db.add(s);servers[hostname]=s
        db.flush();incidents=[]
        for idx,row in enumerate(ROWS):
            key,host,issue,val,thr,sev,teamname,status,summary=row
            inc=Incident(incident_key=key,server=servers[host],server_name=host,issue_type=issue,current_value=val,threshold=thr,severity=sev,team=teams[teamname],team_name=teamname,status=status,summary=summary,detected_at=now-timedelta(minutes=[5,10,17,27,35,47,62,77,95,110,135,160][idx]))
            db.add(inc);incidents.append(inc)
        db.flush()
        for inc in incidents:db.add(IncidentEvent(incident=inc,event_type="detected",message=inc.summary,actor="demo-seeder",created_at=inc.detected_at))
        inc=incidents[0]
        a=AIAnalysis(incident=inc,provider="demo",model_name="demo-rules-v1",summary="Memory usage has reached 94%, above the configured threshold of 90%. Usage has increased steadily over the last 30 minutes.",possible_causes=["Memory leak in application process","High number of active connections","Large cache or temporary file usage","Insufficient memory for current workload"],metrics={"memory_percent":94,"cpu_percent":68,"disk_percent":71,"trend":"increasing"},confidence=.72)
        db.add(a);db.flush()
        for title,desc,priority in [("Inspect top memory consumers","Capture process-level memory metrics and identify unexpected growth.","High"),("Review application logs","Check for memory leak signatures and recent errors.","High"),("Correlate recent deployments","Compare release events against the start of the memory increase.","Medium"),("Escalate before restart","Obtain service-owner approval before remediation.","Medium")]:
            db.add(Recommendation(analysis=a,title=title,description=desc,priority=priority,status="Pending",requires_approval=True))
        for inc in incidents[:5]:db.add(Notification(title=f"{inc.severity} incident: {inc.incident_key}",message=f"{inc.server_name}: {inc.issue_type} is {inc.current_value}% (threshold {inc.threshold}%).",severity=inc.severity,incident_id=inc.id,is_read=False))
        db.commit()
    finally:db.close()
if __name__=="__main__":seed()
