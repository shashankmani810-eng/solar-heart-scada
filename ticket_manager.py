import sqlite3
import socket
import subprocess
import platform
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

DATABASE = "database/jakcms.db"


def connect_db():
    return sqlite3.connect(DATABASE)


# ============================================================
# CREATE TICKET TABLE
# ============================================================

def create_ticket_table():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
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

    conn.commit()
    conn.close()


# ============================================================
# GENERATE TICKET ID
# ============================================================

def generate_ticket_id():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM communication_tickets
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    conn.close()

    if row:
        number = row[0] + 1
    else:
        number = 1

    return f"TKT-{number:06d}"


# ============================================================
# PING CHECK
# ============================================================

def check_ping(ip_address):

    if not ip_address:
        return False

    try:

        system = platform.system().lower()

        if system == "windows":

            result = subprocess.run(
                [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    "1000",
                    ip_address
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        else:

            result = subprocess.run(
                [
                    "ping",
                    "-c",
                    "1",
                    "-W",
                    "1",
                    ip_address
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        return result.returncode == 0

    except Exception:

        return False


# ============================================================
# TCP PORT CHECK
# ============================================================

def check_tcp(ip_address, port):

    if not ip_address or not port:
        return False

    try:

        port = int(port)

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(2)

        result = sock.connect_ex(
            (ip_address, port)
        )

        sock.close()

        return result == 0

    except Exception:

        return False


# ============================================================
# COMMUNICATION CHECK
# ============================================================

def check_communication(
    ip_address,
    communication_port=None
):

    # If communication port is available
    # check TCP port first.

    if communication_port:

        if check_tcp(
            ip_address,
            communication_port
        ):
            return True

        # TCP failed, so also try ping.
        # Some devices block TCP while still
        # responding to ICMP.

        return check_ping(ip_address)

    # No port configured
    # Use ping.

    return check_ping(ip_address)


# ============================================================
# GET OPEN TICKET
# ============================================================

def get_open_ticket(
    location_name,
    equipment_name
):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM communication_tickets

        WHERE location_name = ?
        AND equipment_name = ?
        AND status = 'OPEN'

        ORDER BY id DESC
        LIMIT 1
    """, (
        location_name,
        equipment_name
    ))

    row = cur.fetchone()

    conn.close()

    return row


# ============================================================
# CREATE COMMUNICATION TICKET
# ============================================================

def create_communication_ticket(
    location_name,
    equipment_type,
    equipment_name,
    ip_address,
    communication_protocol,
    communication_port
):

    create_ticket_table()

    # Check whether an OPEN ticket already exists.

    existing = get_open_ticket(
        location_name,
        equipment_name
    )

    if existing:

        # Return existing ticket number.
        return existing[1]

    # Generate new ticket ID.

    ticket_id = generate_ticket_id()

    opened_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO communication_tickets (

            ticket_id,
            location_name,
            equipment_type,
            equipment_name,
            ip_address,
            communication_protocol,
            communication_port,
            issue,
            priority,
            status,
            opened_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        ticket_id,

        location_name,

        equipment_type,

        equipment_name,

        ip_address,

        communication_protocol,

        str(communication_port)
        if communication_port
        else "",

        "Communication Failure",

        "High",

        "OPEN",

        opened_at

    ))

    conn.commit()
    conn.close()

    return ticket_id


# ============================================================
# AUTO RESOLVE TICKET
# ============================================================

def resolve_communication_ticket(
    location_name,
    equipment_name
):

    create_ticket_table()

    ticket = get_open_ticket(
        location_name,
        equipment_name
    )

    if not ticket:

        return False

    ticket_id = ticket[1]

    # Column 11 = opened_at
    opened_at = ticket[11]

    resolved_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Calculate communication failure duration.

    try:

        start = datetime.strptime(
            opened_at,
            "%Y-%m-%d %H:%M:%S"
        )

        end = datetime.strptime(
            resolved_at,
            "%Y-%m-%d %H:%M:%S"
        )

        duration = str(
            end - start
        )

    except Exception:

        duration = ""

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE communication_tickets

        SET

            status = 'AUTO RESOLVED',

            resolved_at = ?,

            duration = ?,

            remarks = ?

        WHERE ticket_id = ?

    """, (

        resolved_at,

        duration,

        "Communication restored automatically.",

        ticket_id

    ))

    conn.commit()
    conn.close()

    return True


# ============================================================
# PROCESS EQUIPMENT COMMUNICATION
# ============================================================

def process_equipment(
    location_name,
    equipment_type,
    equipment_name,
    ip_address,
    communication_protocol,
    communication_port
):

    create_ticket_table()

    # Check communication.

    healthy = check_communication(
        ip_address,
        communication_port
    )

    # ========================================================
    # COMMUNICATION HEALTHY
    # ========================================================

    if healthy:

        # If an old OPEN ticket exists,
        # automatically resolve it.

        resolve_communication_ticket(
            location_name,
            equipment_name
        )

        return {
            "status": "HEALTHY",
            "ticket_id": None
        }

    # ========================================================
    # COMMUNICATION FAILED
    # ========================================================

    else:

        ticket_id = create_communication_ticket(

            location_name,

            equipment_type,

            equipment_name,

            ip_address,

            communication_protocol,

            communication_port

        )

        return {
            "status": "FAILED",
            "ticket_id": ticket_id
        }


# ============================================================
# GET ACTIVE TICKETS
# ============================================================

def get_active_tickets():

    create_ticket_table()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ticket_id,
            location_name,
            equipment_type,
            equipment_name,
            ip_address,
            communication_protocol,
            communication_port,
            issue,
            priority,
            status,
            opened_at

        FROM communication_tickets

        WHERE status = 'OPEN'

        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


# ============================================================
# GET TICKET HISTORY
# ============================================================

def get_ticket_history():

    create_ticket_table()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ticket_id,
            location_name,
            equipment_type,
            equipment_name,
            ip_address,
            communication_protocol,
            communication_port,
            issue,
            priority,
            status,
            opened_at,
            resolved_at,
            duration,
            remarks

        FROM communication_tickets

        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


# ============================================================
# INITIALIZE DATABASE TABLE
# ============================================================

create_ticket_table()