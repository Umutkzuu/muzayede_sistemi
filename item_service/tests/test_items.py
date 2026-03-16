from fastapi.testclient import TestClient
import sys
import os

# Uygulamayı bulabilmesi için yolu ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_get_items_status():
    """Servisin ayakta olduğunu ve listeleme yaptığını doğrular."""
    response = client.get("/items")
    assert response.status_code == 200

def test_create_item_unauthorized():
    """Giriş yapmadan ürün eklenemediğini doğrular."""
    response = client.post("/items", json={"name": "Test", "description": "D", "starting_price": 10})
    assert response.status_code == 401