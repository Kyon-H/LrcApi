import os
import pytest
from app import app
from dotenv import load_dotenv

# load .env file
load_dotenv()
# Access environment variables
auth = os.environ.get('AUTH_TOKEN')


@pytest.fixture(scope="session")
def auth_client():
    with app.test_client() as client:
        if auth:
            client.environ_base['HTTP_AUTHORIZATION'] = auth
        yield client


def test_home_route(auth_client) -> None:
    # Use Flask test client to simulate requests
    response = auth_client.get('/')
    assert response.status_code < 400


def test_source_route(auth_client) -> None:
    response = auth_client.get('/src')
    assert response.status_code < 300


@pytest.mark.parametrize('title, artist, album, path', [
    ['使一颗心免于哀伤', '', '', ''],
    ['鳥の詩', 'Lia', "AIR Analog Collector's Edition – 鳥の詩 / Farewell song", '']
])
def test_lyrics_route(auth_client, title, artist, album, path) -> None:
    uri = f'/lyrics?title={title}&artist={artist}&album={album}&path={path}'
    response = auth_client.get(
        '/lyrics',
        query_string={
            'artist': artist,
            'title': title,
            'album': album,
            'path': path
        }
    )
    print(response.data)
    assert response.status_code == 200


@pytest.mark.parametrize('title, artist, album, path', [
    ['そういう感じのn回目', '東山奈央', 'とおりゃんせ', ''],
    ['鳥の詩', 'Lia', "AIR Analog Collector's Edition – 鳥の詩 / Farewell song", '']
])
def test_cover_route(auth_client, title, artist, album, path) -> None:
    # 防止有特殊字符&时被意外截断
    response = auth_client.get(
        '/cover',
        query_string={
            'artist': artist,
            'title': title,
            'album': album,
            'path': path
        }
    )
    assert response.status_code == 200
