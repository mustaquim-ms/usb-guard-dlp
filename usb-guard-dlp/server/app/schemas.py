from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AgentHeartbeat(BaseModel):
    hwid: str
    hostname: str
    ip_address: str

class PolicyResponse(BaseModel):
    is_usb_blocked: bool
    is_read_only: bool
    whitelisted_serials: List[str]

class USBBlockToggleRequest(BaseModel):
    hwid: str
    block: bool

class WhitelistUSBRequest(BaseModel):
    serial_number: str
    device_name: Optional[str] = "Approved USB Drive"

class LogEntryCreate(BaseModel):
    hwid: str
    event_type: str
    details: str