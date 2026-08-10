import sqlite3
from pathlib import Path
from datetime import datetime

# ============================================================
# JAKCMS DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "jakcms.db"

DATABASE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect():
    conn = sqlite3.connect(str(DATABASE))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    conn = connect()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # LOCATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            location_name TEXT NOT NULL UNIQUE,

            description TEXT,

            status TEXT DEFAULT 'Healthy',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            location_id INTEGER NOT NULL,

            equipment_type TEXT NOT NULL,

            equipment_name TEXT NOT NULL,

            manufacturer TEXT,

            model TEXT,

            capacity TEXT,

            ip_address TEXT,

            communication_protocol TEXT,

            communication_port TEXT,

            status TEXT DEFAULT 'Healthy',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(location_id)
            REFERENCES locations(id)
            ON DELETE CASCADE

        )
    """)

    # --------------------------------------------------------
    # HT PANEL DEVICES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ht_panel_devices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            equipment_id INTEGER NOT NULL,

            device_type TEXT NOT NULL,

            device_name TEXT NOT NULL,

            manufacturer TEXT,

            model TEXT,

            communication_protocol TEXT,

            ip_address TEXT,

            communication_port TEXT,

            status TEXT DEFAULT 'Healthy',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(equipment_id)
            REFERENCES equipment(id)
            ON DELETE CASCADE

        )
    """)

    # --------------------------------------------------------
    # COMMUNICATION TICKETS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communication_tickets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id TEXT UNIQUE,

            location_name TEXT,

            equipment_type TEXT,

            equipment_name TEXT,

            ip_address TEXT,

            communication_protocol TEXT,

            communication_port TEXT,

            issue TEXT,

            priority TEXT DEFAULT 'High',

            status TEXT DEFAULT 'OPEN',

            opened_at TEXT,

            resolved_at TEXT,

            duration TEXT,

            remarks TEXT

        )
    """)

    # --------------------------------------------------------
    # ALARMS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarms (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alarm_time TEXT,

            equipment_name TEXT,

            alarm_type TEXT,

            priority TEXT,

            status TEXT DEFAULT 'ACTIVE',

            remarks TEXT

        )
    """)

    # --------------------------------------------------------
    # DEFAULT LOCATION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM locations
    """)

    count = cursor.fetchone()[0]

    if count == 0:

        cursor.execute("""
            INSERT INTO locations
            (
                location_name,
                description,
                status
            )
            VALUES (?, ?, ?)
        """, (
            "250 MW Solar Plant",
            "JAKCMS Solar Power Plant",
            "Healthy"
        ))

    conn.commit()
    conn.close()


# ============================================================
# LOCATION FUNCTIONS
# ============================================================

def add_location(location_name, description=""):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO locations
        (
            location_name,
            description
        )
        VALUES (?, ?)
    """, (
        location_name,
        description
    ))

    conn.commit()

    location_id = cursor.lastrowid

    conn.close()

    return location_id


def get_locations():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            location_name,
            description,
            status,
            created_at
        FROM locations
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_location(location_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM locations
        WHERE id = ?
    """, (location_id,))

    conn.commit()
    conn.close()


# ============================================================
# EQUIPMENT FUNCTIONS
# ============================================================

def add_equipment(
    location_id,
    equipment_type,
    equipment_name,
    manufacturer="",
    model="",
    capacity="",
    ip_address="",
    communication_protocol="",
    communication_port=""
):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO equipment
        (
            location_id,
            equipment_type,
            equipment_name,
            manufacturer,
            model,
            capacity,
            ip_address,
            communication_protocol,
            communication_port
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        location_id,
        equipment_type,
        equipment_name,
        manufacturer,
        model,
        capacity,
        ip_address,
        communication_protocol,
        communication_port
    ))

    conn.commit()

    equipment_id = cursor.lastrowid

    conn.close()

    return equipment_id


def get_equipment(location_id=None):

    conn = connect()
    cursor = conn.cursor()

    if location_id is None:

        cursor.execute("""
            SELECT
                e.id,
                e.location_id,
                l.location_name,
                e.equipment_type,
                e.equipment_name,
                e.manufacturer,
                e.model,
                e.capacity,
                e.ip_address,
                e.communication_protocol,
                e.communication_port,
                e.status
            FROM equipment e
            LEFT JOIN locations l
            ON e.location_id = l.id
            ORDER BY e.id
        """)

    else:

        cursor.execute("""
            SELECT
                e.id,
                e.location_id,
                l.location_name,
                e.equipment_type,
                e.equipment_name,
                e.manufacturer,
                e.model,
                e.capacity,
                e.ip_address,
                e.communication_protocol,
                e.communication_port,
                e.status
            FROM equipment e
            LEFT JOIN locations l
            ON e.location_id = l.id
            WHERE e.location_id = ?
            ORDER BY e.id
        """, (location_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_equipment(equipment_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM equipment
        WHERE id = ?
    """, (equipment_id,))

    conn.commit()
    conn.close()


# ============================================================
# UPDATE EQUIPMENT STATUS
# ============================================================

def update_equipment_status(equipment_id, status):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE equipment
        SET status = ?
        WHERE id = ?
    """, (
        status,
        equipment_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# HT PANEL DEVICES
# ============================================================

def add_ht_panel_device(
    equipment_id,
    device_type,
    device_name,
    manufacturer="",
    model="",
    communication_protocol="",
    ip_address="",
    communication_port=""
):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ht_panel_devices
        (
            equipment_id,
            device_type,
            device_name,
            manufacturer,
            model,
            communication_protocol,
            ip_address,
            communication_port
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        equipment_id,
        device_type,
        device_name,
        manufacturer,
        model,
        communication_protocol,
        ip_address,
        communication_port
    ))

    conn.commit()

    device_id = cursor.lastrowid

    conn.close()

    return device_id


def get_ht_panel_devices(equipment_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            equipment_id,
            device_type,
            device_name,
            manufacturer,
            model,
            communication_protocol,
            ip_address,
            communication_port,
            status
        FROM ht_panel_devices
        WHERE equipment_id = ?
        ORDER BY id
    """, (equipment_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_ht_panel_device(device_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM ht_panel_devices
        WHERE id = ?
    """, (device_id,))

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE
# ============================================================

create_database()


if __name__ == "__main__":

    print("======================================")
    print(" JAKCMS Database Ready")
    print("======================================")
    print(f"Database : {DATABASE}")