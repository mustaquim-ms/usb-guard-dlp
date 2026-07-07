import time
import logging
import requests
import sys

from config import SERVER_URL, HEARTBEAT_INTERVAL
from core.system_info import is_admin, get_hwid, get_hostname, get_local_ip
from core.registry_manager import USBRegistryController
from core.device_monitor import USBDeviceMonitor

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
)
logger = logging.getLogger("USBGuardAgent")

def on_unauthorized_device(device_info: dict):
    """Action taken when an unapproved USB drive is inserted while locked."""
    logger.warning(f"Reporting unauthorized USB insertion: {device_info}")
    try:
        requests.post(
            f"{SERVER_URL}/api/v1/agent/log",
            json={
                "hwid": get_hwid(),
                "event_type": "UNAUTHORIZED_USB_INSERTION",
                "details": f"Model: {device_info.get('model')} | Serial: {device_info.get('serial')}"
            },
            timeout=3
        )
    except Exception as e:
        logger.error(f"Failed to submit alert log to server: {e}")

def run_agent():
    logger.info("Starting USB Guard Agent Service...")
    
    # 1. Verify Privileges
    if not is_admin():
        logger.critical("FATAL: Agent must run with Administrator Privileges to manipulate USB registry state!")
        sys.exit(1)

    hwid = get_hwid()
    hostname = get_hostname()
    
    # Initialize Device Monitor
    monitor = USBDeviceMonitor(on_unauthorized_device_inserted=on_unauthorized_device)

    current_usb_blocked_state = None

    # 2. Main Executive Polling Loop
    while True:
        try:
            local_ip = get_local_ip()
            
            # Send Heartbeat & retrieve active server directive
            response = requests.post(
                f"{SERVER_URL}/api/v1/agent/heartbeat",
                json={
                    "hwid": hwid,
                    "hostname": hostname,
                    "ip_address": local_ip
                },
                timeout=5
            )

            if response.status_code == 200:
                policy = response.json()
                desired_block_state = policy["is_usb_blocked"]
                whitelisted_serials = policy["whitelisted_serials"]

                # Update Whitelist Filter Cache
                monitor.update_whitelist(whitelisted_serials)

                # Execute lock/unlock only on state transitions
                if desired_block_state != current_usb_blocked_state:
                    logger.info(f"Policy state change requested: Block={desired_block_state}")
                    
                    success, msg = USBRegistryController.set_usb_storage_status(disable=desired_block_state)
                    
                    if success:
                        current_usb_blocked_state = desired_block_state
                        logger.info(f"Enforcement succeeded: {msg}")
                    else:
                        logger.error(f"Enforcement failed: {msg}")

                # Real-time scan check
                if current_usb_blocked_state:
                    monitor.scan_and_enforce()

        except requests.exceptions.RequestException as e:
            logger.warning(f"Connection to Central Server failed ({e}). Retrying in {HEARTBEAT_INTERVAL}s...")
        except Exception as e:
            logger.error(f"Unexpected error in agent loop: {e}", exc_info=True)

        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    run_agent()