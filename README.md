# USB Device Control & Monitoring Framework

## Project Overview
The **USB Device Control & Monitoring Framework** is a Python-based cybersecurity project developed to monitor USB device activity on a system, detect unauthorized USB connections, maintain authorized device allowlists, audit file activity, and generate security reports.

This project is designed to strengthen endpoint security by tracking USB insertions/removals, alerting users about unauthorized devices, recording file events, and providing a dashboard for monitoring USB-related threats.

---

## Objectives
- Monitor USB devices connected to the system
- Detect authorized and unauthorized USB devices
- Alert the user when an unauthorized USB is detected
- Log USB connection and removal events
- Maintain an authorized device list (allowlist)
- Audit file creation, modification, and deletion events
- Generate PDF security reports
- Provide a GUI dashboard for security monitoring

---

## Technologies Used
- **Python**
- **CustomTkinter** – GUI dashboard
- **SQLite** – database for storing USB logs and file audit logs
- **WMI / pywin32** – USB device monitoring on Windows
- **Watchdog** – file activity monitoring
- **ReportLab** – PDF report generation

---

## Main Features
### 1. USB Monitoring
- Detects USB device insertion and removal
- Identifies device name and status
- Logs connection events into the database

### 2. Unauthorized Device Detection
- Checks whether the inserted USB is in the authorized devices list
- Displays warning alert for unauthorized devices
- Logs blocked/unauthorized access attempts

### 3. Allowlist Management
- Add authorized devices
- View authorized devices
- Remove authorized devices

### 4. File Audit Monitoring
- Monitors file creation, modification, and deletion events
- Stores file audit records in database
- Displays file audit logs in GUI

### 5. Security Reports
- Generates PDF reports containing:
  - USB event logs
  - Unauthorized device logs
  - File audit logs

### 6. Dashboard & Statistics
- Connected device count
- Unauthorized device count
- File activity statistics
- Log viewing and searching options

---

## Project Files
- **usb_gui.py** → Main GUI dashboard and USB monitoring system
- **file_audit.py** → File auditing module for tracking file events
- **usb_monitor.db** → SQLite database storing logs and device records

---

## How It Works
1. The system continuously monitors USB devices connected to the computer.
2. When a USB device is inserted, its name is extracted.
3. The device is checked against the authorized device list.
4. If the device is authorized, it is allowed and logged.
5. If the device is unauthorized, a warning alert is generated and the event is logged.
6. File activities inside the monitored folder are tracked separately.
7. Security reports can be generated from the collected logs.

---

## Sample Workflow
**Start**  
↓  
Monitor USB Events  
↓  
Extract Device Information  
↓  
Check Allowlist / Blocklist  
↓  
Authorized?  
- **Yes** → Allow & Log  
- **No** → Alert / Block & Log  
↓  
Monitor File Activity  
↓  
Generate Security Report  
↓  
**End**

---

## Future Enhancements
- Email alert system for unauthorized USB detection
- Real-time auto-blocking of suspicious USB devices
- Admin login authentication for dashboard access
- Cloud log backup and centralized monitoring
- Export reports in multiple formats

---

## Author
**Asna**
Cybersecurity / Digital Forensics Student
