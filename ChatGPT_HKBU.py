from google import genai

class HKBU_ChatGPT:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.client = genai.Client()

    def chat(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text if response and hasattr(response, "text") else "No response."
        except Exception as e:
            return f"Error: {str(e)}"
