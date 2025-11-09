import re
import ast
import json
import typing
from src.core.parser import BasicParser


class Parser(BasicParser):
    @staticmethod
    def contents(data: dict) -> typing.Generator[str, None, None]:
        for c in data['candidates'] or {}:
            for p in (c.get('content') or {}).get('parts') or {}:
                if text := p.get('text'):
                    yield text

    @staticmethod
    def find_lists(text: str) -> typing.Optional[list]:
        return json.loads(re.search(r'json\s*([\s\S]*?)\s*', text).group(1).strip())
