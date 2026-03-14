import streamlit as st
from database_handler import register_user
from utils.validation import is_valid_email


def signup_page():

    st.title("📝 Create Account")

    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):

        if not email or not username or not password:
            st.error("Please fill all fields.")
            return

        if not is_valid_email(email):
            st.error("Invalid email format.")
            return

        created = register_user(email, password, username)
        if created:
            st.success("Account created successfully!")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("User already exists.")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back to Home"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button("Already have an account? Login"):
            st.session_state.page = "login"
            st.rerun()
