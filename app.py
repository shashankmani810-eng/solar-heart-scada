import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

# ============================================================
# SOLAR HEART - MAIN APPLICATION
# Existing login/dashboard/navigation retained.
# OPC-UA is NOT connected yet; demo values are used until
# real Node IDs are mapped.
# ============================================================

APP_NAME = "SOLAR HEART"
COMPANY_NAME = "JAKVISION"
VERSION = "2.0"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# USER / ROLE MANAGEMENT
# ============================================================
USERS_FILE = Path(__file__).with_name("users.json")
DEFAULT_USERS = {
    "admin": {"password_hash": hashlib.sha256("admin123".encode()).hexdigest(), "role": "Administrator"},
    "operator": {"password_hash": hashlib.sha256("operator123".encode()).hexdigest(), "role": "Operator"},
    "supervisor": {"password_hash": hashlib.sha256("supervisor123".encode()).hexdigest(), "role": "Supervisor"},
}

ROLE_PAGES = {
    "Administrator": [
        "Dashboard", "Plant Mimic", "Plant Configuration", "Inverters",
        "HT Panels", "Weather", "Communication", "Alarms", "Trends",
        "Reports", "Settings"
    ],
    "Operator": [
        "Dashboard", "Plant Mimic", "Inverters", "HT Panels", "Alarms", "Trends"
    ],
    "Supervisor": [
        "Dashboard", "Plant Mimic", "Inverters", "HT Panels", "Weather",
        "Alarms", "Trends", "Reports"
    ],
}

def load_users():
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps(DEFAULT_USERS, indent=4), encoding="utf-8")
        return DEFAULT_USERS.copy()
    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data:
            raise ValueError("Invalid users file")
        return data
    except Exception:
        USERS_FILE.write_text(json.dumps(DEFAULT_USERS, indent=4), encoding="utf-8")
        return DEFAULT_USERS.copy()

def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=4), encoding="utf-8")

def password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = load_users()

# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_ANNUNCIATOR = [
    "OC & EF TRIP",
    "MST TRIP",
    "LV3 WTI TRIP",
    "LV4 WTI ALM",
    "TCS OPTD",
    "AC FAIL",
    "LV4 WTI TRIP",
    "HV WTI ALM",
    "DC FAIL",
    "DIFF. OPTD",
    "HV WTI TRIP",
    "OTI ALM",
    "PT FUSE",
    "LV1 WTI ALM",
    "OTI TRIP",
    "BUCH ALM",
    "LV1 WTI TRIP",
    "LV2 WTI ALM",
    "BUCH TRIP",
    "MOG ALM",
    "LV2 WTI ALM",
    "LV3 WTI ALM",
    "PRV TRIP1",
    "PRV TRIP2",
]

DEFAULT_RELAY = [
    "50 Operated",
    "51 Operated",
    "50N Operated",
    "51N Operated",
    "95_1 Operated",
    "95_2 Operated",
    "59 Operated",
    "27 Operated",
    "86 Operated",
    "Remote",
    "Spring Charge",
    "Test",
    "Service",
    "Earth Switch",
    "Communication Error",
]

DEFAULT_MFM = [
    ("Voltage", "kV"),
    ("Current", "A"),
    ("Active Power", "MW"),
    ("Reactive Power", "MVAr"),
    ("Apparent Power", "MVA"),
    ("Power Factor", "PF"),
    ("Frequency", "Hz"),
    ("Energy", "MWh"),
]

DEFAULT_DI = [
    "CB Trip",
    "CB Close",
]

DEFAULT_INV_ANALOG = [
    ("DC Voltage", "V"),
    ("DC Current", "A"),
    ("DC Power", "kW"),
    ("Phase-1 Voltage", "V"),
    ("Phase-1 Current", "A"),
    ("Phase-2 Voltage", "V"),
    ("Phase-2 Current", "A"),
    ("Phase-3 Voltage", "V"),
    ("Phase-3 Current", "A"),
    ("Active Power", "kW"),
    ("Reactive Power", "kVAr"),
    ("Apparent Power", "kVA"),
    ("Power Factor", "PF"),
    ("Grid Frequency", "Hz"),
    ("Efficiency", "%"),
    ("Today Energy Produced", "kWh"),
    ("Monthly Energy Produced", "MWh"),
    ("Total Energy Produced", "MWh"),
    ("Internal Temperature", "°C"),
    ("Temperature-1", "°C"),
    ("Temperature-2", "°C"),
    ("Temperature-3", "°C"),
    ("Temperature-4", "°C"),
    ("Temperature-5", "°C"),
    ("Temperature-6", "°C"),
    ("N Voltage to Ground", "V"),
    ("N Resistance to Ground", "Ohm"),
    ("P Resistance to Ground", "Ohm"),
]

DEFAULT_INV_DIGITAL = [
    "Running",
    "Fault",
    "Warning",
    "Communication Error",
]

def default_ht_panel(name="HT Panel-01"):
    return {
        "name": name,
        "equipment": {
            "MFM": {
                "enabled": True,
                "signals": [x[0] for x in DEFAULT_MFM],
            },
            "Relay": {
                "enabled": True,
                "signals": DEFAULT_RELAY.copy(),
            },
            "Annunciator": {
                "enabled": True,
                "signals": DEFAULT_ANNUNCIATOR.copy(),
            },
            "DI": {
                "enabled": True,
                "signals": DEFAULT_DI.copy(),
            },
        },
    }

