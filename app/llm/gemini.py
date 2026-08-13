from google import genai

from app.config import settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        self.model = settings.gemini_model

    def generate(self, messages: list[dict]) -> str:

        system_instruction = ""
        contents = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                system_instruction = content

            else:
                contents.append(
                    {
                        "role": role,
                        "parts": [{"text": content}],
                    }
                )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={
                "system_instruction": system_instruction,
            },
        )

        return response.text