import json
import enum
import os

# Предполагается, что вы будете использовать те же классы для парсинга и основного Datasource
# from src.parsers import GeminiResp # <-- Вам может потребоваться новый парсер
from src.core.datasource import Datasource, Response
from src.models.music import Track
from src.parsers import GeminiResp


class Gemini(Datasource):
    # Parser = GeminiResp.Parser  # <-- Обновите парсер, если нужно
    # Для целей этого примера оставим заглушку:
    Parser = GeminiResp.Parser

    json_mode_params = {"generationConfig": {
      "response_mime_type": "application/json",
      "response_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
          "title": {"type": "string"},
          "items": {"type": "array", "items": {"type": "string"} }
        },
        "required": ["title", "items"]
      }
    }}

    # 1. URL API: Используется для генерации контента
    url = 'https://generativelanguage.googleapis.com/{tail}'
    # TODO: load from config
    # 2. TOKEN: API Key для Gemini
    token = os.getenv('GeminiToken')

    class Model(enum.Enum):
        # 3. НАЗВАНИЕ МОДЕЛИ: gemini-2.5-flash является хорошим аналогом gpt-4o-mini
        gemini_2_5_flash = 'gemini-2.5-flash'

    async def fetch(self, message: str, **kwargs) -> Response:
        """
        Пример использования
        --------
        >>> import asyncio
        >>> from pprint import pprint
        >>> from src.datasources.Gemini import Gemini
        >>> # Импортируйте ваш класс Gemini

        >>> msg = 'Best Rock songs YouTube urls. Output must be in Python list format.'
        >>> async def fetch():
        ...     async with Gemini() as g:
        ...         return await g.fetch(msg)

        >>> resp = asyncio.run(fetch())

        >>> assert resp.status == 200
        >>> for i in Gemini.Parser.contents(resp.content):
        ...     for j in Gemini.Parser.find_lists(i):
        ...         pprint(j)
        """

        # 4. ФОРМАТ КОНЕЧНОЙ ТОЧКИ (ENDPOINT): Используется 'v1/models/{model}:generateContent'
        model_name = self.Model.gemini_2_5_flash.value
        endpoint = f'v1beta/models/{model_name}:generateContent'

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": message}
                    ]
                }
            ],
            **kwargs,
        }
        return await self.request(
            self.url.format(tail=endpoint),
            headers={'x-goog-api-key': self.token, 'Content-Type': 'application/json'},
            method='post',
            json=payload,
            # assertion=lambda status, _: status == 200,
        )
