# Blood Report Analyzer 🧬

A Streamlit-based web application that helps users upload, analyze, and track their blood reports using AI-powered insights.

## Features

- **User Authentication:** Login, signup, and guest upload options.
- **Report Upload:** Supports PDF and image (JPG, PNG) blood reports.
- **OCR & PDF Extraction:** Extracts text from uploaded reports using OCR and PDF parsing.
- **AI Health Summary:** Summarizes extracted data using Gemini AI.
- **Progress Tracking:** Compares current and previous reports for health trends.
- **Download & View:** View reports in-browser and download originals.
- **Secure Storage:** User-specific report history.

## Getting Started

### Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- Required Python packages (see below)

### Installation

1. **Clone the repository:**

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the app:**
    ```bash
    streamlit run Home.py
    ```


## Usage

- **Login or Signup:** Use the sidebar to log in or sign up.
- **Upload Report:** Upload your blood report (PDF or image).
- **View & Analyze:** See extracted text, AI summary, and compare with previous reports.
- **Download:** Download your original report.

## Technologies Used

- [Streamlit](https://streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)
- OCR libraries (e.g., pytesseract)
- PDF parsing libraries (e.g., PyPDF2)

