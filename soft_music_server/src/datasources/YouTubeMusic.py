import asyncio
from typing import List, Optional
from ytmusicapi import YTMusic



async def get_track_ids_ytmusic(
    queries: List[str],
    headers_path: Optional[str] = None,
    max_concurrency: int = 5,
    use_fallback: bool = True,
) -> List[Optional[str]]:
    """
    Возвращает список videoId в том же порядке, что и queries.
    Если ничего не найдено для запроса — None.
    """
    ytm = YTMusic(headers_path) if headers_path else YTMusic()
    sem = asyncio.Semaphore(max_concurrency)
    loop = asyncio.get_running_loop()

    def search_one(q: str) -> Optional[str]:
        # 1) Песни
        res = ytm.search(q, filter="songs", limit=1) or []
        if res and res[0].get("videoId"):
            return res[0]["videoId"]
        # 2) Fallback — общий поиск
        if use_fallback:
            generic = ytm.search(q, limit=3) or []
            for it in generic:
                vid = it.get("videoId")
                if vid:
                    return vid
        return None

    async def worker(q: str) -> Optional[str]:
        async with sem:
            return await loop.run_in_executor(None, lambda: search_one(q))

    return await asyncio.gather(*(worker(q) for q in queries))


# Пример запуска
if __name__ == "__main__":
    queries = [
        "The Weeknd - Blinding Lights",
        "Billie Eilish - bad guy",
        "Coldplay - Viva La Vida",
        "Imagine Dragons - Believer",
        "Грибы - Тает лед",
    ]
    ids = asyncio.run(get_track_ids_ytmusic(queries, max_concurrency=5))
    print(ids)