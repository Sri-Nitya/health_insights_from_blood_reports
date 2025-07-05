import streamlit as st
from utils.ocr import extract_text_from_image
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_client import GeminiClient

st.header("Upload as Guest")

uploaded_file = st.file_uploader("Upload a blood report", type=["pdf", "jpg", "jpeg", "png"])

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
    else:
        st.error("Text extraction failed.")