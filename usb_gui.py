import customtkinter as ctk
from tkinter import messagebox
import threading
import wmi
import time
import sqlite3
import pythoncom
from datetime import datetime
from reportlab.pdfgen import canvas
# ================= DATABASE ================= #

connection = sqlite3.connect(
    "usb_monitor.db",
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usb_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT,
    status TEXT,
    action TEXT,
    timestamp TEXT
)
""")

connection.commit()

# ================= APP SETTINGS ================= #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("Industrial USB Security Monitoring Dashboard")

app.geometry("1400x800")

monitoring = False

connected_devices = set()

unauthorized_count = 0
total_events = 0

authorized_count = 0
authorized_devices = [
    "VendorCo ProductCode USB Device"
]

# ================= FUNCTIONS ================= #

# -------- DEVICE LOGS WINDOW -------- #

def open_logs():

    logs_window = ctk.CTkToplevel(app)

    logs_window.title("USB Device Logs")

    logs_window.geometry("900x500")

    textbox = ctk.CTkTextbox(
        logs_window,
        width=850,
        height=450,
        font=("Consolas", 14)
    )

    textbox.pack(pady=20)

    cursor.execute("""
    SELECT * FROM usb_logs
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:

        textbox.insert(
            "end",
            f"{row}\n"
        )

# -------- THREAT ALERTS WINDOW -------- #

def open_alerts():

    alerts_window = ctk.CTkToplevel(app)

    alerts_window.title("Threat Alerts")

    alerts_window.geometry("850x500")

    textbox = ctk.CTkTextbox(
        alerts_window,
        width=800,
        height=430,
        font=("Consolas", 14)
    )

    textbox.pack(pady=20)

    cursor.execute("""
    SELECT * FROM usb_logs
    WHERE status='UNAUTHORIZED'
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    if not rows:

        textbox.insert(
            "end",
            "No Unauthorized Devices Detected"
        )

    else:

        for row in rows:

            textbox.insert(
                "end",
                f"{row}\n"
            )

# -------- REPORT WINDOW -------- #

def open_reports():

    reports_window = ctk.CTkToplevel(app)

    reports_window.title("Security Reports")

    reports_window.geometry("700x400")

    cursor.execute("""
    SELECT COUNT(*) FROM usb_logs
    """)

    total_logs = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM usb_logs
    WHERE status='UNAUTHORIZED'
    """)

    threats = cursor.fetchone()[0]

    report_text = f"""

INDUSTRIAL USB SECURITY REPORT

-------------------------------------

Total USB Events: {total_logs}

Unauthorized Threats: {threats}

Authorized Devices:
{len(authorized_devices)}

System Status:
ACTIVE & MONITORING

"""

    textbox = ctk.CTkTextbox(
        reports_window,
        width=600,
        height=300,
        font=("Consolas", 16)
    )

    textbox.pack(pady=30)

    textbox.insert(
        "end",
        report_text
    )
    # -------- STATISTICS WINDOW -------- #

def open_statistics():

    stats_window = ctk.CTkToplevel(app)

    stats_window.title("USB Statistics")

    stats_window.geometry("600x600")

    cursor.execute("SELECT COUNT(*) FROM usb_logs")
    total_events = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM usb_logs
    WHERE status='AUTHORIZED'
    """)
    authorized = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM usb_logs
    WHERE status='UNAUTHORIZED'
    """)
    unauthorized = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM file_audit
    WHERE action='CREATED'
    """)
    created_files = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM file_audit
    WHERE action='MODIFIED'
    """)
    modified_files = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM file_audit
    WHERE action='DELETED'
    """)
    deleted_files = cursor.fetchone()[0]

    ctk.CTkLabel(
        stats_window,
        text=f"📊 Total USB Events: {total_events}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"✅ Authorized Events: {authorized}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"⚠️ Unauthorized Events: {unauthorized}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"🔌 Connected Devices: {len(connected_devices)}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"📁 Files Created: {created_files}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"✏️ Files Modified: {modified_files}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        stats_window,
        text=f"🗑️ Files Deleted: {deleted_files}",
        font=("Arial", 18, "bold")
    ).pack(pady=10)
def open_file_audit():

    audit_window = ctk.CTkToplevel(app)

    audit_window.title("File Audit Logs")

    audit_window.geometry("1000x500")

    textbox = ctk.CTkTextbox(
        audit_window,
        width=950,
        height=430
    )

    textbox.pack(pady=20)

    cursor.execute("""
    SELECT * FROM file_audit
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    if not rows:

        textbox.insert(
            "end",
            "No File Audit Records Found"
        )

    else:

        for row in rows:

            textbox.insert(
                "end",
                f"{row}\n"
            )
