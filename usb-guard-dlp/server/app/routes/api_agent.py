from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Fixed Imports:
from server.app.database import get_db
from server.app.models import AgentNode, WhitelistedUSB, AuditLog
from server.app.schemas import AgentHeartbeat, PolicyResponse, LogEntryCreate

router = APIRouter(prefix="/api/v1/agent", tags=["Agent Operations"])

@router.post("/heartbeat", response_model=PolicyResponse)
def handle_heartbeat(payload: AgentHeartbeat, db: Session = Depends(get_db)):
    """Receives heartbeat from Agent PC and returns assigned USB Enforcement Policy."""
    agent = db.query(AgentNode).filter(AgentNode.hwid == payload.hwid).first()
    
    if not agent:
        # Register new computer automatically
        agent = AgentNode(
            hwid=payload.hwid,
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            is_usb_blocked=False,
            last_seen=datetime.utcnow(),
            status="ONLINE"
        )
        db.add(agent)
    else:
        # Update connection details
        agent.hostname = payload.hostname
        agent.ip_address = payload.ip_address
        agent.last_seen = datetime.utcnow()
        agent.status = "ONLINE"
    
    db.commit()
    db.refresh(agent)

    # Fetch global whitelist serials
    whitelisted = db.query(WhitelistedUSB.serial_number).all()
    whitelist_list = [item[0] for item in whitelisted]

    return PolicyResponse(
        is_usb_blocked=agent.is_usb_blocked,
        is_read_only=agent.is_read_only,
        whitelisted_serials=whitelist_list
    )

@router.post("/log")
def submit_audit_log(payload: LogEntryCreate, db: Session = Depends(get_db)):
    """Receives security alert/audit events from endpoints."""
    log_entry = AuditLog(
        hwid=payload.hwid,
        event_type=payload.event_type,
        details=payload.details
    )
    db.add(log_entry)
    db.commit()
    return {"status": "success"}