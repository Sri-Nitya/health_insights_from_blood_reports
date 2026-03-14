import streamlit as st
from utils.ocr import extract_text_from_image
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_client import GeminiClient

def guest_upload_page():

    st.title("📤 Upload Blood Report (Guest Mode)")

    st.write(
        "Upload a blood report and get **AI-powered health insights** instantly. "
        "Guest reports are not saved."
    )

    uploaded_file = st.file_uploader(
        "Upload a blood report",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    if uploaded_file:

        with st.spinner("Extracting report text..."):

            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_image(uploaded_file)

        if text and text.strip():

            with st.expander("🔍 View Extracted Text"):
                st.text_area("Extracted Text", text, height=200)

            with st.spinner("Analyzing report with AI..."):

                gemini = GeminiClient(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                summary = gemini.get_summary(text)

            st.markdown("### 🧠 AI Health Insights")
            st.success(summary)

            if "guest_full_inflight" not in st.session_state:
                st.session_state.guest_full_inflight = False
            if "guest_last_full" not in st.session_state:
                st.session_state.guest_last_full = None

            if not st.session_state.guest_full_inflight:
                if st.button("Read full explanation (detailed)", key="guest_full_explanation"):
                    st.session_state.guest_full_inflight = True
                    with st.spinner("Generating full explanation..."):
                        full = gemini.get_full_explanation(text)
                    st.session_state.guest_last_full = full
                    st.session_state.guest_full_inflight = False
                    with st.expander("📚 Full Medical Explanation"):
                        st.write(st.session_state.guest_last_full)
            else:
                st.info("Generating full explanation — please wait...")
                if st.session_state.guest_last_full:
                    with st.expander("📚 Full Medical Explanation"):
                        st.write(st.session_state.guest_last_full)

        else:
            st.error("Text extraction failed. Please upload a clearer report.")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back to Home"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button("🔐 Login to Save Reports"):
            st.session_state.page = "login"
            st.rerun()
