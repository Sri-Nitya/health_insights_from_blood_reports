import streamlit as st
from auth.login import login_page
from auth.signup import signup_page
from auth.guest_upload import guest_upload_page
from views.dashboard import dashboard_page
from database_handler import load_current_session

st.set_page_config(page_title="Blood Report Analyzer 🧬", page_icon="🩺")

if "username" not in st.session_state:
    st.session_state.username = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if not st.session_state.username:
    persisted = load_current_session()
    if persisted:
        st.session_state.username = persisted
        # If a user session exists, show dashboard by default
        if "page" not in st.session_state or st.session_state.page == "home":
            st.session_state.page = "dashboard"

if st.session_state.page == "home":

    st.title("🧬 Blood Report Analyzer")

    st.write(
        "Upload your blood report and get **AI-powered health insights**."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔐 Login"):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("📝 Sign Up"):
            st.session_state.page = "signup"
            st.rerun()

    with col3:
        if st.button("📤 Upload as Guest"):
            st.session_state.page = "guest_upload"
            st.rerun()


elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "signup":
    signup_page()

elif st.session_state.page == "guest_upload":
    guest_upload_page()

elif st.session_state.page == "dashboard":
    if not st.session_state.username:
        st.warning("Please login first")
        st.session_state.page = "login"
        st.rerun()
    dashboard_page()
