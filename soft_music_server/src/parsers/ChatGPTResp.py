import typing
from src.core.parser import BasicParser


class Parser(BasicParser):
    @staticmethod
    def contents(data: dict) -> typing.Generator[str, None, None]:
        for i in data['choices']:
            yield i['message']['content']
