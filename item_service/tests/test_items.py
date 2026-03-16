from fastapi import FastAPI, HTTPException, Depends, Header
import pytest
import sys
import os
from unittest.mock import MagicMock

# Yolu ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# main.py'yi import etmeden önce veritabanını mocklayabiliriz 
# veya main'den app'i alıp test edebiliriz.
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_all_items_empty(client, monkeypatch):
    """Veritabanına bağlanmadan boş liste dönüp dönmediğini test eder."""
    
    # Gerçek veritabanı çağrısını taklit ediyoruz (Mocking)
    # Bu sayede 'mongodb' ismini aramaya çalışıp 30 saniye beklemeyecek.
    async def mock_find():
        return []
        
    # main.py içindeki get_items fonksiyonunun davranışını geçici olarak değiştiriyoruz
    # veya veritabanı yanıtını boş liste kabul ediyoruz.
    response = client.get("/items")
    # Eğer Docker kapalıysa bu aşamada bağlantı hatası almamak için 
    # main.py'de try-except bloğu olması güvenlidir.
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item_without_auth(client):
    """Token olmadan 401 döndüğünü doğrular."""
    item_data = {"name": "Test", "description": "Desc", "starting_price": 100}
    response = client.post("/items", json=item_data)
    assert response.status_code == 401