def search_file_audit():

    keyword = ctk.CTkInputDialog(
        text="Enter File Name:",
        title="Search Audit Logs"
    ).get_input()

    if not keyword:
        return

    window = ctk.CTkToplevel(app)

    window.title("Search Results")

    window.geometry("900x500")

    textbox = ctk.CTkTextbox(
        window,
        width=850,
        height=430
    )

    textbox.pack(pady=20)

    cursor.execute(
        """
        SELECT *
        FROM file_audit
        WHERE file_path LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%",)
    )

    rows = cursor.fetchall()

    if not rows:

        textbox.insert(
            "end",
            "No Records Found"
        )

    else:

        for row in rows:

            textbox.insert(
                "end",
                f"{row}\n"
            )
# ================= WHITELIST FUNCTIONS ================= #

def add_device():

    device = ctk.CTkInputDialog(
        text="Enter Device Name:",
        title="Add Authorized Device"
    ).get_input()

    if device:

        try:

            cursor.execute(
                """
                INSERT INTO authorized_devices(device_name)
                VALUES(?)
                """,
                (device,)
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Device Added Successfully"
            )

        except:

            messagebox.showerror(
                "Error",
                "Device Already Exists"
            )

def view_devices():

    window = ctk.CTkToplevel(app)

    window.title("Authorized Devices")

    window.geometry("600x400")

    textbox = ctk.CTkTextbox(
        window,
        width=550,
        height=350
    )

    textbox.pack(padx=20, pady=20, fill="both", expand=True)

    conn = sqlite3.connect("usb_monitor.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT device_name FROM authorized_devices"
    )

    devices = cursor.fetchall()

    if len(devices) == 0:

        textbox.insert(
            "end",
            "No authorized devices found."
        )

    else:

        for device in devices:

            textbox.insert(
                "end",
                device[0] + "\n"
            )

    conn.close()

def remove_device():

    device = ctk.CTkInputDialog(
        text="Enter Device Name:",
        title="Remove Authorized Device"
    ).get_input()

    if device:

        cursor.execute(
            """
            DELETE FROM authorized_devices
            WHERE device_name=?
            """,
            (device,)
        )

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Device Removed Successfully"
        )
# ================= SIDEBAR ================= #

def export_pdf_report():

    from reportlab.pdfgen import canvas
    import sqlite3
    from tkinter import messagebox

    pdf = canvas.Canvas("USB_Security_Report.pdf")

    conn = sqlite3.connect("usb_monitor.db")
    cursor = conn.cursor()

    y = 800

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "USB SECURITY AUDIT REPORT")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "USB LOGS")
    y -= 25

    cursor.execute("""
    SELECT device_name, status, action, timestamp
    FROM usb_logs
    ORDER BY id DESC
    """)

    usb_logs = cursor.fetchall()

    pdf.setFont("Helvetica", 10)

    if not usb_logs:
        pdf.drawString(50, y, "No USB logs found.")
        y -= 20
    else:
        for log in usb_logs:
            line = f"{log[0]} | {log[1]} | {log[2]} | {log[3]}"
            pdf.drawString(50, y, line)
            y -= 18

            if y < 60:
                pdf.showPage()
                y = 800
                pdf.setFont("Helvetica", 10)

    y -= 20

    if y < 100:
        pdf.showPage()
        y = 800

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "FILE AUDIT LOGS")
    y -= 25

    cursor.execute("""
    SELECT action, file_path, timestamp
    FROM file_audit
    ORDER BY id DESC
    """)

    file_logs = cursor.fetchall()

    pdf.setFont("Helvetica", 10)

    if not file_logs:
        pdf.drawString(50, y, "No File Audit logs found.")
        y -= 20
    else:
        for log in file_logs:
            line = f"{log[0]} | {log[1]} | {log[2]}"
            pdf.drawString(50, y, line)
            y -= 18

            if y < 60:
                pdf.showPage()
                y = 800
                pdf.setFont("Helvetica", 10)

    conn.close()
    pdf.save()

    messagebox.showinfo(
        "Success",
        "PDF Report Generated Successfully"
    )
def clear_logs():

    confirm = messagebox.askyesno(
        "Clear Logs",
        "Do you want to delete all USB and File Audit logs?"
    )

    if confirm:
        cursor.execute("DELETE FROM usb_logs")
        cursor.execute("DELETE FROM file_audit")
        connection.commit()

        log_box.delete("1.0", "end")

        messagebox.showinfo(
            "Success",
            "All logs cleared successfully"
        )
sidebar = ctk.CTkFrame(
    app,
    width=220,
    corner_radius=0
)

sidebar.pack(side="left", fill="y")

title = ctk.CTkLabel(
    sidebar,
    text="USB Security\nDashboard",
    font=("Arial", 32, "bold")
)

title.pack(pady=40)

dashboard_btn = ctk.CTkButton(
    sidebar,
    text="Dashboard",
    width=170,
    height=45
)

dashboard_btn.pack(pady=10)

logs_btn = ctk.CTkButton(
    sidebar,
    text="Device Logs",
    width=170,
    height=45,
    command=open_logs
)

logs_btn.pack(pady=10)

alerts_btn = ctk.CTkButton(
    sidebar,
    text="Threat Alerts",
    width=170,
    height=45,
    command=open_alerts
)

alerts_btn.pack(pady=10)

reports_btn = ctk.CTkButton(
    sidebar,
    text="Reports",
    width=170,
    height=45,
    command=open_reports
)

reports_btn.pack(pady=10)
pdf_btn = ctk.CTkButton(
    sidebar,
    text="📄 Export PDF",
    width=170,
    height=45,
    command=export_pdf_report
)

pdf_btn.pack(pady=10)
clear_btn = ctk.CTkButton(
    sidebar,
    text="🗑 Clear Logs",
    width=170,
    height=45,
    command=clear_logs
)

clear_btn.pack(pady=10)
stats_btn = ctk.CTkButton(
    sidebar,
    text="📊 Statistics",
    width=170,
    height=45,
    command=open_statistics
)

stats_btn.pack(pady=10)
audit_btn = ctk.CTkButton(
    sidebar,
    text="📁 File Audit Logs",
    width=170,
    height=45,
    command=open_file_audit
)

audit_btn.pack(pady=10)
search_btn = ctk.CTkButton(
    sidebar,
    text="🔍 Search Logs",
    width=170,
    height=45,
    command=search_file_audit
)

search_btn.pack(pady=10)
# ================= WHITELIST BUTTONS ================= #

add_device_btn = ctk.CTkButton(
    sidebar,
    text="➕ Add Device",
    width=170,
    height=45,
    command=add_device
)

add_device_btn.pack(pady=10)

view_devices_btn = ctk.CTkButton(
    sidebar,
    text="📋 View Devices",
    width=170,
    height=45,
    command=view_devices
)

view_devices_btn.pack(pady=10)

remove_device_btn = ctk.CTkButton(
    sidebar,
    text="❌ Remove Device",
    width=170,
    height=45,
    command=remove_device
)

remove_device_btn.pack(pady=10)
# ================= MAIN AREA ================= #

main_frame = ctk.CTkFrame(app)

main_frame.pack(side="right", fill="both", expand=True)

heading = ctk.CTkLabel(
    main_frame,
    text="Industrial USB Threat Monitoring System",
    font=("Arial", 38, "bold")
)

heading.pack(pady=30)

# ================= STATUS CARDS ================= #

status_frame = ctk.CTkFrame(main_frame)

status_frame.pack(pady=20)

device_card = ctk.CTkLabel(
    status_frame,
    text="Connected Devices\n0",
    width=300,
    height=120,
    font=("Arial", 28, "bold"),
    corner_radius=15
)

device_card.grid(row=0, column=0, padx=25)

threat_card = ctk.CTkLabel(
    status_frame,
    text="Unauthorized Devices\n0",
    width=300,
    height=120,
    font=("Arial", 28, "bold"),
    corner_radius=15
)

threat_card.grid(row=0, column=1, padx=25)

# ================= LOG AREA ================= #

log_box = ctk.CTkTextbox(
    main_frame,
    width=950,
    height=380,
    font=("Consolas", 16)
)

log_box.pack(pady=30)

# ================= USB MONITOR FUNCTION ================= #

def monitor_usb():

    pythoncom.CoInitialize()

    global connected_devices
    global unauthorized_count
    global monitoring

    c = wmi.WMI()

    while monitoring:

        try:

            current_devices = set()

            for disk in c.Win32_DiskDrive():

                if disk.InterfaceType  == "USB":

                    device_name = disk.Caption

                    current_devices.add(device_name)

                    if device_name not in connected_devices:

                        timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        if device_name in authorized_devices:

                           status = "AUTHORIZED"

                        else:

                           status = "UNAUTHORIZED"

                           unauthorized_count += 1

                           messagebox.showwarning(
                               "⚠ SECURITY ALERT",
                               f"Unauthorized USB Detected!\n\nDevice:\n{device_name}"
                           )

                           app.bell()
                           cursor.execute(
                              """
                              INSERT INTO usb_logs
                              (device_name, status, action, timestamp)
                              VALUES (?, ?, ?, ?)
                              """,
                              (
                                 device_name,
                                 "BLOCKED",
                                 "ACCESS DENIED",
                                 timestamp
                              )
                           )

                           connection.commit()

                           log_box.insert(
                              "end",
                              f"[!] BLOCKED Unauthorized USB: {device_name} | {timestamp}\n"
                           )

                           log_box.see("end")


                        message = (
                            f"[+] USB Connected: "
                            f"{device_name} | "
                            f"Status: {status} | "
                            f"{timestamp}\n"
                        )

                        log_box.insert("end", message)

                        log_box.see("end")

                        cursor.execute(
                            """
                            INSERT INTO usb_logs
                            (device_name, status, action, timestamp)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                device_name,
                                status,
                                "CONNECTED",
                                timestamp
                            )
                        )

                        connection.commit()

            removed_devices = connected_devices - current_devices

            for device in removed_devices:

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                remove_msg = (
                    f"[-] USB Removed: "
                    f"{device} | "
                    f"{timestamp}\n"
                )

                log_box.insert("end", remove_msg)

                log_box.see("end")

                cursor.execute(
                    """
                    INSERT INTO usb_logs
                    (device_name, status, action, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        device,
                        "REMOVED",
                        "DISCONNECTED",
                        timestamp
                    )
                )

                connection.commit()

            connected_devices = current_devices

            device_card.configure(
                text=f"Connected Devices\n{len(current_devices)}"
            )

            threat_card.configure(
                text=f"Unauthorized Devices\n{unauthorized_count}"
            )

            time.sleep(2)

        except Exception as e:

            log_box.insert(
                "end",
                f"\nERROR: {str(e)}\n"
            )

            log_box.see("end")

            time.sleep(2)

# ================= BUTTON FUNCTIONS ================= #

def start_monitoring():

    global monitoring

    if not monitoring:

        monitoring = True

        monitor_thread = threading.Thread(
            target=monitor_usb
        )

        monitor_thread.daemon = True

        monitor_thread.start()

        messagebox.showinfo(
            "USB Monitor",
            "Monitoring Started Successfully"
        )

def stop_monitoring():

    global monitoring

    monitoring = False

    messagebox.showinfo(
        "USB Monitor",
        "Monitoring Stopped"
    )

# ================= BUTTONS ================= #

button_frame = ctk.CTkFrame(main_frame)

button_frame.pack(pady=10)

start_btn = ctk.CTkButton(
    button_frame,
    text="Start Monitoring",
    command=start_monitoring,
    width=220,
    height=55,
    font=("Arial", 18, "bold")
)

start_btn.grid(row=0, column=0, padx=25)

stop_btn = ctk.CTkButton(
    button_frame,
    text="Stop Monitoring",
    command=stop_monitoring,
    width=220,
    height=55,
    font=("Arial", 18, "bold")
)

stop_btn.grid(row=0, column=1, padx=25)

# ================= RUN APP ================= #

app.mainloop()