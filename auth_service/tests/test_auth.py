from fastapi.testclient import TestClient
import pytest
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
except ImportError:
    app = None

client = TestClient(app)

def test_register_user_fail():
    """Kullanıcı kayıt fonksiyonu henüz yazılmadığı için fail etmeli."""
    if app is None:
        pytest.fail("Auth service main.py henüz hazır değil!")
        
    user_data = {"username": "umut", "password": "123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 201