import json
import aiohttp
import asyncio
import base64
import random
import string
import time
import logging

from functools import lru_cache

from mod import textcompare
from mod import tools

from mygo.devtools import no_error

headers: dict = {'User-Agent': '{"percent": 21.4, "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", "system": "Chrome '
                 '116.0 Win10", "browser": "chrome", "version": 116.0, "os": "win10"}', }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMMON_SEARCH_URL_KUGO = "http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={}&page=1&pagesize={}&showtype=1"
LYRIC_ID_URL_KUGO = "https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={}&album_audio_id="
LYRICS_URL_KUGO = "http://lyrics.kugou.com/download?ver=1&client=pc&id={}&accesskey={}&fmt=lrc&charset=utf8"


async def get_cover(session: aiohttp.ClientSession, m_hash: str, m_id: int | str) -> str:
    def _dfid(num):
        random_str = ''.join(random.sample(
            (string.ascii_letters + string.digits), num))
        return random_str

    # 获取a-z  0-9组成的随机23位数列
    def _mid(num):
        random_str = ''.join(random.sample(
            (string.ascii_letters[:26] + string.digits), num))
        return random_str

    music_url = 'https://wwwapi.kugou.com/yy/index.php'
    parameter = {
        'r': 'play/getdata',
        'hash': m_hash,
        'dfid': _dfid(23),
        'mid': _mid(23),
        'album_id': m_id,
        '_': str(round(time.time() * 1000))  # 时间戳
    }
    response = await session.get(music_url, headers=headers, params=parameter)
    json_data = await response.json(content_type=None)
    if json_data.get("data"):
        return json_data['data'].get("img")
    return ""


async def get_lyrics(session: aiohttp.ClientSession, m_hash: str) -> str:
    """
    根据歌曲hash获取base64歌词并解码
    :param session: aiohttp.ClientSession
    :param m_hash: 歌曲hash值
    :return: 歌词文本
    """
    # 获取 id 和 accesskey
    url = LYRIC_ID_URL_KUGO.format(m_hash)
    response = await session.get(url, headers=headers)
    if response.status != 200:
        return None
    lyrics_info = await response.json(content_type=None)
    if not lyrics_info["candidates"]:
        return None
    lyrics_id = lyrics_info["candidates"][0]["id"]
    lyrics_key = lyrics_info["candidates"][0]["accesskey"]

    # 获取base64编码歌词
    url = LYRICS_URL_KUGO.format(lyrics_id, lyrics_key)
    response = await session.get(url, headers=headers)
    if response.status != 200:
        return None
    lyrics_data = await response.json(content_type=None)
    lyrics_encode = lyrics_data["content"]

    # Base64 解码
    lrc_text = tools.standard_lrc(
        base64.b64decode(lyrics_encode).decode('utf-8'))
    return lrc_text


async def search_track(session: aiohttp.ClientSession, title: str, artist: str, album: str, search_for: str):
    """
    搜索歌词或封面
    """
    result_list = []
    limit = 3
    search_str = ' '.join(
        [item for item in [title, artist, album] if item])
    url = COMMON_SEARCH_URL_KUGO.format(search_str, 5)
    response = await session.get(url, headers=headers)
    if response.status != 200:
        return None

    song_info_t: dict = await response.json(content_type=None)
    song_info: list[dict] = song_info_t["data"]["info"]
    if len(song_info) < 1:
        return None

    candidate_songs = []
    for song_item in song_info:
        song_name = song_item["songname"]
        singer_name = song_item["singername"]
        album_id = song_item["album_id"]
        album_name = song_item["album_name"]
        # 计算相似度
        title_conform_ratio = textcompare.association(title, song_name)
        artist_conform_ratio = textcompare.assoc_artists(
            artist, singer_name)
        album_conform_ratio = textcompare.association(album, album_name)
        ratio: float = (title_conform_ratio *
                        (artist_conform_ratio + album_conform_ratio) / 2.0) ** 0.5
        if ratio >= 0.2:
            song_hash = song_item["hash"]
            candidate_songs.append(
                {'ratio': ratio, 'item': {
                    'artist': singer_name,
                    'title': song_name,
                    'album': album_name,
                    'album_id': album_id,
                    'song_hash': song_hash
                }})
    # 根据相似度排序
    if len(candidate_songs) < 1:
        return None
    candidate_songs.sort(
        key=lambda x: x['ratio'], reverse=True)
    # 取前3个
    candidate_songs = candidate_songs[:min(
        len(candidate_songs), limit)]
    # 获取歌词和封面
    for candidate in candidate_songs:
        track = candidate['item']
        ratio = candidate['ratio']
        # 根据 search_for 获取歌词/封面
        lyrics = ''
        cover = ''
        if search_for == 'lyrics':
            lyrics = await get_lyrics(session, track['song_hash'])
        elif search_for == 'cover':
            cover = await get_cover(session, track['song_hash'], track['album_id'])
        else:
            lyrics = await get_lyrics(session, track['song_hash'])
            cover = await get_cover(session, track['song_hash'], track['album_id'])
        # 结构化JSON数据
        music_json_data: dict = {
            "title": track['title'],
            "album": track['album'],
            "artist": track['artist'],
            "lyrics": lyrics,
            "cover": cover,
            "id": tools.calculate_md5(
                f"title:{track['title']};artists:{track['artist']};album:{track['album']}", base='decstr')
        }

        result_list.append(music_json_data)
    return result_list


async def a_search(title='', artist='', album='', search_for=''):
    if not any((title, artist, album)):
        return None
    async with aiohttp.ClientSession() as session:
        if title:
            return await search_track(session, title, artist, album, search_for)
        else:
            return await search_track(session, title, artist, album, search_for)


@lru_cache(maxsize=64)
@no_error(throw=logger.info,
          exceptions=(aiohttp.ClientError, asyncio.TimeoutError, KeyError, IndexError, AttributeError))
def search(title='', artist='', album='', search_for=''):
    return asyncio.run(a_search(title=title, artist=artist, album=album, search_for=search_for))


if __name__ == "__main__":
    print(search(album="十年"))
