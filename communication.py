import socket
import subprocess
import platform
import sqlite3

from datetime import datetime

from database import DATABASE


# ============================================================
# DATABASE
# ============================================================

def connect_db():

    return sqlite3.connect(
        str(DATABASE)
    )


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
# TCP CHECK
# ============================================================

def check_tcp(
    ip_address,
    port
):

    if not ip_address:
        return False

    if not port:
        return check_ping(ip_address)

    try:

        port = int(port)

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(2)

        result = sock.connect_ex(
            (
                ip_address,
                port
            )
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
    communication_port=""
):

    if communication_port:

        return check_tcp(
            ip_address,
            communication_port
        )

    return check_ping(
        ip_address
    )


# ============================================================
# GENERATE TICKET ID
# ============================================================

def generate_ticket_id():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM communication_tickets
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row:

        number = row[0] + 1

    else:

        number = 1

    return f"TKT-{number:06d}"


# ============================================================
# OPEN TICKET
# ============================================================

def get_open_ticket(
    equipment_name
):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM communication_tickets
        WHERE equipment_name = ?
        AND status = 'OPEN'
        ORDER BY id DESC
        LIMIT 1
    """, (
        equipment_name,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


# ============================================================
# CREATE TICKET
# ============================================================

def create_communication_ticket(

    location_name,
    equipment_type,
    equipment_name,
    ip_address,
    communication_protocol,
    communication_port

):

    existing = get_open_ticket(
        equipment_name
    )

    if existing:

        return existing[1]

    ticket_id = generate_ticket_id()

    opened_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO communication_tickets
        (
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
        str(communication_port),

        "Communication Failure",

        "High",

        "OPEN",

        opened_at

    ))

    conn.commit()

    conn.close()

    return ticket_id


# ============================================================
# RESOLVE TICKET
# ============================================================

def resolve_communication_ticket(
    equipment_name
):

    ticket = get_open_ticket(
        equipment_name
    )

    if not ticket:

        return False

    ticket_id = ticket[1]

    opened_at = ticket[11]

    resolved_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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

    cursor = conn.cursor()

    cursor.execute("""
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
# PROCESS EQUIPMENT
# ============================================================

def process_equipment(

    location_name,
    equipment_type,
    equipment_name,
    ip_address,
    communication_protocol,
    communication_port

):

    healthy = check_communication(

        ip_address,

        communication_port

    )

    if healthy:

        resolve_communication_ticket(
            equipment_name
        )

        return "HEALTHY"

    else:

        ticket_id = create_communication_ticket(

            location_name,

            equipment_type,

            equipment_name,

            ip_address,

            communication_protocol,

            communication_port

        )

        return f"FAILED - {ticket_id}"


# ============================================================
# ACTIVE TICKETS
# ============================================================

def get_active_tickets():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# TICKET HISTORY
# ============================================================

def get_ticket_history():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# COMMUNICATION MONITOR
# ============================================================

def communication_monitor():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            e.id,
            l.location_name,
            e.equipment_type,
            e.equipment_name,
            e.ip_address,
            e.communication_protocol,
            e.communication_port,
            e.status
        FROM equipment e
        LEFT JOIN locations l
        ON e.location_id = l.id
        ORDER BY e.id
    """)

    equipment_list = cursor.fetchall()

    conn.close()

    results = []

    for equipment in equipment_list:

        (
            equipment_id,
            location_name,
            equipment_type,
            equipment_name,
            ip_address,
            protocol,
            port,
            old_status
        ) = equipment

        result = process_equipment(

            location_name,

            equipment_type,

            equipment_name,

            ip_address,

            protocol,

            port

        )

        if result == "HEALTHY":

            status = "Healthy"

        else:

            status = "Communication Failed"

        conn = connect_db()

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

        results.append({

            "Equipment": equipment_name,

            "Type": equipment_type,

            "IP Address": ip_address,

            "Protocol": protocol,

            "Port": port,

            "Status": status,

            "Result": result

        })

    return results