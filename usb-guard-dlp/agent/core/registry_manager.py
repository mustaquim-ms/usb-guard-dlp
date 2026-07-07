import winreg
import logging
from typing import Tuple

logger = logging.getLogger("Agent.Registry")

# USBSTOR Registry Path
USBSTOR_PATH = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
STORAGE_POLICIES_PATH = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"

class USBRegistryController:
    @staticmethod
    def set_usb_storage_status(disable: bool) -> Tuple[bool, str]:
        """
        Enables or Disables USB Storage Devices at the Windows registry level.
        - Disable: Sets USBSTOR Start value to 4 (Disabled).
        - Enable: Sets USBSTOR Start value to 3 (Automatic/Enabled).
        """
        target_val = 4 if disable else 3
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, 
                USBSTOR_PATH, 
                0, 
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )
            
            # Write key
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, target_val)
            winreg.CloseKey(key)
            
            # Verification Step
            verify_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, USBSTOR_PATH, 0, winreg.KEY_READ)
            current_val, _ = winreg.QueryValueEx(verify_key, "Start")
            winreg.CloseKey(verify_key)
            
            if current_val == target_val:
                status_str = "BLOCKED" if disable else "ENABLED"
                logger.info(f"Successfully changed USB Storage state to: {status_str}")
                return True, f"USB Storage successfully {status_str}"
            else:
                return False, "Registry write verification failed."

        except PermissionError:
            err = "Access Denied. Administrator privileges are required to modify registry."
            logger.error(err)
            return False, err
        except Exception as e:
            err = f"Failed to modify USB registry state: {str(e)}"
            logger.error(err)
            return False, err

    @staticmethod
    def set_read_only_mode(enable: bool) -> Tuple[bool, str]:
        """
        Sets USB drives to Read-Only mode (prevents writing/copying files out).
        """
        target_val = 1 if enable else 0
        try:
            # Create key if it doesn't exist
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE, 
                STORAGE_POLICIES_PATH, 
                0, 
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "WriteProtect", 0, winreg.REG_DWORD, target_val)
            winreg.CloseKey(key)
            return True, f"USB Read-Only mode set to {enable}"
        except Exception as e:
            return False, f"Failed to configure Read-Only state: {str(e)}"