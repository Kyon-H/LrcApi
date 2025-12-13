import math
import pytest
from mod.textcompare import association, assoc_artists


def calc_ratio(title, artist, album):
    return (title * (artist + album) / 2.0) ** 0.5


def calc_ratio_v2(title, artist, album):
    aux = max(artist, album)
    return (title * aux) ** 0.5


def music_similarity(song_a: dict, song_b: dict) -> float:
    """
    song = {
        "title": str,
        "artist": str,
        "album": str,
    }
    """
    title_r = association(song_a["title"], song_b["title"])
    artist_r = assoc_artists(song_a["artist"], song_b["artist"])
    album_r = association(song_a["album"], song_b["album"])

    return calc_ratio_v2(title_r, artist_r, album_r)


@pytest.mark.parametrize(
    "song_a,song_b",
    [
        # 中文
        (
            {
                "title": "稻香",
                "artist": "周杰伦",
                "album": "魔杰座",
            },
            {
                "title": "稻 香",
                "artist": "周 杰 伦",
                "album": "魔杰座",
            },
        ),
        # 日文（假名缺失）
        (
            {
                "title": "夜に駆ける",
                "artist": "YOASOBI",
                "album": "THE BOOK",
            },
            {
                "title": "夜に駆け",
                "artist": "YOASOBI",
                "album": "THE BOOK",
            },
        ),
        # 英文（版本信息）
        (
            {
                "title": "Hello (Live)",
                "artist": "Adele",
                "album": "25",
            },
            {
                "title": "Hello",
                "artist": "Adele",
                "album": "25",
            },
        ),
    ],
)
def test_grouped_strong_match(song_a, song_b):
    """
    强匹配
    """
    ratio = music_similarity(song_a, song_b)
    assert ratio >= 0.85, f"ratio={ratio}"


@pytest.mark.parametrize(
    "song_a,song_b",
    [
        # 同歌不同专辑
        (
            {
                "title": "Lemon",
                "artist": "米津玄師",
                "album": "Lemon",
            },
            {
                "title": "Lemon",
                "artist": "米津玄師",
                "album": "STRAY SHEEP",
            },
        ),
        # 专辑缺失
        (
            {
                "title": "晴天",
                "artist": "周杰伦",
                "album": "",
            },
            {
                "title": "晴 天",
                "artist": "周 杰 伦",
                "album": "",
            },
        ),
    ],
)
def test_grouped_weak_match(song_a, song_b):
    """
    弱匹配
    """
    ratio = music_similarity(song_a, song_b)
    assert 0.70 <= ratio < 0.85, f"ratio={ratio}"


@pytest.mark.parametrize(
    "song_a,song_b",
    [
        # 同名不同歌手
        (
            {
                "title": "Hello",
                "artist": "Adele",
                "album": "",
            },
            {
                "title": "Hello",
                "artist": "Lionel Richie",
                "album": "",
            },
        ),
        # 标题相似但歌手不同
        (
            {
                "title": "稻香",
                "artist": "周杰伦",
                "album": "",
            },
            {
                "title": "稻米香",
                "artist": "李荣浩",
                "album": "",
            },
        ),
        # 日文同音异形 + 不同歌手
        (
            {
                "title": "カタオモイ",
                "artist": "Aimer",
                "album": "",
            },
            {
                "title": "片想い",
                "artist": "米津玄師",
                "album": "",
            },
        ),
    ],
)
def test_grouped_should_not_match(song_a, song_b):
    """无匹配"""
    ratio = music_similarity(song_a, song_b)
    assert ratio < 0.70, f"ratio={ratio}"


def test_title_is_gatekeeper_in_group():
    song_good = {
        "title": "稻香",
        "artist": "周杰伦",
        "album": "魔杰座",
    }

    song_same_artist = {
        "title": "晴天",
        "artist": "周杰伦",
        "album": "叶惠美",
    }
    ratio = music_similarity(song_good, song_same_artist)
    assert ratio == 0.0, f"ratio={ratio}"
