import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from fastapi.testclient import TestClient
from apps.api.main import app

def test_health_and_packs():
    client = TestClient(app)
    assert client.get('/health').json()['ok'] is True
    packs = client.get('/packs').json()
    assert any(p['slug']=='snap' for p in packs)
