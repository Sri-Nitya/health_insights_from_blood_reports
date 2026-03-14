import streamlit as st
from database_handler import authenticate_user, save_current_session


def login_page():

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(email, password):
            st.session_state.username = email
            save_current_session(email)
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()


