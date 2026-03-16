from fastapi.testclient import TestClient
import pytest
import sys
import os

# Dispatcher klasörünü yola ekleyelim
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
except ImportError:
    app = None

def test_health_check():
    """Dispatcher'ın çalışıp çalışmadığını kontrol eden ilk test."""
    if app is None:
        pytest.fail("Ana uygulama (app) henüz main.py içinde tanımlanmamış!")
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}