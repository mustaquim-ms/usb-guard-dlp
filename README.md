# 🛡️ Octate Odyssey | Enterprise Device Defense

![Version](https://img.shields.io/badge/version-1.2.0-a3e635?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-05070a?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Hardened-blue?style=for-the-badge)

**Octate Odyssey** is a high-fidelity, production-level Data Loss Prevention (DLP) and Endpoint Management system. It provides IT Administrators with a "Single Pane of Glass" to monitor, block, and whitelist USB hardware across an entire corporate fleet in real-time.

---

## 🚀 Core Capabilities

*   **Navigator ID Command:** A biometric-inspired, glassmorphic administrative console.
*   **One-Click Fleet Lockdown:** Instantly disable USB mass storage across all registered IPs.
*   **Hardware Whitelisting:** Authorize specific pendrives by Hardware Serial ID to bypass security blocks.
*   **Network Health Matrix:** Real-time visualization of fleet status using Spider/Radar charts.
*   **Biometric Authentication:** Multi-factor "Navigator" style login for authorized IT Personnel.
*   **Audit Intelligence:** Comprehensive logging of all device insertions and policy changes.
*   **Bulk Provisioning:** Support for CSV-based mass enrollment of endpoints and hardware.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy
- **Database:** SQLite (Enterprise-ready logic)
- **Frontend:** Tailwind CSS, JavaScript (ES6+), Chart.js
- **Icons/UI:** FontAwesome 6, Plus Jakarta Sans Typography

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/octate-odyssey.git
   cd octate-odyssey
# BASH CODE
## pip install fastapi uvicorn sqlalchemy requests pywin32 wmi python-multipart
## python setup_admin.py
## python -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload

# 📊 CSV Data Structure

To use the bulk upload feature, ensure your CSV files follow these headers:
## Fleet Enrollment (fleet.csv)
hostname	ip_address	owner
## Hardware Whitelist (whitelist.csv)
serial	owner


# ⚖️ License
Distributed under the MIT License. See LICENSE for more information.
Developed by Mustaquim Ahmad | Octate Odyssey Device Block Service

