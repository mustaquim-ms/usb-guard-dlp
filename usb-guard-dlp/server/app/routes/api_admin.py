import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from server.app.database import get_db
from server.app.models import User, AgentNode, WhitelistedUSB, AuditLog
from server.app.schemas import USBBlockToggleRequest, WhitelistUSBRequest

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Control"])

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total": db.query(AgentNode).count(),
        "blocked": db.query(AgentNode).filter(AgentNode.is_usb_blocked == True).count(),
        "alerts": db.query(AuditLog).count(),
        "whitelist": db.query(WhitelistedUSB).count()
    }

@router.get("/agents")
def get_all_agents(db: Session = Depends(get_db)):
    return db.query(AgentNode).all()

@router.get("/whitelist/list")
def get_whitelist(db: Session = Depends(get_db)):
    return db.query(WhitelistedUSB).order_by(WhitelistedUSB.added_at.desc()).all()

@router.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.hashed_password != password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {
        "status": "success", 
        "user": {
            "name": user.full_name or user.username, 
            "username": user.username,
            "uid": user.user_id_code or "ADM-01"
        }
    }

@router.post("/profile/update")
async def update_profile(name: str = Form(...), uid: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == "admin").first()
    if user:
        user.full_name = name
        user.user_id_code = uid
        db.commit()
        return {"status": "success", "name": name, "uid": uid}
    raise HTTPException(status_code=404, detail="Admin user not found")

@router.post("/users/create")
async def create_user(name: str = Form(...), uid: str = Form(...), user: str = Form(...), pw: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(full_name=name, user_id_code=uid, username=user, hashed_password=pw)
    db.add(new_user)
    db.commit()
    return {"status": "success"}

@router.get("/users/list")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/fleet/add")
async def add_fleet_manual(host: str = Form(...), ip: str = Form(...), owner: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(AgentNode).filter(AgentNode.ip_address == ip).first()
    if existing:
        existing.hostname = host
        existing.device_username = owner
    else:
        node = AgentNode(hwid=f"MANUAL-{ip}", hostname=host, ip_address=ip, device_username=owner, status="PENDING")
        db.add(node)
    db.commit()
    return {"status": "success"}

@router.post("/fleet/upload-csv")
async def upload_fleet_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode('utf-8-sig') # Handle BOM if saved from Excel
    reader = csv.DictReader(io.StringIO(decoded))
    
    added_count = 0
    for row in reader:
        if 'ip_address' in row and 'hostname' in row:
            ip = row['ip_address'].strip()
            existing = db.query(AgentNode).filter(AgentNode.ip_address == ip).first()
            if not existing:
                new_node = AgentNode(
                    hwid=f"CSV-{ip}",
                    hostname=row['hostname'].strip(),
                    ip_address=ip,
                    device_username=row.get('owner', 'Unknown User').strip(),
                    status="PENDING"
                )
                db.add(new_node)
                added_count += 1
    db.commit()
    return {"status": "success", "added": added_count}

@router.post("/whitelist/add")
async def add_whitelist_manual(serial: str = Form(...), owner: str = Form(...), db: Session = Depends(get_db)):
    clean_serial = serial.strip().upper()
    existing = db.query(WhitelistedUSB).filter(WhitelistedUSB.serial_number == clean_serial).first()
    if not existing:
        entry = WhitelistedUSB(serial_number=clean_serial, device_owner=owner.strip())
        db.add(entry)
        db.commit()
    return {"status": "success"}

@router.post("/whitelist/upload-csv")
async def upload_whitelist_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    added_count = 0
    for row in reader:
        if 'serial' in row:
            clean_serial = row['serial'].strip().upper()
            existing = db.query(WhitelistedUSB).filter(WhitelistedUSB.serial_number == clean_serial).first()
            if not existing:
                entry = WhitelistedUSB(
                    serial_number=clean_serial,
                    device_owner=row.get('owner', 'Approved USB Drive').strip()
                )
                db.add(entry)
                added_count += 1
    db.commit()
    return {"status": "success", "added": added_count}

@router.post("/toggle-usb")
def toggle_usb_lock(payload: USBBlockToggleRequest, db: Session = Depends(get_db)):
    agent = db.query(AgentNode).filter(AgentNode.hwid == payload.hwid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.is_usb_blocked = payload.block
    db.commit()
    return {"status": "success"}

@router.post("/global-lock")
def global_lock(lock: bool, db: Session = Depends(get_db)):
    db.query(AgentNode).update({AgentNode.is_usb_blocked: lock})
    db.commit()
    return {"status": "success", "message": f"Global policy set to {lock}"}