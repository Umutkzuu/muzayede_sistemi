import os
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Müzayede Sistemi - Dispatcher")

# Docker compose içindeki servis adını kullanıyoruz: "item_service"
ITEM_SERVICE_URL = os.getenv("ITEM_SERVICE_URL", "http://item_service:8001")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/items")
async def proxy_get_items():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ITEM_SERVICE_URL}/items")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

@app.post("/items")
async def proxy_post_items(item: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{ITEM_SERVICE_URL}/items", json=item)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))