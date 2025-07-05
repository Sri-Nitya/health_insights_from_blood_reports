import streamlit as st
from database_handler import register_user
from utils.validation import is_valid_email

st.header("📝 Signup")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Signup"):
    if not email or not password:
        st.error("Please fill in both fields.")
    elif not is_valid_email(email):
        st.error("Invalid email format.")
    elif len(password) < 6:
        st.warning("Password should be at least 6 characters.")
    elif register_user(email, password):
        st.success("Account created! Please login from the sidebar.")
    else:
        st.error("Email already registered.")