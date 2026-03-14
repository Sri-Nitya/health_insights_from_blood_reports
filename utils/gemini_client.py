import google.generativeai as genai
import hashlib
import json
import os
import threading
from google.api_core.exceptions import ResourceExhausted


class GeminiClient:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.base_dir = os.path.dirname(__file__)
        self._lock = threading.Lock()

    def _load_cache(self, filename):
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self, filename, data):
        path = os.path.join(self.base_dir, filename)
        try:
            with open(path + ".tmp", "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(path + ".tmp", path)
        except Exception:
            pass

    def get_summary(self, text):
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_file = "summary_cache.json"

        cache = self._load_cache(cache_file)
        if key in cache:
            return cache[key]

        prompt = self._create_summary_prompt(text)
        try:
            response = self.model.generate_content(prompt)
            summary = response.text
        except ResourceExhausted:
            return cache.get(key, "AI quota exceeded — please try again later.")
        except Exception:
            return "AI service unavailable. Please try again later."

        if summary and (len(summary) > 900 or summary.count("\n") > 8):
            short_prompt = (
                "Please convert the following output into concise bullet points (<=12 bullets), "
                "keeping the sections: Key findings; What improved / worse; Suggested food & habits; Need doctor?; Must-dos / Must-don'ts.\n\n"
                + summary
            )
            try:
                resp2 = self.model.generate_content(short_prompt)
                summary = resp2.text
            except ResourceExhausted:
                pass
            except Exception:
                pass

        try:
            with self._lock:
                cache[key] = summary
                self._save_cache(cache_file, cache)
        except Exception:
            pass

        return summary

    def get_comparison(self, old_text, new_text):
        key = hashlib.sha256((old_text + "|||" + new_text).encode("utf-8")).hexdigest()
        cache_file = "comparison_cache.json"

        cache = self._load_cache(cache_file)
        if key in cache:
            return cache[key]

        prompt = self._create_comparison_prompt(old_text, new_text)
        try:
            response = self.model.generate_content(prompt)
            comparison = response.text
        except ResourceExhausted:
            return cache.get(key, "AI quota exceeded — please try again later.")
        except Exception:
            return "AI service unavailable. Please try again later."

        if comparison and (len(comparison) > 1200 or comparison.count("\n") > 12):
            short_prompt = (
                "Please shorten the following comparison into concise bullets with these sections: Improvements; Deteriorations; Suggested food & habit changes (3-5 bullets); Need doctor?; Urgent flags; Quick must-dos and must-don'ts.\n\n"
                + comparison
            )
            try:
                resp2 = self.model.generate_content(short_prompt)
                comparison = resp2.text
            except ResourceExhausted:
                pass
            except Exception:
                pass

        try:
            with self._lock:
                cache[key] = comparison
                self._save_cache(cache_file, cache)
        except Exception:
            pass

        return comparison

    def get_full_explanation(self, text):
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_file = "full_explanation_cache.json"

        cache = self._load_cache(cache_file)
        if key in cache:
            return cache[key]

        prompt = self._create_full_explanation_prompt(text)
        try:
            response = self.model.generate_content(prompt)
            full = response.text
        except ResourceExhausted:
            return cache.get(key, "AI quota exceeded — please try again later.")
        except Exception:
            return "AI service unavailable. Please try again later."

        try:
            with self._lock:
                cache[key] = full
                self._save_cache(cache_file, cache)
        except Exception:
            pass

        return full

    def _create_summary_prompt(self, extracted_text):
        return f"""
        You are a helpful medical assistant. Given the following extracted blood report text, produce a short, friendly summary in concise bullet points (no long paragraphs). Include these sections as bullets when relevant:
        - Key findings (one-line bullets)
        - what is worse
        - Suggested food & habit changes (short bullet list)
        - Need doctor visit? (Yes/No + one-line reason)
        - Quick must-dos and must-don'ts

        Keep output under ~12 bullets and use plain language. Do NOT include medical jargon without a short explanation.

        Report:
        {extracted_text}
        """

    def _create_comparison_prompt(self, old_report, new_report):
        return f"""
        You are a concise medical assistant. Compare the OLD report and the NEW report below and return a short, ordered bullet list with these sections when applicable:
        - Improvements: (what improved since the old report)
        - Deteriorations: (what worsened)
        - Suggested food & habit changes: (3-5 short bullets)
        - Need doctor visit?: (Yes/No + one-line reason)
        - Urgent flags: (any critical values needing immediate attention)
        - Quick must-dos and must-don'ts

        Keep each item short (one sentence). Use emojis sparingly and avoid long paragraphs.

        ---
        OLD REPORT:
        {old_report}
        
        NEW REPORT:
        {new_report}
        """

    def _create_full_explanation_prompt(self, extracted_text):
        return f"""
        You are a careful medical assistant. Given the extracted blood report below, produce a detailed, structured explanation for a layperson in very simple words. Include:
        - A short summary (2-3 sentences)
        - Interpretations for key values (what each important value means and normal ranges)
        - Possible causes for abnormal values (brief list)
        - Recommended next steps and tests to consider
        - Diet and lifestyle suggestions with rationale
        - When to seek medical attention (red flags)
        - References or resources (if applicable)

        Use clear language, numbered or bulleted sections, and keep medical caveats prominent: this is informational and not a substitute for clinical advice.

        Report:
        {extracted_text}
        """
