import json
import typing

from aiohttp.web_exceptions import HTTPNotFound
from fastapi import APIRouter

from src.datasources.Gemini import Gemini
from src.datasources.ITunes import ITunes
from src.models.music import Track

router = APIRouter()


async def tracks_ai(query: str) -> typing.List[Track]:
    """
    Searches for tracks by query using AI.

    Parameters
    ----------
    query:
        Search query given by user.

    Examples
    --------
    >>> import asyncio
    >>> from pprint import pprint
    >>> from src.api import tracks
    >>> my_tracks = asyncio.run(tracks.tracks_ai('Chill rock music for driving'))
    >>> pprint([i.as_dict for i in my_tracks])
    Out:
    [{'artist': 'Fleetwood Mac',
      'title': 'Dreams',
      ...},
     {'artist': 'The Eagles',
      'title': 'Hotel California',
      ...},
     {'artist': 'Dire Straits',
      'title': 'Sultans of Swing',
      ...}, ...]
    """
    prompt = (
        f"Choose bet music track for request '{query}'"
        "As many as possible, up to 20 tracks."
        "Return only JSON, without explanations."
        "Each element must contain fields: "
        "title, artist"
    )
    kwargs = {"generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "artist": {"type": "string"},
                },
                # "required": ["title", "artist", "durationSec", "coverUrl", "previewUrl"]
            }
        },
        # Для более предсказуемого вывода можно занизить температуру:
        # "temperature": 0.2,
        # "maxOutputTokens": 1024
    }}
    async with Gemini() as gpt:
        resp = await gpt.fetch(message=prompt, **kwargs)

    assert resp.status == 200
    return [Track(
        title=i['title'],
        artist=i['artist']
    ) for i in json.loads(*Gemini.Parser.contents(resp.content))]


async def collect(tracks: typing.Sequence[Track]) -> typing.List[Track]:
    """
    Collects tracks data by titles and artist from ITunes.

    Parameters
    ----------
    tracks:
        Sequence of tracks with titles and artists to collect from ITunes.

    Examples
    --------
    >>> import asyncio
    >>> from pprint import pprint
    >>> from src.api import tracks
    >>> my_tracks = asyncio.run(tracks.collect([tracks.Track(title='Smells like teen spirit', artist='Nirvana')]))
    >>> pprint([i.as_dict for i in my_tracks])
    Out:
    [{'artist': 'Nirvana',
      'coverUrl': 'https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/95/fd/b9/95fdb9b2 ... jpg/600x600bb.jpg',
      'durationSec': 301,
      'previewUrl': 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/...p.m4a',
      'title': 'Smells Like Teen Spirit',
      'url': 'https://music.apple.com/us/album/smells-like-teen-spirit/1440783617?i=1440783625&uo=4'}]
    """
    titles = [title for t in tracks if (title := ' - '.join(filter(None, [t.title, t.artist])))]
    async with ITunes() as itunes:
        resp = await itunes.fetch(
            titles,
            country="US",
            lang="en_us",
            prefer_preview=True,
            concurrency=8,
        )
        assert resp.status == 200
        found_ids = [i["result"]["id"] for i in ITunes.Parser.contents(resp.content) if i.get("result")]
        if found_ids:
            details = await itunes.by_ids(found_ids, country="US")
            assert details.status == 200
            return list(ITunes.Parser.parse(details.content))
        raise HTTPNotFound


@router.get("/tracks/search")
async def search(q: str = None):
    if not q:
        return {}

    print(f'AI Search started for "{q}" ...')
    tracks: typing.List[Track] = await tracks_ai(q)

    print(f'Collect tracks info "{tracks}"')
    tracks: typing.List[Track] = await collect(tracks)

    return {'tracks': [t.as_dict for t in tracks]}
