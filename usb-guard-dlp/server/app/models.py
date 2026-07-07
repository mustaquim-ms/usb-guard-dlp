from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from server.app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    user_id_code = Column(String(50), unique=True) # ID Card Number / Employee ID
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    is_admin = Column(Boolean, default=True)

class AgentNode(Base):
    __tablename__ = "agent_nodes"
    id = Column(Integer, primary_key=True, index=True)
    hwid = Column(String(100), unique=True, index=True)
    hostname = Column(String(100))
    ip_address = Column(String(50))
    device_username = Column(String(100)) # NEW: The person using the laptop
    is_usb_blocked = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="OFFLINE")

# Keep WhitelistedUSB and AuditLog as they were
class WhitelistedUSB(Base):
    __tablename__ = "whitelisted_usbs"
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(100), unique=True)
    device_owner = Column(String(100)) # NEW: Who owns this USB
    added_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    hwid = Column(String(100))
    event_type = Column(String(50))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)