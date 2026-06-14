import pytest
from app.main import app

@pytest.fixture
def client():
    app.testing = True 
    with app.test_client() as client:
        yield client

def test_health_status_code(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_health_response_keys(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert 'status' in response.json
    assert response.json['status'] == 'ok'
    assert 'timestamp' in response.json

def test_info_status_code(client):
    response = client.get('/info')
    assert response.status_code == 200
