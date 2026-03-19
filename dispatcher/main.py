import os
import httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from jose import jwt, JWTError

app = FastAPI(title="Müzayede Sistemi - Dispatcher")

ITEM_SERVICE_URL = os.getenv("ITEM_SERVICE_URL", "http://item_service:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8002")
SECRET_KEY = "super-gizli-anahtar"
ALGORITHM = "HS256"

# Merkezi Yetki Kontrolü
async def verify_access(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token bulunamadı! Lütfen giriş yapın.")
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token!")

@app.get("/items")
async def proxy_get_items():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ITEM_SERVICE_URL}/items")
        return response.json()

# DİKKAT: Burada verify_access bağımlılığını ekledik
@app.post("/items")
async def proxy_post_items(item: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient() as client:
        # Dispatcher onay verdi, isteği iç ağdaki servise ilet
        response = await client.post(f"{ITEM_SERVICE_URL}/items", json=item)
        return response.json()

@app.post("/register")
async def proxy_register(user: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user)
        return response.json()

@app.post("/login")
async def proxy_login(user: dict):
    async with httpx.AsyncClient() as client:
        # Auth service'deki /token endpoint'ine yönlendiriyoruz
        response = await client.post(f"{AUTH_SERVICE_URL}/token", json=user)
        return response.json()