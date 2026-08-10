import streamlit as st


def plant_configuration():

    st.title(
        "⚙️ SOLAR HEART - Plant Configuration"
    )

    st.info(
        "Plant configuration is managed from the main SOLAR HEART application."
    )

    st.markdown("---")

    st.subheader(
        "🏭 Current Plant Configuration"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Plant Capacity",
            f"{st.session_state.get('capacity', 250)} MW"
        )

    with col2:

        st.metric(
            "Total Blocks",
            st.session_state.get('blocks', 4)
        )

    with col3:

        total_inverters = (
            st.session_state.get('blocks', 4)
            *
            st.session_state.get(
                'inverters_per_block',
                4
            )
        )

        st.metric(
            "Total Inverters",
            total_inverters
        )

    st.markdown("---")

    st.subheader(
        "🔌 HT Panel Equipment"
    )

    h1, h2, h3, h4 = st.columns(4)

    with h1:

        st.metric(
            "MFM",
            st.session_state.get(
                'mfm_count',
                15
            )
        )

    with h2:

        st.metric(
            "Relay",
            st.session_state.get(
                'relay_count',
                15
            )
        )

    with h3:

        st.metric(
            "Annunciator",
            st.session_state.get(
                'annunciator_count',
                15
            )
        )

    with h4:

        di = st.session_state.get(
            'di_count',
            32
        )

        do = st.session_state.get(
            'do_count',
            16
        )

        st.metric(
            "DI / DO",
            f"{di} / {do}"
        )

    st.markdown("---")

    st.caption(
        "SOLAR HEART Solar SCADA | Developed by Shashank Mani"
    )