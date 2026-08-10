# ============================================================
# ALARMS
# ============================================================

elif page == "Alarms":

    st.title("🚨 Alarm Management")

    st.subheader("🔴 Active Plant Alarms")

    alarms = pd.DataFrame({

        "Time": [
            "10:20:15",
            "11:45:22",
            "12:30:10",
            "14:10:45"
        ],

        "Device": [
            "INV-03",
            "Weather Station",
            "SCB-12",
            "INV-09"
        ],

        "Alarm": [
            "AC Fault",
            "Communication Lost",
            "Fuse Failure",
            "DC Over Voltage"
        ],

        "Priority": [
            "HIGH",
            "MEDIUM",
            "HIGH",
            "LOW"
        ],

        "Status": [
            "Active",
            "Active",
            "Active",
            "Active"
        ]
    })

    st.dataframe(
        alarms,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🔴 Total Alarms",
        "4"
    )

    c2.metric(
        "🔴 High Priority",
        "2"
    )

    c3.metric(
        "🟡 Medium Priority",
        "1"
    )

    c4.metric(
        "🔵 Low Priority",
        "1"
    )

    st.markdown("---")

    st.subheader("📋 Alarm Actions")

    selected_alarm = st.selectbox(
        "Select Alarm",
        [
            "INV-03 - AC Fault",
            "Weather Station - Communication Lost",
            "SCB-12 - Fuse Failure",
            "INV-09 - DC Over Voltage"
        ]
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button("✅ Acknowledge Alarm"):

            st.success(
                f"Alarm Acknowledged: {selected_alarm}"
            )

    with c2:

        if st.button("🔄 Reset Alarm"):

            st.info(
                f"Reset command issued for: {selected_alarm}"
            )