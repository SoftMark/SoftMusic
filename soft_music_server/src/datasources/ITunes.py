import enum
import asyncio
import typing
from typing import Any, Dict, List, Optional, Iterable

from src.core.datasource import Datasource
from src.models.music import Track


class ITunes(Datasource):
    """
    Асинхронный Datasource для iTunes Search API.

    Документация:
      - https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/

    Возможности:
      - Поиск по списку тайтлов с возвратом лучшего совпадения (по умолчанию с наличием preview_url)
      - Получение данных по списку track_id через lookup
      - Нормализованные поля (id, title, artist, album, duration, preview_url, artwork и т.д.)

    Важно:
      - iTunes отдаёт preview (30–90 секунд), не полный трек.

    Пример
    ------
    >>> import asyncio
    >>> from pprint import pprint
    >>> from src.datasources.ITunes import ITunes
    >>>
    >>> titles = [
    ...     "Smells Like Teen Spirit",
    ...     "Hotel California",
    ...     "Billie Jean",
    ... ]
    >>>
    >>> async def run():
    ...     results = []
    ...     async with ITunes() as api:
    ...         resp = await api.fetch(
    ...             titles,
    ...             country="US",
    ...             lang="en_us",
    ...             prefer_preview=True,
    ...             concurrency=8,
    ...         )
    ...         assert resp.status == 200
    ...         # Разбор результатов
    ...         for item in ITunes.Parser.contents(resp.content):
    ...             if item.get("error"):
    ...                 print("ERR:", item["query"], "->", item["error"])
    ...                 continue
    ...             res = item.get("result")
    ...             if not res:
    ...                 print(item["query"], "-> not found")
    ...                 continue
    ...             print(f"{item['query']} -> [{res['id']}] {res['artist']} — {res['title']} ({res['duration']}s)")
    ...             print("  preview:", res.get("preview_url"))
    ...             print("  track:", res.get("track_url"))
    ...             print("  artwork:", res.get("artwork_url"))
    ...
    ...         # Получаем детали по track_id
    ...         found_ids = [i["result"]["id"] for i in ITunes.Parser.contents(resp.content) if i.get("result")]
    ...         if found_ids:
    ...             details = await api.by_ids(found_ids, country="US")
    ...             assert details.status == 200
    ...             print("\\nBy IDs:")
    ...             for item in ITunes.Parser.contents(details.content):
    ...                 res = item.get("result")
    ...                 if res:
    ...                     print(f" id={item['id']} -> {res['artist']} — {res['title']} preview={res.get('preview_url')}")
    ...                     results.append(res)
    >>>
    >>> asyncio.run(run())
    """

    class Parser:
        @staticmethod
        def parse(content: typing.Dict[str, Any]) -> typing.Generator[Track, None, None]:
            # return {'tracks': [{
            #     'title': i['title'],
            #     'artist': i['artist'],
            #     'coverUrl': i['artwork_url'],
            #     'previewUrl': i['preview_url'],
            #     'durationSec': i['duration'],
            #     'url': 'track_url'} for i in tracks]}
            for r in content.get("results", []):
                t = r['result']
                yield Track(
                    source='ITunes',
                    url=t['track_url'],

                    title=t['title'],
                    artist=t['artist'],

                    duration=t['duration'],
                    img_url=t['artwork_url'],
                    preview_url=t['preview_url'],
                )


        @staticmethod
        def contents(content: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
            return content.get("results", [])

        @staticmethod
        def find_preview_url(item: Dict[str, Any]) -> Optional[str]:
            res = item.get("result") or {}
            return res.get("preview_url")

        @staticmethod
        def find_artwork(item: Dict[str, Any]) -> Optional[str]:
            res = item.get("result") or {}
            return res.get("artwork_url")

    url = "https://itunes.apple.com/{tail}"

    # Единый ответ в стиле вашего ChatGPT класса
    class _Resp:
        def __init__(self, status: int, content: Any):
            self.status = status
            self.content = content

    @staticmethod
    def _normalize_track(track: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализует iTunes search/lookup элемент в компактный трек-объект.
        """
        track_id = track.get("trackId") or track.get("collectionId")
        title = track.get("trackName") or track.get("collectionName")
        duration_ms = track.get("trackTimeMillis") or 0
        artwork = track.get("artworkUrl100") or track.get("artworkUrl60") or track.get("artworkUrl30")
        # Частый трюк: повысить разрешение арта, если доступно
        if isinstance(artwork, str):
            artwork = artwork.replace("100x100bb", "600x600bb").replace("100x100", "600x600")

        return {
            "id": str(track_id) if track_id is not None else None,
            "title": title,
            "artist": track.get("artistName"),
            "album": track.get("collectionName"),
            "duration": int(round((duration_ms or 0) / 1000)),
            "release_date": track.get("releaseDate"),
            "preview_url": track.get("previewUrl"),  # прямая ссылка на превью (mp3/m4a)
            "track_url": track.get("trackViewUrl"),
            "artist_url": track.get("artistViewUrl"),
            "collection_url": track.get("collectionViewUrl"),
            "artwork_url": artwork,
            "genre": track.get("primaryGenreName"),
            "country": track.get("country"),
            "currency": track.get("currency"),
            "explicitness": track.get("trackExplicitness"),
        }

    async def _search_request(self, params: Dict[str, Any]) -> "_Resp":
        """
        GET /search
        """
        resp = await self.request(
            self.url.format(tail="search"),
            method="get",
            params=params,
            assertion=lambda status, _: status == 200,
        )
        return resp

    async def _lookup_request(self, params: Dict[str, Any]) -> "_Resp":
        """
        GET /lookup
        """
        resp = await self.request(
            self.url.format(tail="lookup"),
            method="get",
            params=params,
            assertion=lambda status, _: status == 200,
        )
        return resp

    async def _search_best_one(
        self,
        title: str,
        *,
        country: str,
        lang: Optional[str],
        prefer_preview: bool,
    ) -> Dict[str, Any]:
        """
        Ищет лучший трек для одного запроса.
        Если prefer_preview=True — берём первый результат с previewUrl (делаем limit до 5).
        """
        base = {
            "term": title,
            "media": "music",
            "entity": "musicTrack",
            "country": country,
        }
        if lang:
            base["lang"] = lang

        # Если нужно гарантировать превью — берём до 5 результатов и фильтруем.
        params = dict(base)
        params["limit"] = 5 if prefer_preview else 1

        try:
            resp = await self._search_request(params)
            data = resp.content or {}
            results = data.get("results") or []

            picked = None
            if prefer_preview:
                for r in results:
                    if r.get("previewUrl"):
                        picked = r
                        break
                # если ни у кого нет превью, можем взять 1-й (или вернуть None)
                if not picked and results:
                    picked = results[0]
            else:
                picked = results[0] if results else None

            if not picked:
                return {"query": title, "result": None, "error": None}

            return {"query": title, "result": self._normalize_track(picked), "error": None}
        except Exception as e:
            return {"query": title, "result": None, "error": str(e)}

    async def fetch(
        self,
        titles: List[str],
        *,
        country: str = "US",
        lang: Optional[str] = "en_us",
        prefer_preview: bool = True,
        concurrency: int = 8,
    ):
        """
        Ищет лучший матч для каждого тайтла.
        Возвращает: _Resp(status=200, content={"results": [ {query, result|None, error|None}, ... ]})

        Examples
        --------
        >>> import asyncio
        >>> from pprint import pprint
        >>> from src.datasources.ITunes import ITunes
        >>>
        >>> async def fetch_all():
        ...     async with ITunes() as api:
        ...         return await api.fetch(["Smells Like Teen Spirit", "Hotel California"])
        >>>
        >>> resp = asyncio.run(fetch_all())
        >>> assert resp.status == 200
        >>> for item in ITunes.Parser.contents(resp.content):
        ...     pprint(item)
        """
        if not isinstance(titles, (list, tuple)) or not titles:
            return self._Resp(400, {"error": "titles must be a non-empty list"})

        sem = asyncio.Semaphore(concurrency)

        async def _one(t: str):
            async with sem:
                return await self._search_best_one(
                    t, country=country, lang=lang, prefer_preview=prefer_preview
                )

        items = await asyncio.gather(*[_one(t) for t in titles])
        return self._Resp(200, {"results": items})

    async def by_ids(
        self,
        track_ids: List[str],
        *,
        country: str = "US",
        lang: Optional[str] = "en_us",
        chunk_size: int = 50,
    ):
        """
        Получение деталей по списку track_id через /lookup (батчами).
        Возвращает: _Resp(status=200, content={"results": [ {"id": <id>, "result"|None, "error"|None}, ... ]})
        """
        if not isinstance(track_ids, (list, tuple)) or not track_ids:
            return self._Resp(400, {"error": "track_ids must be a non-empty list"})

        def chunks(xs: List[str], n: int):
            for i in range(0, len(xs), n):
                yield xs[i : i + n]

        out_map: Dict[str, Dict[str, Any]] = {}

        try:
            # Apple позволяет lookup по нескольким id (до ~200), делаем батчами
            for group in chunks(list(track_ids), chunk_size):
                params = {
                    "id": ",".join(str(x) for x in group),
                    "country": country,
                }
                if lang:
                    params["lang"] = lang
                resp = await self._lookup_request(params)
                data = resp.content or {}
                results = data.get("results") or []
                for r in results:
                    rid = str(r.get("trackId") or r.get("collectionId"))
                    out_map[rid] = {
                        "id": rid,
                        "result": self._normalize_track(r),
                        "error": None,
                    }

            # Собираем в исходном порядке, заполняя None для отсутствующих
            items = [out_map.get(str(tid), {"id": str(tid), "result": None, "error": None}) for tid in track_ids]
            return self._Resp(200, {"results": items})
        except Exception as e:
            # Если упали целиком, вернём пометку ошибки
            items = [{"id": str(tid), "result": None, "error": str(e)} for tid in track_ids]
            return self._Resp(200, {"results": items})