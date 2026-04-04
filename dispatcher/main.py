import os
import httpx
import logging
from fastapi import FastAPI, HTTPException, Header, Depends, Request, Response
from fastapi.responses import JSONResponse
from jose import jwt, JWTError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Dispatcher")
# Dispatcher icin loglama mekanizmasi

app = FastAPI(title="Müzayede Sistemi - Dispatcher (RMM Level 2 Gateway)")
# Dispatcher, gelen istekleri ilgili mikroservislere yonlendirir


ITEM_SERVICE_URL = os.getenv("ITEM_SERVICE_URL", "http://item_service:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8002")
BID_SERVICE_URL = os.getenv("BID_SERVICE_URL", "http://bid_service:8003")
SECRET_KEY = "super-gizli-anahtar"
ALGORITHM = "HS256"


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    status_code = 500
    message = "Sunucu tarafında beklenmedik bir hata oluştu."
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    
    logger.error(f"HATA | Yol: {request.url.path} | Kod: {status_code} | Mesaj: {message}")
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "code": status_code, "message": message, "path": request.url.path}
    )


async def verify_access(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Yetkilendirme anahtarı (Token) eksik!")
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"YETKİ | Kullanıcı '{payload.get('sub')}' doğrulandı.")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token!")



@app.get("/items")
async def proxy_get_items():
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{ITEM_SERVICE_URL}/items")
        return response.json()

@app.post("/items")
async def proxy_post_items(item: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{ITEM_SERVICE_URL}/items", json=item)
        return JSONResponse(status_code=201, content=response.json())


@app.put("/items/{item_id}")
async def proxy_update_item(item_id: str, item_data: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        logger.info(f"PUT | Ürün {item_id} güncelleniyor. İsteyen: {user_data.get('sub')}")
        response = await client.put(f"{ITEM_SERVICE_URL}/items/{item_id}", json=item_data)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

@app.delete("/items/{item_id}")
async def proxy_delete_item(item_id: str, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        logger.warning(f"DELETE | Ürün {item_id} siliniyor! İsteyen: {user_data.get('sub')}")
        response = await client.delete(f"{ITEM_SERVICE_URL}/items/{item_id}")
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        
        return Response(status_code=204)


@app.post("/register")
async def proxy_register(user: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

@app.post("/login")
async def proxy_login(user: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/token", json=user)
        return response.json()


@app.post("/bids")
async def proxy_place_bid(bid_data: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        bid_data["user_id"] = user_data["sub"]
        response = await client.post(f"{BID_SERVICE_URL}/bids", json=bid_data)
        return JSONResponse(status_code=201, content=response.json())

@app.get("/bids/{item_id}")
async def proxy_get_bids(item_id: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{BID_SERVICE_URL}/bids/{item_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Bu ürün için henüz teklif bulunamadı.")
        return response.json()