from datetime import datetime,timezone
from app.main import app
from app.database import get_db
from app.models import Team,Server,Incident,IncidentEvent,AIAnalysis,Recommendation,Notification
def seed_test():
    db=next(app.dependency_overrides[get_db]())
    t=Team(name="App Test",description="test",email=None);db.add(t);db.flush()
    s=Server(hostname="APP-TEST-001",environment="Test",os_name="Linux",team=t,status="Critical",cpu_percent=40,memory_percent=94,disk_percent=50,last_seen_at=datetime.now(timezone.utc));db.add(s);db.flush()
    i=Incident(incident_key="INC-TEST-1",server=s,server_name=s.hostname,issue_type="Memory Usage",current_value=94,threshold=90,severity="Critical",team=t,team_name=t.name,status="Open",summary="Memory threshold breached");db.add(i);db.flush()
    db.add(IncidentEvent(incident=i,event_type="detected",message="Test detected",actor="test"))
    a=AIAnalysis(incident=i,provider="test",model_name="test-v1",summary="Test analysis",possible_causes=["leak"],metrics={"memory_percent":94},confidence=.9);db.add(a);db.flush()
    db.add(Recommendation(analysis=a,title="Inspect process",description="Inspect memory",priority="High",status="Pending",requires_approval=True))
    db.add(Notification(title="Test notification",message="Test",severity="Critical",incident_id=i.id,is_read=False));db.commit()
    result=i.id;db.close();return result
def test_health(client):
    assert client.get("/health/live").status_code==200
    assert client.get("/health/ready").json()["database"]=="connected"
def test_dashboard_and_filter(client):
    seed_test()
    data=client.get("/api/v1/dashboard/overview").json()
    assert data["total_servers"]==1 and data["critical"]==1 and data["active_incidents"]==1
    page=client.get("/api/v1/incidents?q=INC-TEST&severity=Critical").json()
    assert page["meta"]["total"]==1
def test_status_events_audit_and_validation(client):
    iid=seed_test()
    r=client.patch(f"/api/v1/incidents/{iid}/status",json={"status":"Acknowledged","actor":"tester","note":"reviewed"})
    assert r.status_code==200 and r.json()["status"]=="Acknowledged"
    assert len(client.get(f"/api/v1/incidents/{iid}/events").json())==2
    assert len(client.get("/api/v1/audit-logs?entity_type=incident").json())==1
    assert client.patch(f"/api/v1/incidents/{iid}/status",json={"status":"banana"}).status_code==422
    assert client.get("/api/v1/incidents/99999").status_code==404
def test_ai_recommendations_notifications(client):
    seed_test()
    assert client.get("/api/v1/ai-analyses").json()[0]["summary"]=="Test analysis"
    rec=client.get("/api/v1/recommendations").json()[0]
    assert client.patch(f"/api/v1/recommendations/{rec['id']}/status",json={"status":"Accepted"}).status_code==200
    note=client.get("/api/v1/notifications?unread_only=true").json()[0]
    assert client.patch(f"/api/v1/notifications/{note['id']}/read").status_code==200
