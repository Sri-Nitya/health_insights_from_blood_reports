import streamlit as st
from database_handler import load_reports_for_user, save_report, clear_current_session, delete_report
from utils.ocr import extract_text_from_image
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_client import GeminiClient
import base64


def dashboard_page():
    st.set_page_config(page_title="Dashboard 🧬", page_icon="🩺", layout="centered")

    if "username" not in st.session_state or not st.session_state.username:
        st.warning("Please login to access your dashboard.")
        st.stop()

    username = st.session_state.username

    st.title("📊 Blood Report Dashboard")
    st.write(f"Welcome **{username}**")

    view = st.sidebar.radio("Navigate", ["Overview", "Previous Reports"])

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        clear_current_session()
        st.session_state.page = "home"
        st.rerun()

    reports = load_reports_for_user(username) or []

    if view == "Overview":
        st.markdown("### 📈 Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Reports", len(reports))

        with col2:
            if reports:
                st.metric("Latest Upload", reports[-1]["file_name"])
            else:
                st.metric("Latest Upload", "None")

        st.markdown("---")

        st.markdown("### 📤 Upload New Blood Report")

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

                    gemini = GeminiClient(api_key=st.secrets["GEMINI_API_KEY"])
                    summary = gemini.get_summary(text)

                st.markdown("### 🧠 AI Health Insights")
                st.success(summary)

                # prevent double clicks and show cached result if available
                if "full_expl_inflight" not in st.session_state:
                    st.session_state.full_expl_inflight = False
                if "last_full_expl" not in st.session_state:
                    st.session_state.last_full_expl = None

                if not st.session_state.full_expl_inflight:
                    if st.button("Read full explanation", key="full_explanation"):
                        st.session_state.full_expl_inflight = True
                        with st.spinner("Generating full explanation..."):
                            full = gemini.get_full_explanation(text)
                        st.session_state.last_full_expl = full
                        st.session_state.full_expl_inflight = False
                        with st.expander("📚 Full Medical Explanation"):
                            st.write(st.session_state.last_full_expl)
                else:
                    st.info("Generating full explanation — please wait...")
                    if st.session_state.last_full_expl:
                        with st.expander("📚 Full Medical Explanation"):
                            st.write(st.session_state.last_full_expl)

                file_bytes = uploaded_file.getvalue()
                file_type = uploaded_file.type
                file_name = uploaded_file.name

                previous_report = reports[-1] if reports else None

                save_report(username, text, file_bytes, file_type, file_name)

                st.success("Report saved successfully!")

                if previous_report:

                    st.markdown("### 📊 Health Progress Comparison")

                    old_text = previous_report["text"]
                    comparison = gemini.get_comparison(old_text, text)

                    st.info(comparison)

            else:
                st.error("Text extraction failed. Please upload a clearer report.")

    elif view == "Previous Reports":
        st.markdown("### 📁 Previous Reports")

        if reports:

            most_recent = reports[-1]

            for i, report in enumerate(reports[::-1], 1):

                st.markdown(f"#### Report {i}")

                if st.button("Delete Report", key=f"delete_{i}"):   
                    delete_report(username, report.get("created_at"))
                    st.success("Report deleted successfully!")
                    st.rerun()

                file_bytes = report.get("file_bytes")
                file_type = report.get("file_type")
                file_name = report.get("file_name", f"report_{i}")

                if file_bytes and file_type:

                    if file_type == "application/pdf":

                        st.download_button(
                            "⬇ Download PDF",
                            file_bytes,
                            file_name=file_name,
                            mime=file_type,
                            key=f"pdf_{i}"
                        )

                        pdf_base64 = base64.b64encode(file_bytes).decode("utf-8")

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

                if len(reports) >= 2:
                    is_latest = (
                        report.get("text") == most_recent.get("text") and
                        report.get("file_name") == most_recent.get("file_name")
                    )
                    if not is_latest:
                        compare_key = f"compare_inflight_{i}"
                        if compare_key not in st.session_state:
                            st.session_state[compare_key] = False
                        if not st.session_state[compare_key]:
                            if st.button("🔁 Compare with Most Recent", key=f"compare_{i}"):
                                st.session_state[compare_key] = True
                                with st.spinner("Generating comparison..."):
                                    gemini = GeminiClient(api_key=st.secrets["GEMINI_API_KEY"])
                                    comparison = gemini.get_comparison(report.get("text", ""), most_recent.get("text", ""))
                                st.markdown("### 🔍 Comparison")
                                st.info(comparison)
                                st.session_state[compare_key] = False
                        else:
                            st.info("Generating comparison — please wait...")
                    else:
                        st.caption("This is the most recent report")

                st.markdown("---")

        else:
            st.info("No previous reports found. Upload your first report from Overview.")


if __name__ == "__main__":
    dashboard_page()
