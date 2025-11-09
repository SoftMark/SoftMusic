import aiohttp
import asyncio
import json
import typing
import traceback

from asyncio_throttle import Throttler
from logging import getLogger


log = getLogger()


class Response(typing.NamedTuple):
    status: int = None
    content: typing.Any = None
    error: typing.Any = None


class Datasource:

    class Error(BaseException):
        ...

    timeout = aiohttp.ClientTimeout(total=None, sock_read=120)
    limit, period = 2, 1  # 2 requests per 1 second

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        self.throttle = Throttler(rate_limit=self.limit, period=self.period)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        for i in ('session', 'throttle'):
            delattr(self, i)

    async def request(
            self,
            url: str = None,
            method: str = 'get',
            attempts: int = 3,
            delay: int = 1,
            assertion=lambda status, content: True,
            decode: str = 'json',
            **kwargs
    ) -> Response:
        """
        Send GET request to API

        Parameters
        ----------
        url: str
            request URL address;
        method: str
            HTTP request method name;
        attempts: int
            how many attempts to do before error returned;
        delay: int
            sleep between each try;
        assertion: func
            callable object returns True/False to catch errors by http satus code and/or response content;
        decode: str
            one of:
            - read - returns bytes object with body content;
            - text - returns str with body content, decoded with charset encoding or UTF-8;
            - json - returns response body decoded as json;
        kwargs:
            requests kwargs:
            - params: dict, other parameters API required;
            - data: dict, posted data;
            - proxy: dict, proxy setting.

        Returns
        -------
        out: Coroutine
            API response
        """
        while (attempts := attempts - 1) >= 0:
            try:
                async with self.throttle, self.session.request(method, url, **kwargs) as resp:
                    status = resp.status
                    if decode == 'json':
                        try:
                            content = await resp.json(content_type=None)  # ключевая строка
                        except aiohttp.ContentTypeError:
                            # Фоллбек: читаем текст и пробуем распарсить вручную
                            text = await resp.text()
                            try:
                                content = json.loads(text)
                            except json.JSONDecodeError:
                                content = text  # оставляем как текст, если это не JSON
                    elif decode == 'text':
                        content = await resp.text()
                    elif decode in ('bytes', 'read'):
                        content = await resp.read()
                    else:
                        # на случай, если вы хотите вызвать другой метод aiohttp ответа
                        content = await getattr(resp, decode)()
                    # response custom validation
                    if not assertion(status, content):
                        raise self.Error('false assertion:', status, content)

                    # cache if response is valid
                    return Response(status=status, content=content)

            except Exception as error:
                log.error(traceback.format_exc())

                if attempts > 0:
                    await asyncio.sleep(delay)
                    continue

                return Response(error=error)
