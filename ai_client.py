import os
import requests


class AIClient:
    def __init__(self):
        self.api_key = os.environ.get("AI_API_KEY")
        self.base_url = os.environ.get("AI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("AI_MODEL", "gpt-4o")

        if not self.api_key:
            raise ValueError(
                "AI_API_KEY is not set. "
                "Please create a .env file based on .env.example."
            )

    def submit(self, messages: list[dict]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"model": self.model, "messages": messages}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            return "抱歉，AI 服务响应超时，请稍后重试。"
        except requests.exceptions.ConnectionError:
            return "抱歉，无法连接到 AI 服务，请稍后重试。"
        except (KeyError, IndexError):
            return "抱歉，AI 服务返回了意外的响应格式。"
        except requests.exceptions.HTTPError:
            return f"抱歉，AI 服务返回了错误（HTTP {response.status_code}）。"
        except Exception:
            return "抱歉，调用 AI 服务时发生了未知错误。"


if __name__ == '__main__':
    chatgpt = AIClient()
    while True:
        user_input = input('Type something to ChatGPT:\t')
        messages = [{"role": "user", "content": user_input}]
        response = chatgpt.submit(messages)
        print(response)