def default_block(name="Block-01"):
    return {
        "name": name,
        "status": "Enabled",
        "inverters": 4,
        "scbs": 1,
        "ht_panels": [default_ht_panel("HT Panel-01")],
    }

# ============================================================
# SESSION STATE
# ============================================================

if "login" not in st.session_state:
    st.session_state.login = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "blocks" not in st.session_state:
    st.session_state.blocks = [default_block()]

if "weather_count" not in st.session_state:
    st.session_state.weather_count = 2

if "protocol" not in st.session_state:
    st.session_state.protocol = "OPC UA"

if "server_ip" not in st.session_state:
    st.session_state.server_ip = "192.168.1.100"

if "port" not in st.session_state:
    st.session_state.port = 4840

if "trend_seconds" not in st.session_state:
    st.session_state.trend_seconds = {}

# ============================================================
# HELPERS
# ============================================================

def signal_key(prefix, block_idx, ht_idx, eq_type, signal):
    clean = "".join(ch if ch.isalnum() else "_" for ch in signal)
    return f"{prefix}_{block_idx}_{ht_idx}_{eq_type}_{clean}"

def demo_bool(seed_text):
    # Stable demo state. Replace with OPC-UA value later.
    return (sum(ord(c) for c in seed_text) % 3) == 0

def demo_numeric(signal, equipment_index=0):
    base = sum(ord(c) for c in signal) % 100
    if "Voltage" in signal:
        return round(590 + (base % 15), 2)
    if "Current" in signal:
        return round(100 + (base % 180), 2)
    if "Power Factor" in signal or signal == "Power Factor":
        return round(0.90 + ((base % 10) / 100), 2)
    if "Frequency" in signal:
        return 50.0
    if "Temperature" in signal:
        return round(35 + (base % 20), 2)
    if "Energy" in signal:
        return round(100 + (base * 1.7), 2)
    if "Power" in signal:
        return round(0.5 + (base / 10), 2)
    if "Resistance" in signal:
        return round(1000 + base * 20, 2)
    return round(10 + base / 5, 2)

def make_trend(signal, unit="", period="1 min", digital=False):
    points = {
        "1 sec": 60,
        "1 min": 60,
        "15 min": 48,
        "30 min": 48,
        "1 hour": 48,
    }.get(period, 60)

    step = {
        "1 sec": 1,
        "1 min": 60,
        "15 min": 900,
        "30 min": 1800,
        "1 hour": 3600,
    }.get(period, 60)

    end = datetime.now()
    times = [end - timedelta(seconds=step * (points - 1 - i)) for i in range(points)]

    seed = sum(ord(c) for c in signal)
    rng = np.random.default_rng(seed)

    if digital:
        values = [(i + seed) % 5 == 0 for i in range(points)]
        display = [1 if v else 0 for v in values]
    else:
        base = demo_numeric(signal)
        noise = rng.normal(0, max(abs(base) * 0.015, 0.02), points)
        display = np.maximum(0, base + noise)

    return pd.DataFrame({
        "Time": times,
        "Value": display,
        "Signal": signal,
    })

