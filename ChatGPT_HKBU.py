from google import genai


class HKBU_ChatGPT:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def chat(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            if hasattr(response, "text") and response.text:
                return response.text
            return "（none）"
        except Exception as e:
            return f"error: {e}"
