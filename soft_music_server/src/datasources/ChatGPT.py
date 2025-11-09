import enum
import os

from src.parsers import ChatGPTResp
from src.core.datasource import Datasource


class ChatGPT(Datasource):
    Parser = ChatGPTResp.Parser
    url = 'https://api.openai.com/{tail}'
    # TODO: load from config
    token = os.getenv('GPTToken')

    class Model(enum.Enum):
        gpt_4o_mini = 'gpt-4o-mini'

    async def fetch(self, message: str):
        """
        Examples
        --------
        >>> import asyncio
        >>> from pprint import pprint
        >>> from src.datasources.ChatGPT import ChatGPT

        >>> msg = 'Best Rock songs YouTubeMusic urls. Output must be in Python list format.'
        >>> async def fetch():
        ...     async with ChatGPT() as gpt:
        ...         return await gpt.fetch(msg)

        >>> resp = asyncio.run(fetch())

        >>> assert resp.status == 200
        >>> for i in ChatGPT.Parser.contents(resp.content):
        ...     for j in ChatGPT.Parser.find_lists(i):
        ...         pprint(j)
        """
        return await self.request(
            self.url.format(tail='v1/chat/completions'),
            method='post',
            headers={
                'Authorization': f'Bearer {self.token}'
            },
            json={
                "model": self.Model.gpt_4o_mini.value,
                "store": True,
                "messages": [{"role": "user", "content": message}]},
            assertion=lambda status, _: status == 200, )
