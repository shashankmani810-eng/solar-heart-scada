import streamlit as st


def login():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:25px;
        ">
            <h1>☀️ JAKCMS</h1>
            <h3>Industrial Solar SCADA Monitoring System</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.subheader("🔐 Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if username == "admin" and password == "admin123":

                st.session_state["login"] = True

                st.success(
                    "Login successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password"
                )