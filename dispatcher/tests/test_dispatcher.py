from fastapi.testclient import TestClient
import pytest
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client): 
    """Dispatcher'ın çalışıp çalışmadığını kontrol eden  test."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_items_routing(client): # client'ı parametre olarak alıyoruz
    """Dispatcher'ın /items isteğini yönlendirip yönlendirmediğini test eder."""
    
    response = client.get("/items")
    assert response.status_code == 502