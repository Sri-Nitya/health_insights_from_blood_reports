import streamlit as st
from database_handler import load_reports_for_user, save_report
from utils.ocr import extract_text_from_image
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_client import GeminiClient
import base64
import base64 as b64

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please login to access your dashboard.")
    st.stop()

st.header("Your Dashboard")

uploaded_file = st.file_uploader("Upload a new blood report", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_image(uploaded_file)

    if text and text.strip():
        with st.expander("🔍 View Extracted Text"):
            st.text_area("Extracted", text, height=200)

        with st.spinner("Analyzing with Gemini..."):
            gemini = GeminiClient(api_key="AIzaSyBR0LYlmRJUuwqDg_Cm9pSfKi5fZ5B5pG4")
            summary = gemini.get_summary(text)

        st.markdown("### 🧠 AI Health Summary")
        st.success(summary)

        file_bytes = uploaded_file.getvalue()
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        save_report(st.session_state.username, text, file_bytes, file_type, file_name)

        reports = load_reports_for_user(st.session_state.username) or []
        if len(reports) >= 2:
            st.markdown("### 📊 Health Progress Comparison")
            old_text = reports[-2]["text"]
            comparison = gemini.get_comparison(old_text, text)
            st.info(comparison)
    else:
        st.error("Text extraction failed.")


st.subheader("Previous Reports")
reports = load_reports_for_user(st.session_state.username) or []
if reports:
    for i, report in enumerate(reports, 1):
        st.markdown(f"**Report {i}:**")
        file_bytes = report.get("file_bytes")
        file_type = report.get("file_type")
        file_name = report.get("file_name", f"report_{i}")
        if file_bytes and file_type:
            file_bytes = base64.b64decode(file_bytes)
            if file_type == "application/pdf":
                st.download_button("Download PDF", file_bytes, file_name=file_name, mime=file_type, key=f"pdf_{i}")
                pdf_base64 = b64.b64encode(file_bytes).decode("utf-8")
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="400"></iframe>',
                    unsafe_allow_html=True
                )
            elif file_type.startswith("image/"):
                st.image(file_bytes, caption=file_name)
            else:
                st.info("Unsupported file type.")
        else:
            st.info("No file available for this report.")
else:
    st.info("No previous reports found.")