import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")

    def get_summary(self, text):
        prompt = self._create_summary_prompt(text)
        response = self.model.generate_content(prompt)
        return response.text

    def get_comparison(self, old_text, new_text):
        prompt = self._create_comparison_prompt(old_text, new_text)
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_summary_prompt(self, extracted_text):
        return f"""
        👋 **Hello! I'm your friendly AI Health Assistant. Let's dive into your blood report together!**

        ✨ **Here's what I found in your report:**
        {extracted_text}

        ---

        🔎 **Personalized Insights:**
        - I’ll break down your results in simple, easy-to-understand language.
        - **Important values** will be highlighted in bold.
        - 🚦 I’ll use emojis to show what’s great 😊, what needs attention ⚠️, and what’s urgent 🚨.
        - If something stands out, I’ll explain what it means for your health.

        💡 **What You Can Do:**
        - For each key result, I’ll give you friendly tips and next steps.
        - If everything looks good, I’ll celebrate with you! 🎉
        - If there’s something to watch, I’ll gently let you know and suggest what to ask your doctor.

        ---

        🙋 **Remember:**  
        This summary is for your information only. For any concerns or questions, always consult a healthcare professional. Your health matters! ❤️

        ---

        **Ready? Here’s your interactive summary:**  
        """
    def _create_comparison_prompt(self, old_report, new_report):
        return f"""
        You are a medical assistant. Compare these two blood test reports and provide a detailed health progression summary:
        ---
        **Old Report:**
        {old_report}
        **New Report:**
        {new_report}
        ---
        Highlight improvements 📈 or deterioration 📉, and give clear, understandable suggestions.
        """
    