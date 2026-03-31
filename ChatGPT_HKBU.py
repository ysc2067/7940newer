import os
import requests
from dotenv import load_dotenv


class HKBU_ChatGPT():
    def __init__(self):
        load_dotenv()

        self.api_key = os.environ.get("AI_API_KEY")
        self.base_url = os.environ.get("AI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("AI_MODEL", "gpt-4o")

        if not self.api_key:
            raise ValueError(
                "AI_API_KEY is not set. "
                "Please create a .env file based on .env.example."
            )

    def submit(self, messages):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"model": self.model, "messages": messages}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"


if __name__ == '__main__':
    chatgpt = HKBU_ChatGPT()
    while True:
        user_input = input('Type something to ChatGPT:\t')
        messages = [{"role": "user", "content": user_input}]
        response = chatgpt.submit(messages)
        print(response)
