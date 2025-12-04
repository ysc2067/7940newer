import configparser
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

        api_key = self.config["GEMINI"]["API_KEY"].strip()
        model_name = self.config["GEMINI"].get("MODEL_NAME", "").strip()

        if not model_name:
            model_name = "gemini-2.5-flash-lite"
        if model_name.startswith("gemini-1."):
            model_name = "gemini-2.5-flash-lite"

        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def submit(self, message: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=message
            )
            return getattr(response, "text", str(response))
        except Exception as e:
            return f"Gemini API error: {e}"


if __name__ == "__main__":
    bot = HKBU_ChatGPT()
    while True:
        text = input("You: ")
        print("Bot:", bot.submit(text))
