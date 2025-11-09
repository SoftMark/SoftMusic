import json
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.datasources.ChatGPT import ChatGPT
from src.datasources.Gemini import Gemini
from src.datasources.ITunes import ITunes

router = APIRouter()

# @router.get("/search")
# async def ask_gpt(q: str = None):
#   if not q:
#     return {}
#   print(q)
#   msg = f'Youtube. "{q}". Answer must be raw JSON. list of dict fields: title, artist, coverUrl, durationSec, url'
#
#   async with Gemini() as gpt:
#     resp = await gpt.fetch(msg)
#
#   print(resp.status)
#   assert resp.status == 200
#   tracks = []
#   for i in Gemini.Parser.contents(resp.content):
#     for j in Gemini.Parser.find_lists(i):
#       tracks.extend(j)
#   return {'tracks': tracks}


@router.get("/search")
async def ask_gpt(q: str = None):
  if not q:
    return {}
  print(q)

  async with Gemini() as gpt:
    resp = await gpt.search_music(q)
  titles = [i['title'] for i in json.loads(*Gemini.Parser.contents(resp.content))]

  print(f'Titles: {titles}')
  tracks = []
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
      for item in ITunes.Parser.contents(details.content):
        if res := item.get("result"):
          tracks.append(res)

  print(tracks)
  return {'tracks': [{
    'title': i['title'],
    'artist': i['artist'],
    'coverUrl': i['artwork_url'],
    'previewUrl': i['preview_url'],
    'durationSec': i['duration'],
    'url': 'track_url'} for i in tracks]}
