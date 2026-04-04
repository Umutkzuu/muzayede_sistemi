import pytest
from httpx import AsyncClient
from main import app 

@pytest.mark.asyncio
async def test_create_bid_fail():
    """Henüz servis yazılmadığı için bu testin çalışmaması veya fail etmesi gerekir."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "item_id": "test_item_123",
            "amount": 500.0
        }
        
        response = await ac.post("/bids", json=payload)
    
    assert response.status_code == 201
    assert response.json()["item_id"] == "test_item_123"