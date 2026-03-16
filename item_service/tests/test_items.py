from fastapi.testclient import TestClient
import sys
import os

# Yolu ayarlayalım
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
except ImportError:
    app = None

client = TestClient(app)

def test_get_all_items_empty():
    """Veritabanı boşken bile boş bir liste dönmeli."""
    if app is None:
        import pytest
        pytest.fail("Item service main.py henüz hazır değil!")
        
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == [] # Başlangıçta boş liste bekliyoruz