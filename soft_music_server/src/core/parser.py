import ast
import re
import typing


class BasicParser:
    def parse(self, data: typing.Any) -> typing.Any:
        return data

    @staticmethod
    def find_lists(text: str) -> typing.Optional[list]:
        for i in re.findall(r"=\s*(\[[\s\S]*?\])", text):
            yield ast.literal_eval(i)