def show_trend(signal, unit="", title=None, period="1 min", digital=False, key=None):
    df = make_trend(signal, unit, period, digital)

    if digital:
        df["Status"] = df["Value"].map({0: "FALSE", 1: "TRUE"})
        fig = px.line(
            df,
            x="Time",
            y="Value",
            title=title or signal,
            markers=True,
        )
        fig.update_traces(line_shape="hv")
        fig.update_yaxes(
            tickvals=[0, 1],
            ticktext=["FALSE", "TRUE"],
            title="Digital State",
            range=[-0.1, 1.1],
        )
    else:
        fig = px.line(
            df,
            x="Time",
            y="Value",
            title=title or f"{signal} Trend",
        )
        fig.update_yaxes(title=f"{signal} ({unit})" if unit else signal)

    fig.update_layout(height=320, margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(fig, use_container_width=True, key=key)

def equipment_signal_card(eq_type, signal, unit="", block_idx=0, ht_idx=0, signal_idx=0):
    digital = eq_type in ("Relay", "Annunciator", "DI")
    if digital:
        state = demo_bool(f"{block_idx}-{ht_idx}-{eq_type}-{signal}")
        if state:
            st.error(f"🔴 TRUE — {signal}")
        else:
            st.success(f"🟢 FALSE — {signal}")
        st.caption("Demo state; OPC-UA mapping will replace this value.")
    else:
        value = demo_numeric(signal)
        st.metric(signal, f"{value} {unit}" if unit else value)

# ============================================================
# LOGIN
# ============================================================

if not st.session_state.login:
    st.markdown(
        """
        <div style="text-align:center;padding:20px 0 10px 0;">
            <div style="font-size:48px;">☀️</div>
            <h1 style="margin:0;">SOLAR HEART</h1>
            <p style="font-size:18px;">Industrial Solar SCADA Monitoring System</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Secure Login")
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter password")

        if st.button("🚀 Login", use_container_width=True, type="primary"):
            record = users.get(username.strip())
            if record and password_hash(password) == record.get("password_hash"):
                st.session_state.login = True
                st.session_state.username = username.strip()
                st.session_state.role = record.get("role", "Operator")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

        st.info("Default users: admin / admin123 | operator / operator123 | supervisor / supervisor123")

    st.markdown("---")
    st.caption(f"{APP_NAME} v{VERSION} | Role Based Access Control")
    st.stop()

# ============================================================
# COMMON TOTALS
# ============================================================

blocks = st.session_state.blocks
total_blocks = len(blocks)
total_inverters = sum(int(b["inverters"]) for b in blocks)
total_scbs = sum(int(b["scbs"]) for b in blocks)
total_ht_panels = sum(len(b["ht_panels"]) for b in blocks)

total_mfms = sum(
    sum(1 for p in b["ht_panels"] if p["equipment"]["MFM"]["enabled"])
    for b in blocks
)
total_relays = sum(
    sum(1 for p in b["ht_panels"] if p["equipment"]["Relay"]["enabled"])
    for b in blocks
)
total_ann = sum(
    sum(1 for p in b["ht_panels"] if p["equipment"]["Annunciator"]["enabled"])
    for b in blocks
)

running_inverters = total_inverters
fault_inverters = 0

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("☀️ SOLAR HEART")
st.sidebar.success("🟢 Plant Online")
st.sidebar.write(f"👤 User : {st.session_state.username}")
st.sidebar.write(f"🛡️ Role : {st.session_state.role}")
st.sidebar.write("🏭 Plant : 250 MW")
st.sidebar.write("📍 Location : Rajasthan")
st.sidebar.write("🕒 Time : " + datetime.now().strftime("%H:%M:%S"))
st.sidebar.markdown("---")

allowed_pages = ROLE_PAGES.get(st.session_state.role, ["Dashboard"])
page = st.sidebar.radio("Navigation", allowed_pages)

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.login = False
    st.rerun()

# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":
    st.title("☀️ SOLAR HEART")
    st.subheader("Industrial Solar SCADA Monitoring System")
    st.success("🟢 Plant Status : HEALTHY")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ Generation", "245 MW")
    c2.metric("🔋 Today's Energy", "1850 MWh")
    c3.metric("🟢 Running Inverters", running_inverters)
    c4.metric("🔴 Fault Inverters", fault_inverters)

    st.markdown("---")

    chart = pd.DataFrame({
        "Hour": list(range(6, 19)),
        "Generation (MW)": [10, 35, 70, 120, 170, 210, 240, 245, 238, 210, 180, 120, 40],
    })
    fig = px.line(chart, x="Hour", y="Generation (MW)", markers=True,
                  title="Daily Generation Curve")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("🏭 Plant Information")
        st.info(
            f"Plant Capacity : 250 MW\n\n"
            f"Location : Rajasthan\n\n"
            f"Total Blocks : {total_blocks}\n\n"
            f"Total Inverters : {total_inverters}\n\n"
            f"Total SCBs : {total_scbs}\n\n"
            f"Total HT Panels : {total_ht_panels}\n\n"
            f"Total MFM : {total_mfms}\n\n"
            f"Total Relays : {total_relays}\n\n"
            f"Annunciators : {total_ann}"
        )

    with right:
        st.subheader("🟢 Quick Status")
        st.success("Weather Station : Healthy")
        st.success("SCADA Server : Healthy")
        st.success("Historian : Healthy")
        st.success("Database : Healthy")
        st.success("OPC UA : Ready for mapping")

# ============================================================
# PLANT MIMIC
# ============================================================

elif page == "Plant Mimic":
    st.title("🗺️ Solar Plant Mimic")
    st.success("🟢 Plant Communication Healthy")

    st.markdown("## ⚡ GRID")
    st.info("Grid Status : ON")
    st.markdown("⬇️")

    st.markdown("## 🔌 MAIN TRANSFORMER")
    st.success("🟢 Transformer Healthy")
    st.markdown("⬇️")

    for block_idx, block in enumerate(blocks):
        with st.container(border=True):
            st.markdown(f"### 🏗️ {block['name']}")
            st.success(f"🟢 {block['name']} : {block['status']}")

            cols = st.columns(4)
            for i in range(int(block["inverters"])):
                with cols[i % 4]:
                    st.success(f"⚡ INV-{i+1:03d}")
                    st.caption("AC Power: 2.10 MW | Running")

            st.markdown("#### 🏭 HT Panels")
            ht_cols = st.columns(4)
            for ht_idx, panel in enumerate(block["ht_panels"]):
                with ht_cols[ht_idx % 4]:
                    st.info(f"🏭 {panel['name']}")
                    st.caption("MFM + Relay + ANN + DI")

# ============================================================
# PLANT CONFIGURATION
# ============================================================

elif page == "Plant Configuration":
    st.title("⚙️ Plant & Equipment Configuration")
    st.caption(
        "Block, inverter, SCB and HT Panel configuration. "
        "Each HT Panel can have equipment and signals added/removed."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Blocks", total_blocks)
    c2.metric("Inverters", total_inverters)
    c3.metric("SCBs", total_scbs)
    c4.metric("HT Panels", total_ht_panels)
    c5.metric("MFM / Relay", f"{total_mfms} / {total_relays}")

    st.markdown("---")

    # ---------------- Block management ----------------
    st.subheader("🧱 Block Management")
    a1, a2, a3 = st.columns([1, 1, 3])

    with a1:
        if st.button("➕ Add Block", use_container_width=True):
            n = len(st.session_state.blocks) + 1
            st.session_state.blocks.append(default_block(f"Block-{n:02d}"))
            st.rerun()

    with a2:
        if st.button("➖ Remove Last Block", use_container_width=True):
            if len(st.session_state.blocks) > 1:
                st.session_state.blocks.pop()
                st.rerun()
            else:
                st.warning("At least one block is required.")

    with a3:
        st.info("Default: 4 Inverters per Block. You can increase/decrease it.")

    # ---------------- Block editor ----------------
    for bidx, block in enumerate(st.session_state.blocks):
        with st.container(border=True):
            st.subheader(f"🏗️ {block['name']}")

            c1, c2 = st.columns(2)
            with c1:
                block_name = st.text_input(
                    "Block Name",
                    value=block["name"],
                    key=f"cfg_block_name_{bidx}",
                )
            with c2:
                block_status = st.selectbox(
                    "Block Status",
                    ["Enabled", "Disabled"],
                    index=0 if block["status"] == "Enabled" else 1,
                    key=f"cfg_block_status_{bidx}",
                )

            e1, e2 = st.columns(2)
            with e1:
                inv_count = st.number_input(
                    "⚡ Number of Inverters",
                    min_value=0, max_value=500,
                    value=int(block["inverters"]),
                    step=1, key=f"cfg_inv_{bidx}",
                )
            with e2:
                scb_count = st.number_input(
                    "🔌 Number of SCBs",
                    min_value=0, max_value=1000,
                    value=int(block["scbs"]),
                    step=1, key=f"cfg_scb_{bidx}",
                )

            if st.button("💾 Save Block", key=f"save_block_{bidx}", use_container_width=True):
                block["name"] = block_name
                block["status"] = block_status
                block["inverters"] = int(inv_count)
                block["scbs"] = int(scb_count)
                st.session_state.blocks[bidx] = block
                st.success(f"Saved {block_name}")
                st.rerun()

            st.markdown("---")
            st.markdown("### 🏭 HT Panel Configuration")

            if st.button(
                "➕ Add HT Panel",
                key=f"add_ht_{bidx}",
            ):
                n = len(block["ht_panels"]) + 1
                block["ht_panels"].append(default_ht_panel(f"HT Panel-{n:02d}"))
                st.rerun()

            for hidx, panel in enumerate(block["ht_panels"]):
                with st.container(border=True):
                    top1, top2, top3 = st.columns([3, 1, 1])

                    with top1:
                        new_panel_name = st.text_input(
                            "HT Panel Name",
                            value=panel["name"],
                            key=f"ht_name_{bidx}_{hidx}",
                        )

                    with top2:
                        if st.button(
                            "💾 Save Name",
                            key=f"save_ht_name_{bidx}_{hidx}",
                            use_container_width=True,
                        ):
                            panel["name"] = new_panel_name
                            st.success("HT Panel name saved.")
                            st.rerun()

                    with top3:
                        if st.button(
                            "🗑️ Remove",
                            key=f"remove_ht_{bidx}_{hidx}",
                            use_container_width=True,
                        ):
                            if len(block["ht_panels"]) > 1:
                                block["ht_panels"].pop(hidx)
                                st.rerun()
                            else:
                                st.warning("Keep at least one HT Panel.")

                    st.markdown(f"#### {panel['name']} → Equipment")

                    eq_cols = st.columns(4)
                    for eq_col, eq_type in zip(
                        eq_cols, ["MFM", "Relay", "Annunciator", "DI"]
                    ):
                        with eq_col:
                            eq = panel["equipment"][eq_type]
                            enabled = st.checkbox(
                                f"Enable {eq_type}",
                                value=eq["enabled"],
                                key=f"enable_{bidx}_{hidx}_{eq_type}",
                            )
                            eq["enabled"] = enabled

                    st.markdown("##### ➕ / ➖ Signals")

                    # ---- MFM ----
                    if panel["equipment"]["MFM"]["enabled"]:
                        with st.expander("📊 MFM Signals", expanded=True):
                            for sidx, signal in enumerate(
                                panel["equipment"]["MFM"]["signals"]
                            ):
                                c1, c2 = st.columns([5, 1])
                                with c1:
                                    st.text_input(
                                        "Signal",
                                        value=signal,
                                        key=f"mfm_signal_{bidx}_{hidx}_{sidx}",
                                        label_visibility="collapsed",
                                    )
                                with c2:
                                    if st.button(
                                        "🗑️",
                                        key=f"del_mfm_{bidx}_{hidx}_{sidx}",
                                    ):
                                        panel["equipment"]["MFM"]["signals"].pop(sidx)
                                        st.rerun()

                            new_mfm = st.text_input(
                                "New MFM Signal",
                                placeholder="Example: Bus Voltage",
                                key=f"new_mfm_{bidx}_{hidx}",
                            )
                            if st.button("➕ Add MFM Signal", key=f"add_mfm_{bidx}_{hidx}"):
                                if new_mfm.strip():
                                    panel["equipment"]["MFM"]["signals"].append(new_mfm.strip())
                                    st.rerun()

                    # ---- Relay ----
                    if panel["equipment"]["Relay"]["enabled"]:
                        with st.expander("🛡 Relay Signals", expanded=False):
                            for sidx, signal in enumerate(
                                panel["equipment"]["Relay"]["signals"]
                            ):
                                c1, c2 = st.columns([5, 1])
                                with c1:
                                    st.text_input(
                                        "Signal",
                                        value=signal,
                                        key=f"relay_signal_{bidx}_{hidx}_{sidx}",
                                        label_visibility="collapsed",
                                    )
                                with c2:
                                    if st.button(
                                        "🗑️",
                                        key=f"del_relay_{bidx}_{hidx}_{sidx}",
                                    ):
                                        panel["equipment"]["Relay"]["signals"].pop(sidx)
                                        st.rerun()

                            new_relay = st.text_input(
                                "New Relay Signal",
                                placeholder="Example: 67 Operated",
                                key=f"new_relay_{bidx}_{hidx}",
                            )
                            if st.button("➕ Add Relay Signal", key=f"add_relay_{bidx}_{hidx}"):
                                if new_relay.strip():
                                    panel["equipment"]["Relay"]["signals"].append(new_relay.strip())
                                    st.rerun()

                    # ---- Annunciator ----
                    if panel["equipment"]["Annunciator"]["enabled"]:
                        with st.expander("🚨 Annunciator Signals", expanded=False):
                            for sidx, signal in enumerate(
                                panel["equipment"]["Annunciator"]["signals"]
                            ):
                                c1, c2 = st.columns([5, 1])
                                with c1:
                                    st.text_input(
                                        "Signal",
                                        value=signal,
                                        key=f"ann_signal_{bidx}_{hidx}_{sidx}",
                                        label_visibility="collapsed",
                                    )
                                with c2:
                                    if st.button(
                                        "🗑️",
                                        key=f"del_ann_{bidx}_{hidx}_{sidx}",
                                    ):
                                        panel["equipment"]["Annunciator"]["signals"].pop(sidx)
                                        st.rerun()

                            new_ann = st.text_input(
                                "New Annunciator Signal",
                                placeholder="Example: OTI ALM",
                                key=f"new_ann_{bidx}_{hidx}",
                            )
                            if st.button("➕ Add Annunciator Signal", key=f"add_ann_{bidx}_{hidx}"):
                                if new_ann.strip():
                                    panel["equipment"]["Annunciator"]["signals"].append(new_ann.strip())
                                    st.rerun()

                    # ---- DI ----
                    if panel["equipment"]["DI"]["enabled"]:
                        with st.expander("🔘 DI / Breaker Signals", expanded=True):
                            for sidx, signal in enumerate(
                                panel["equipment"]["DI"]["signals"]
                            ):
                                c1, c2 = st.columns([5, 1])
                                with c1:
                                    st.text_input(
                                        "Signal",
                                        value=signal,
                                        key=f"di_signal_{bidx}_{hidx}_{sidx}",
                                        label_visibility="collapsed",
                                    )
                                with c2:
                                    if st.button(
                                        "🗑️",
                                        key=f"del_di_{bidx}_{hidx}_{sidx}",
                                    ):
                                        panel["equipment"]["DI"]["signals"].pop(sidx)
                                        st.rerun()

                            new_di = st.text_input(
                                "New DI Signal",
                                placeholder="Example: Earth Switch",
                                key=f"new_di_{bidx}_{hidx}",
                            )
                            if st.button("➕ Add DI Signal", key=f"add_di_{bidx}_{hidx}"):
                                if new_di.strip():
                                    panel["equipment"]["DI"]["signals"].append(new_di.strip())
                                    st.rerun()

    st.markdown("---")
    st.subheader("🌐 Communication Configuration")

    protocol = st.selectbox(
        "Communication Protocol",
        ["OPC UA", "Modbus TCP", "IEC 60870-5-104", "IEC 61850"],
        index=["OPC UA", "Modbus TCP", "IEC 60870-5-104", "IEC 61850"].index(
            st.session_state.protocol
        ),
    )
    server_ip = st.text_input(
        "SCADA / OPC UA Server IP",
        value=st.session_state.server_ip,
    )
    port = st.number_input(
        "Communication Port",
        min_value=1, max_value=65535,
        value=int(st.session_state.port),
        step=1,
    )

    if st.button("💾 Save Communication Configuration", use_container_width=True):
        st.session_state.protocol = protocol
        st.session_state.server_ip = server_ip
        st.session_state.port = int(port)
        st.success("Communication configuration saved.")

# ============================================================
# HT PANELS
# ============================================================

elif page == "HT Panels":
    st.title("🏭 HT Panel Monitoring")
    st.caption("HT Panel → MFM / Relay / Annunciator / DI")

    period = st.selectbox(
        "Trend Interval",
        ["1 sec", "1 min", "15 min", "30 min", "1 hour"],
        key="ht_trend_period",
    )

    for bidx, block in enumerate(blocks):
        st.markdown(f"## 🧱 {block['name']}")

        for hidx, panel in enumerate(block["ht_panels"]):
            with st.container(border=True):
                st.subheader(f"🏭 {panel['name']}")

                # Equipment tabs
                tabs = st.tabs(["📊 MFM", "🛡 Relay", "🚨 Annunciator", "🔘 DI"])

                # MFM
                with tabs[0]:
                    eq = panel["equipment"]["MFM"]
                    if not eq["enabled"]:
                        st.warning("MFM disabled in configuration.")
                    else:
                        cols = st.columns(4)
                        for idx, signal in enumerate(eq["signals"]):
                            unit = next((u for n, u in DEFAULT_MFM if n == signal), "")
                            with cols[idx % 4]:
                                equipment_signal_card(
                                    "MFM", signal, unit, bidx, hidx, idx
                                )

                        st.markdown("---")
                        st.subheader("📈 MFM Trend")
                        trend_signal = st.selectbox(
                            "Select MFM Signal",
                            eq["signals"],
                            key=f"ht_mfm_trend_signal_{bidx}_{hidx}",
                        )
                        unit = next((u for n, u in DEFAULT_MFM if n == trend_signal), "")
                        show_trend(
                            trend_signal,
                            unit,
                            f"{panel['name']} - MFM - {trend_signal}",
                            period,
                            False,
                            key=f"trend_mfm_{bidx}_{hidx}",
                        )

                # Relay
                with tabs[1]:
                    eq = panel["equipment"]["Relay"]
                    if not eq["enabled"]:
                        st.warning("Relay disabled in configuration.")
                    else:
                        cols = st.columns(3)
                        for idx, signal in enumerate(eq["signals"]):
                            with cols[idx % 3]:
                                equipment_signal_card(
                                    "Relay", signal, "", bidx, hidx, idx
                                )

                        st.markdown("---")
                        st.subheader("📈 Relay Trend")
                        trend_signal = st.selectbox(
                            "Select Relay Signal",
                            eq["signals"],
                            key=f"ht_relay_trend_signal_{bidx}_{hidx}",
                        )
                        show_trend(
                            trend_signal,
                            "",
                            f"{panel['name']} - Relay - {trend_signal}",
                            period,
                            True,
                            key=f"trend_relay_{bidx}_{hidx}",
                        )

                # Annunciator
                with tabs[2]:
                    eq = panel["equipment"]["Annunciator"]
                    if not eq["enabled"]:
                        st.warning("Annunciator disabled in configuration.")
                    else:
                        cols = st.columns(4)
                        for idx, signal in enumerate(eq["signals"]):
                            with cols[idx % 4]:
                                equipment_signal_card(
                                    "Annunciator", signal, "", bidx, hidx, idx
                                )

                        st.markdown("---")
                        st.subheader("📈 Annunciator Trend")
                        trend_signal = st.selectbox(
                            "Select Annunciator Signal",
                            eq["signals"],
                            key=f"ht_ann_trend_signal_{bidx}_{hidx}",
                        )
                        show_trend(
                            trend_signal,
                            "",
                            f"{panel['name']} - Annunciator - {trend_signal}",
                            period,
                            True,
                            key=f"trend_ann_{bidx}_{hidx}",
                        )

                # DI
                with tabs[3]:
                    eq = panel["equipment"]["DI"]
                    if not eq["enabled"]:
                        st.warning("DI disabled in configuration.")
                    else:
                        cols = st.columns(4)
                        for idx, signal in enumerate(eq["signals"]):
                            state = demo_bool(f"DI-{bidx}-{hidx}-{signal}")
                            with cols[idx % 4]:
                                if state:
                                    st.error(f"🔴 {signal} : TRUE")
                                else:
                                    st.success(f"🟢 {signal} : FALSE")
                                st.caption("Digital status")

                        st.markdown("---")
                        st.subheader("📈 DI Trend")
                        trend_signal = st.selectbox(
                            "Select DI Signal",
                            eq["signals"],
                            key=f"ht_di_trend_signal_{bidx}_{hidx}",
                        )
                        show_trend(
                            trend_signal,
                            "",
                            f"{panel['name']} - DI - {trend_signal}",
                            period,
                            True,
                            key=f"trend_di_{bidx}_{hidx}",
                        )

# ============================================================
# INVERTERS
# ============================================================

elif page == "Inverters":
    st.title("⚡ Inverter Monitoring")
    st.success("🟢 Inverter Communication Healthy")

    st.info(
        "Each inverter is modeled with Unit-1, Unit-2 and Unit-3, "
        "matching the equipment screen you provided."
    )

    period = st.selectbox(
        "Trend Interval",
        ["1 sec", "1 min", "15 min", "30 min", "1 hour"],
        key="inv_trend_period",
    )

    inv_no = 1

    for bidx, block in enumerate(blocks):
        st.markdown(f"## 🧱 {block['name']}")

        for i in range(int(block["inverters"])):
            inv_name = f"INV-{inv_no:03d}"

            with st.container(border=True):
                st.subheader(f"⚡ {inv_name}")

                tabs = st.tabs(["Overview", "Unit-1", "Unit-2", "Unit-3", "Trend"])

                with tabs[0]:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Status", "RUNNING")
                    c2.metric("AC Power", "237.19 kW")
                    c3.metric("DC Voltage", "1228 V")
                    c4.metric("Efficiency", "98.1 %")

                for unit_no, unit_tab in enumerate(tabs[1:4], start=1):
                    with unit_tab:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("DC Voltage", f"{1220 + unit_no * 4} V")
                        c2.metric("DC Current", f"{180 + unit_no * 5} A")
                        c3.metric("DC Power", f"{210 + unit_no * 8} kW")

                        c4, c5, c6 = st.columns(3)
                        c4.metric("AC Voltage", f"{590 + unit_no} V")
                        c5.metric("AC Current", f"{240 + unit_no} A")
                        c6.metric("Active Power", f"{230 + unit_no * 3} kW")

                        st.markdown("**Additional parameters**")
                        st.write(
                            "Reactive Power: 84.74 kVAr | "
                            "Apparent Power: 251.87 kVA | "
                            "PF: 0.94 | Frequency: 50 Hz"
                        )
                        st.write(
                            "Internal Temp: 37 °C | "
                            "Temperature-1: 47 °C | "
                            "Temperature-2: -30 °C"
                        )

                with tabs[4]:
                    trend_signal = st.selectbox(
                        "Inverter analog signal",
                        [x[0] for x in DEFAULT_INV_ANALOG],
                        key=f"inv_signal_{bidx}_{i}",
                    )
                    unit = next(
                        (u for n, u in DEFAULT_INV_ANALOG if n == trend_signal),
                        "",
                    )
                    show_trend(
                        trend_signal,
                        unit,
                        f"{inv_name} - {trend_signal}",
                        period,
                        False,
                        key=f"inv_trend_{bidx}_{i}",
                    )

            inv_no += 1

# ============================================================
# WEATHER
# ============================================================

elif page == "Weather":
    st.title("🌤 Weather Station")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("☀️ Irradiance", "890 W/m²")
    c2.metric("🌡 Ambient Temp", "35°C")
    c3.metric("🔥 Module Temp", "48°C")
    c4.metric("💨 Wind Speed", "6.2 m/s")

    weather = pd.DataFrame({
        "Hour": list(range(6, 18)),
        "Irradiance (W/m²)": [120, 240, 410, 620, 760, 850, 900, 890, 860, 780, 620, 300],
    })
    fig = px.area(weather, x="Hour", y="Irradiance (W/m²)",
                  title="Solar Irradiance")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# COMMUNICATION
# ============================================================

elif page == "Communication":
    st.title("🌐 Communication Monitoring")
    st.success("🟢 SCADA Communication System")

    c1, c2, c3 = st.columns(3)
    c1.metric("Protocol", st.session_state.protocol)
    c2.metric("Server", st.session_state.server_ip)
    c3.metric("Port", st.session_state.port)

    st.markdown("---")
    communication = pd.DataFrame({
        "Device": [
            "SCADA Server", "Historian Server", "PLC",
            "Inverter Network", "Weather Station", "MFM",
            "Protection Relay", "HT Panel",
        ],
        "Protocol": [
            "TCP/IP", "TCP/IP", "OPC UA", "OPC UA",
            "OPC UA", "Modbus TCP", "IEC 61850", "IEC 61850",
        ],
        "Status": ["Healthy"] * 8,
        "Latency (ms)": [2, 3, 5, 8, 10, 8, 5, 6],
    })
    st.dataframe(communication, use_container_width=True, hide_index=True)

    st.info(
        "Next step: replace the demo values with the actual OPC-UA endpoint "
        "and Node IDs from your SCADA."
    )

# ============================================================
# ALARMS
# ============================================================

elif page == "Alarms":
    st.title("🚨 Alarm Management")

    alarms = pd.DataFrame({
        "Time": ["10:20", "11:45", "12:30", "14:10"],
        "Device": ["INV-003", "Weather Station", "SCB-012", "HT Panel-01"],
        "Alarm": ["AC Fault", "Communication Lost", "Fuse Failure", "CB Trip"],
        "Priority": ["High", "Medium", "High", "High"],
        "Status": ["Active", "Active", "Active", "Active"],
    })
    st.dataframe(alarms, use_container_width=True, hide_index=True)

# ============================================================
# ALL TRENDS
# ============================================================

elif page == "Trends":
    st.title("📈 Analog & Digital Trend Viewer")

    period = st.selectbox(
        "Trend Interval",
        ["1 sec", "1 min", "15 min", "30 min", "1 hour"],
        key="global_trend_period",
    )

    block_names = [b["name"] for b in blocks]
    selected_block_name = st.selectbox(
        "🏗️ Block",
        block_names,
        key="global_trend_block",
    )
    selected_block = blocks[block_names.index(selected_block_name)]

    source = st.selectbox(
        "Equipment Type",
        ["Inverter", "HT Panel", "MFM", "Relay", "Annunciator", "DI"],
        key="global_trend_source",
    )

    equipment_name = ""
    if source == "Inverter":
        inv_count = int(selected_block["inverters"])
        if inv_count > 0:
            inv_no = st.selectbox(
                "Inverter",
                list(range(1, inv_count + 1)),
                format_func=lambda n: f"{selected_block_name} → INV-{n:03d}",
                key="global_trend_inv",
            )
            equipment_name = f"INV-{inv_no:03d}"
        signals = DEFAULT_INV_ANALOG
        digital = False

    elif source == "HT Panel":
        panels = selected_block["ht_panels"]
        panel_names = [p["name"] for p in panels]
        equipment_name = st.selectbox(
            "HT Panel",
            panel_names,
            key="global_trend_ht",
        )
        signals = [("Panel Status", "")]
        digital = True

    else:
        panels = selected_block["ht_panels"]
        panel_names = [p["name"] for p in panels]
        panel_name = st.selectbox(
            "HT Panel",
            panel_names,
            key=f"global_trend_panel_{source}",
        )
        panel = panels[panel_names.index(panel_name)]
        equipment_name = panel_name

        eq_type = source
        if source in panel["equipment"]:
            eq = panel["equipment"][eq_type]
            if not eq["enabled"]:
                st.warning(f"{source} is disabled in this HT Panel.")
                signals = []
                digital = source != "MFM"
            else:
                if source == "MFM":
                    signals = [
                        (s, next((u for n, u in DEFAULT_MFM if n == s), ""))
                        for s in eq["signals"]
                    ]
                    digital = False
                    equipment_name = f"{panel_name} → MFM"
                else:
                    signals = [(s, "") for s in eq["signals"]]
                    digital = True
                    equipment_name = f"{panel_name} → {source}"
        else:
            signals = []
            digital = True

    if not signals:
        st.info("No signals configured for this equipment.")
    else:
        signal_names = [x[0] for x in signals]
        signal = st.selectbox(
            "Signal",
            signal_names,
            key="global_trend_signal",
        )
        unit = next((u for n, u in signals if n == signal), "")

        st.info(
            f"📍 **Trend Source:** {selected_block_name} → "
            f"{equipment_name} → {signal}"
        )

        show_trend(
            signal,
            unit,
            f"{selected_block_name} - {equipment_name} - {signal}",
            period,
            digital,
            key="global_trend_chart",
        )

        st.caption(
            "Digital signals are displayed as TRUE/FALSE. "
            "For example, CB Trip = TRUE while the trip condition is active "
            "and FALSE when inactive."
        )


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":
    st.title("📄 Reports")

    report = pd.DataFrame({
        "Report": [
            "Daily Generation",
            "Monthly Generation",
            "Yearly Generation",
            "Alarm Report",
            "Inverter Report",
            "Weather Report",
            "Communication Report",
            "MFM Report",
            "Relay Report",
            "Annunciator Report",
            "HT Panel Report",
            "SCB Current Report",
        ],
        "Status": ["Ready"] * 12,
    })
    st.dataframe(report, use_container_width=True, hide_index=True)

# ============================================================
# SETTINGS
# ============================================================

elif page == "Settings":
    st.title("⚙️ System Settings")

    plant_name = st.text_input("Plant Name", "SOLAR HEART")
    location = st.text_input("Location", "Rajasthan")
    capacity = st.number_input("Plant Capacity (MW)", min_value=1, value=250)
    theme = st.selectbox("Theme", ["Light", "Dark"])

    st.markdown("---")
    st.subheader("🔐 Security")

    password_policy = st.selectbox(
        "Password Policy",
        [
            "Minimum 12 Characters",
            "Minimum 14 Characters",
            "Strong Password Policy",
        ],
    )
    audit_log = st.checkbox("Enable Audit Logging", value=True)

    st.markdown("---")
    st.subheader("👥 User Management")
    st.caption("Administrator only. Changes are saved locally in users.json.")

    if st.session_state.role == "Administrator":
        user_rows = []
        for uname, record in users.items():
            user_rows.append({"Username": uname, "Role": record.get("role", "")})
        st.dataframe(pd.DataFrame(user_rows), use_container_width=True, hide_index=True)

        selected_user = st.selectbox("Select User", list(users.keys()), key="selected_user")
        selected_role = st.selectbox(
            "Role",
            ["Administrator", "Operator", "Supervisor"],
            index=["Administrator", "Operator", "Supervisor"].index(users[selected_user].get("role", "Operator")),
            key="selected_role",
        )
        new_username = st.text_input("New Username", value=selected_user, key="new_username")
        new_password = st.text_input("New Password (leave blank to keep current)", type="password", key="new_password")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Update User", use_container_width=True):
                new_username = new_username.strip()
                if not new_username:
                    st.error("Username cannot be empty.")
                elif new_password and len(new_password) < 12:
                    st.error("Password must be at least 12 characters.")
                else:
                    record = users.pop(selected_user)
                    record["role"] = selected_role
                    if new_password:
                        record["password_hash"] = password_hash(new_password)
                    users[new_username] = record
                    save_users(users)
                    if selected_user == st.session_state.username:
                        st.session_state.username = new_username
                        st.session_state.role = selected_role
                    st.success("✅ User updated successfully.")
                    st.rerun()
        reset_password = st.text_input("Reset Password", type="password", key="reset_pw")
        if st.button("🔄 Reset Password", use_container_width=True):
            if len(reset_password) < 12:
                st.error("Password must be at least 12 characters.")
            else:
                users[selected_user]["password_hash"] = password_hash(reset_password)
                save_users(users)
                st.success("✅ Password reset successfully.")

    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings Saved Successfully")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(
    f"{APP_NAME} v{VERSION} | Industrial Solar SCADA Platform | "
    "Developed by Shashank Mani"
)