import enum
import asyncio
from typing import Any, Dict, List, Optional

from src.core.datasource import Datasource


class Jamendo(Datasource):
    """
    Асинхронный Datasource для Jamendo API (v3.0).

    Требуется client_id (ниже в token). Документация:
    https://developer.jamendo.com/v3.0

    Пример
    ------
    >>> import asyncio
    >>> from pprint import pprint
    >>> from src.datasources.Jamendo import Jamendo
    >>>
    >>> titles = [
    ...     "Acoustic Breeze",
    ...     "Electro Swing",
    ...     "Ambient Dreams",
    ... ]
    >>>
    >>> async def run():
    ...     async with Jamendo() as api:
    ...         # Поиск лучших совпадений по списку тайтлов
    ...         resp = await api.fetch(titles, prefer_downloadable=False, concurrency=8)
    ...         assert resp.status == 200
    ...         # Пример использования встроенного парсера
    ...         for item in Jamendo.Parser.contents(resp.content):
    ...             res = item.get("result")
    ...             if res:
    ...                 print(f"{item['query']} -> {res['artist']} — {res['title']}")
    ...                 print("  stream:", res.get("stream_url"))
    ...                 if res.get("download_url"):
    ...                     print("  download:", res["download_url"])
    ...         # Получение деталей по списку найденных ID
    ...         found_ids = [i["result"]["id"] for i in resp.content["results"] if i.get("result")]
    ...         if found_ids:
    ...             details = await api.by_ids(found_ids, concurrency=8)
    ...             assert details.status == 200
    ...             print("\\nDetails by IDs:")
    ...             for d in Jamendo.Parser.contents(details.content):
    ...                 res = d.get("result")
    ...                 if res:
    ...                     print(f" id={d['id']} -> {res['artist']} — {res['title']}")
    >>>
    >>> asyncio.run(run())
    """

    # Поддержка "по примеру" вашего ChatGPT класса
    class Parser:
        @staticmethod
        def contents(content: Dict[str, Any]):
            # Единый интерфейс итерации результатов
            return content.get("results", [])

        @staticmethod
        def find_stream_url(item: Dict[str, Any]) -> Optional[str]:
            res = item.get("result") or {}
            return res.get("stream_url")

        @staticmethod
        def find_download_url(item: Dict[str, Any]) -> Optional[str]:
            res = item.get("result") or {}
            return res.get("download_url")

    url = 'https://api.jamendo.com/v3.0/{tail}'
    # TODO: load from config / env
    token = 'JamendoClientID'  # это client_id Jamendo

    include = "musicinfo+stats+licenses"

    # Вспомогательный mini-Response, чтобы совпадать с вашим стилем (resp.status, resp.content)
    class _Resp:
        def __init__(self, status: int, content: Any):
            self.status = status
            self.content = content

    @staticmethod
    def _normalize_track(track: Dict[str, Any]) -> Dict[str, Any]:
        musicinfo = track.get("musicinfo") or {}
        stats = track.get("stats") or {}

        stream_url = track.get("audio")  # прямая ссылка на поток
        download_url = track.get("audiodownload") or None  # если доступно по лицензии

        permalink = track.get("shareurl") or track.get("shorturl")
        license_url = track.get("license_ccurl") or None
        image = track.get("album_image") or track.get("image")

        return {
            "id": str(track.get("id")),
            "title": track.get("name"),
            "artist": track.get("artist_name"),
            "album": track.get("album_name"),
            "duration": int(track.get("duration") or 0),
            # "releasedate": track.get("releasedate"),
            "stream_url": stream_url,
            "download_url": download_url,
            "permalink": permalink,
            "license_url": license_url,
            # "tags": (musicinfo.get("tags") or {}).get("genres") or [],
            # "bpm": (musicinfo.get("rhythm") or {}).get("bpm"),
            # "vocal_instrumental": (musicinfo.get("vocalinstrumental") or {}).get("value"),
            # "language": (musicinfo.get("lang") or {}).get("value"),
            "image": image,
            # "stats_listened": stats.get("listened_total"),
            # "stats_favorited": stats.get("favorited_total"),
        }

    async def _tracks_request(self, params: Dict[str, Any]) -> "_Resp":
        """
        Обёртка над self.request в стиле вашего ChatGPT класса.
        """
        # Jamendo ждёт client_id как query-параметр
        q = {
            "client_id": self.token,
            "format": "json",
            "include": self.include,
            **params,
        }
        resp = await self.request(
            self.url.format(tail='tracks'),
            method='get',
            params=q,
            assertion=lambda status, _: status == 200,
        )
        return resp

    async def _search_best_one(
        self,
        title: str,
        *,
        lang: Optional[str],
        prefer_downloadable: bool,
    ) -> Dict[str, Any]:
        """
        Поиск одного лучшего трека по названию с fallback.
        Возвращает {"query": <title>, "result": <normalized>|None, "error": <str>|None}
        """
        # 1) Сначала точное по имени
        params_name = {"limit": 1, "namesearch": title, "order": "relevance"}
        if lang:
            params_name["lang"] = lang

        resp = await self._tracks_request(params_name)
        data = resp.content or {}
        results = data.get("results") or []
        # from ipdb import set_trace; set_trace()

        # 2) Если не нашли — fallback на общий search
        if not results:
            params_search = {"limit": 1, "search": title, "order": "relevance"}
            if lang:
                params_search["lang"] = lang
            resp2 = await self._tracks_request(params_search)
            data2 = resp2.content or {}
            results = data2.get("results") or []

        if not results:
            return {"query": title, "result": None, "error": None}

        track = results[0]
        if prefer_downloadable and not track.get("audiodownload"):
            return {"query": title, "result": None, "error": None}

        return {"query": title, "result": self._normalize_track(track), "error": None}

    async def fetch(
        self,
        titles: List[str],
        *,
        lang: Optional[str] = None,
        prefer_downloadable: bool = False,
        concurrency: int = 8,
    ):
        """
        Ищет лучший матч для каждого тайтла и возвращает единый ответ:
        _Resp(status=200, content={"results": [ ... ]})

        Examples
        --------
        >>> import asyncio
        >>> from pprint import pprint
        >>> from src.datasources.Jamendo import Jamendo
        >>>
        >>> titles = ["Acoustic Breeze", "Electro Swing"]
        >>>
        >>> async def fetch_all():
        ...     async with Jamendo() as api:
        ...         return await api.fetch(titles, prefer_downloadable=False, concurrency=8)
        >>>
        >>> resp = asyncio.run(fetch_all())
        >>> assert resp.status == 200
        >>> for item in Jamendo.Parser.contents(resp.content):
        ...     pprint(item)
        """
        if not isinstance(titles, (list, tuple)) or not titles:
            return self._Resp(400, {"error": "titles must be a non-empty list"})

        sem = asyncio.Semaphore(concurrency)

        async def _one(t: str):
            async with sem:
                try:
                    return await self._search_best_one(
                        t, lang=lang, prefer_downloadable=prefer_downloadable
                    )
                except Exception as e:
                    return {"query": t, "result": None, "error": str(e)}

        items = await asyncio.gather(*[_one(t) for t in titles])
        return self._Resp(200, {"results": items})

    async def by_ids(
        self,
        track_ids: List[str],
        *,
        concurrency: int = 8,
    ):
        """
        Возвращает детали по списку track_id.
        Ответ: _Resp(status=200, content={"results": [{"id": <id>, "result": <normalized>|None, "error": <str>|None}, ...]})
        """
        if not isinstance(track_ids, (list, tuple)) or not track_ids:
            return self._Resp(400, {"error": "track_ids must be a non-empty list"})

        sem = asyncio.Semaphore(concurrency)

        async def _one(tid: str):
            async with sem:
                try:
                    resp = await self._tracks_request({"id": tid, "limit": 1})
                    data = resp.content or {}
                    results = data.get("results") or []
                    if not results:
                        return {"id": tid, "result": None, "error": None}
                    return {"id": tid, "result": self._normalize_track(results[0]), "error": None}
                except Exception as e:
                    return {"id": tid, "result": None, "error": str(e)}

        items = await asyncio.gather(*[_one(t) for t in track_ids])
        return self._Resp(200, {"results": items})
