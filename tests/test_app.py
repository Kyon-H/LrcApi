import os
from app import app
import pytest
from dotenv import load_dotenv

# load .env file
load_dotenv()
# Access environment variables
auth = os.environ.get('AUTH_TOKEN')


@pytest.fixture
def auth_client():
    with app.test_client() as client:
        if auth:
            client.environ_base['HTTP_AUTHORIZATION'] = auth
        yield client


def test_home_route(auth_client):
    # Use Flask test client to simulate requests
    response = auth_client.get('/')
    assert response.status_code < 400


def test_source_route(auth_client):
    response = auth_client.get('/src')
    assert response.status_code < 300


def test_lyrics_route(auth_client):
    response = auth_client.get('/lyrics?title=使一颗心免于哀伤')
    assert response.status_code == 200


def test_cover_route(auth_client):
    response = auth_client.get(
        '/cover',
        query_string={
            'artist': '東山奈央',
            'title': 'そういう感じのn回目',
            'album': 'とおりゃんせ',
            'path': '/home/load/Music/2025/2025.10/[251105]+TVアニメ「かくりよの宿飯+弐」OP&EDテーマ「とおりゃんせ／涙のレシピ」／東山奈央+[FLAC+48kHz／24bit]/05.+そういう感じのn回目.flac'
        }
    )
    print(response.data)
    assert response.status_code < 500
