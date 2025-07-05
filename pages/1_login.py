import streamlit as st
from database_handler import authenticate_user
from utils.validation import is_valid_email

st.header("🔐 Login")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email or not password:
        st.error("Please fill in both fields.")
    elif not is_valid_email(email):
        st.error("Invalid email format.")
    elif authenticate_user(email, password):
        st.session_state.username = email
        st.success("Logged in successfully! Go to Home.")
    else:
        st.error("Invalid credentials.")