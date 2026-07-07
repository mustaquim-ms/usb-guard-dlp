import os
import socket
import ctypes
import uuid
import logging

logger = logging.getLogger("Agent.SystemInfo")

def is_admin() -> bool:
    """Verifies if the current script process is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"Failed to check admin status: {e}")
        return False

def get_hwid() -> str:
    """Generates a stable unique Hardware ID (HWID) based on machine UUID."""
    try:
        # Get machine hardware UUID on Windows
        cmd = 'wmic csproduct get uuid'
        uuid_str = os.popen(cmd).read().replace('UUID', '').strip()
        if uuid_str:
            return uuid_str
    except Exception:
        pass
    # Fallback to MAC-based UUID
    return str(uuid.UUID(int=uuid.getnode()))

def get_hostname() -> str:
    """Returns the local computer network hostname."""
    return socket.gethostname()

def get_local_ip() -> str:
    """Attempts to fetch the primary local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a non-routable address to determine local interface IP
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip