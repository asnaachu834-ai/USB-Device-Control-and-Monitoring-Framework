import time
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Database Connection

connection = sqlite3.connect(
    "usb_monitor.db",
    check_same_thread=False
)

cursor = connection.cursor()

# Create File Audit Table

cursor.execute("""
CREATE TABLE IF NOT EXISTS file_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    file_path TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()

# Event Handler

class FileMonitor(FileSystemEventHandler):

    def on_created(self, event):

        if not event.is_directory:

            print(f"[CREATED] {event.src_path}")

            cursor.execute(
                """
                INSERT INTO file_audit(action,file_path)
                VALUES(?,?)
                """,
                ("CREATED", event.src_path)
            )

            connection.commit()

    def on_deleted(self, event):

        if not event.is_directory:

            print(f"[DELETED] {event.src_path}")

            cursor.execute(
                """
                INSERT INTO file_audit(action,file_path)
                VALUES(?,?)
                """,
                ("DELETED", event.src_path)
            )

            connection.commit()

    def on_modified(self, event):

        if not event.is_directory:

            print(f"[MODIFIED] {event.src_path}")

            cursor.execute(
                """
                INSERT INTO file_audit(action,file_path)
                VALUES(?,?)
                """,
                ("MODIFIED", event.src_path)
            )

            connection.commit()

# CHANGE THIS PATH

WATCH_FOLDER = r"D:\TestUSB"

observer = Observer()

observer.schedule(
    FileMonitor(),
    WATCH_FOLDER,
    recursive=True
)

observer.start()

print("File Auditing Started...")
print("Monitoring:", WATCH_FOLDER)

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    observer.stop()

observer.join()

connection.close()