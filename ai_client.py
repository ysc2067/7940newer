import logging
import os

import requests


class AIClient:
    def __init__(self):
        self.api_key = (os.environ.get("AI_API_KEY") or "").strip()
        self.base_url = (os.environ.get("AI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = os.environ.get("AI_MODEL") or "gpt-4o"

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
            return data["choices"][0]["message"]["content"] or "AI 服务暂时没有返回内容。"
        except requests.exceptions.Timeout:
            return "抱歉，AI 服务响应超时，请稍后重试。"
        except requests.exceptions.ConnectionError:
            return "抱歉，无法连接到 AI 服务，请稍后重试。"
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            logging.warning("AI service returned HTTP %s", status_code)
            return f"抱歉，AI 服务返回了错误（HTTP {status_code}），请稍后重试。"
        except (KeyError, IndexError, TypeError, ValueError):
            logging.exception("AI service returned an unexpected response format")
            return "抱歉，AI 服务返回了意外的响应格式。"
        except requests.exceptions.RequestException:
            logging.exception("AI service request failed")
            return "抱歉，请求 AI 服务时发生错误，请稍后重试。"
        except Exception:
            logging.exception("Unexpected error while calling AI service")
            return "抱歉，调用 AI 服务时发生了未知错误。"


if __name__ == '__main__':
    chatgpt = AIClient()
    while True:
        user_input = input('Type something to ChatGPT:\t')
        messages = [{"role": "user", "content": user_input}]
        response = chatgpt.submit(messages)
        print(response)
