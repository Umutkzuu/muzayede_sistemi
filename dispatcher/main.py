import os
from fastapi import FastAPI, HTTPException, Header
import httpx

app = FastAPI(title="Müzayede Sistemi - Dispatcher")

# Servis URL'leri
ITEM_SERVICE_URL = os.getenv("ITEM_SERVICE_URL", "http://item_service:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8002")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- ITEM SERVICE YÖNLENDİRMELERİ ---

@app.get("/items")
async def proxy_get_items():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ITEM_SERVICE_URL}/items")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

@app.post("/items")
async def proxy_post_items(item: dict, authorization: str = Header(None)):
    """Gelen Token'ı (Authorization) alıp Item Service'e iletir."""
    async with httpx.AsyncClient() as client:
        try:
            # Token varsa headers sözlüğüne ekle
            headers = {"Authorization": authorization} if authorization else {}
            
            response = await client.post(
                f"{ITEM_SERVICE_URL}/items", 
                json=item, 
                headers=headers
            )
            
            # Eğer karşı servis hata dönerse (401 gibi), kullanıcıya o hatayı yansıt
            if response.status_code >= 400:
                return response.json() # Hata detayını gör
                
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

# --- AUTH SERVICE YÖNLENDİRMELERİ ---

@app.post("/register")
async def proxy_register(user: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def proxy_login(user: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/token", json=user)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))