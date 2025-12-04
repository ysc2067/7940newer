import configparser
import google.generativeai as genai
from google import genai


class HKBU_ChatGPT:

    def __init__(self, config_="./config.ini"):
        if isinstance(config_, str):
            self.config = configparser.ConfigParser()
            self.config.read(config_)
        elif isinstance(config_, configparser.ConfigParser):
            self.config = config_
        else:
            raise ValueError("config_ must be a path or ConfigParser object")

        api_key = self.config["GEMINI"]["API_KEY"]
        model_name = self.config["GEMINI"].get("MODEL_NAME", "gemini-1.5-flash")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def submit(self, message: str) -> str:
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Gemini API error: {e}"


if __name__ == "__main__":
    bot = HKBU_ChatGPT()
    while True:
        text = input("You: ")
        print("Bot:", bot.submit(text))
