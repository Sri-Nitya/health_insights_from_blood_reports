import streamlit as st
from database_handler import load_reports_for_user
import base64

st.set_page_config(page_title="Blood Report Analyzer 🧬", page_icon="🩺", layout="centered")

with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "username" in st.session_state and st.session_state.username:
    st.title(f"Welcome back, {st.session_state.username}!")
    st.write("Here are your details and previous medical history:")

    reports = load_reports_for_user(st.session_state.username) or []
    if reports:
        for i, report in enumerate(reports, 1):
            st.markdown(f"**Report {i}:**")
            file_bytes = report.get("file_bytes")
            file_type = report.get("file_type")
            file_name = report.get("file_name", f"report_{i}")
            if file_bytes and file_type:
                if file_type == "application/pdf":
                    st.download_button("Download PDF", file_bytes, file_name=file_name, mime=file_type, key=f"pdf_{i}")
                    st.markdown(f'<iframe src="data:application/pdf;base64,{file_bytes.decode("latin1")}" width="700" height="400"></iframe>', unsafe_allow_html=True)
                elif file_type.startswith("image/"):
                    
                    if isinstance(file_bytes, str):
                        try:
                    
                            file_bytes = base64.b64decode(file_bytes)
                        except Exception:
                            
                            file_bytes = file_bytes.encode("latin1")
                    st.image(file_bytes, caption=file_name)
                else:
                    st.info("Unsupported file type.")
            else:
                st.info("No file available for this report.")
    else:
        st.info("No previous reports found.")

    if st.button("Logout"):
        st.session_state.username = None
        st.success("Logged out! Please use the sidebar to login or upload as guest.")
else:
    st.title("Welcome to Blood Report Analyzer 🧬")
    st.write("Use the sidebar to Login, Signup, or Upload as Guest.")