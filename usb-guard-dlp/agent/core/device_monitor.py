import time
import logging
from typing import List, Dict, Callable

logger = logging.getLogger("Agent.DeviceMonitor")

class USBDeviceMonitor:
    def __init__(self, on_unauthorized_device_inserted: Callable[[Dict], None]):
        self.on_unauthorized = on_unauthorized_device_inserted
        self.whitelist_serials: List[str] = []

    def update_whitelist(self, serials: List[str]):
        """Updates internal cached serial whitelist."""
        self.whitelist_serials = [s.strip().upper() for s in serials]
        logger.info(f"Updated whitelist serial numbers count: {len(self.whitelist_serials)}")

    def get_connected_usb_devices(self) -> List[Dict[str, str]]:
        """Queries WMI for currently plugged-in USB Disk Drives."""
        devices = []
        try:
            import wmi
            c = wmi.WMI()
            # Query physical disk drives connected via USB interface
            for disk in c.Win32_DiskDrive(InterfaceType="USB"):
                devices.append({
                    "deviceID": str(disk.DeviceID),
                    "model": str(disk.Model),
                    "serial": str(disk.SerialNumber).strip().upper() if disk.SerialNumber else "UNKNOWN",
                    "pnpDeviceID": str(disk.PNPDeviceID)
                })
        except Exception as e:
            logger.error(f"Error querying USB devices via WMI: {e}")
        return devices

    def scan_and_enforce(self):
        """Scans connected USB drives and checks against active whitelist."""
        connected = self.get_connected_usb_devices()
        for dev in connected:
            serial = dev["serial"]
            if serial not in self.whitelist_serials and serial != "UNKNOWN":
                logger.warning(f"UNAUTHORIZED USB DETECTED! Model: {dev['model']} Serial: {serial}")
                # Execute callback action for unauthorized device
                self.on_unauthorized(dev)