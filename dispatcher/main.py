import os
import httpx
import logging
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

# Loglama Ayarları (GUI için veri kaynağı olacak)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Dispatcher")

app = FastAPI(title="Müzayede Sistemi - Dispatcher (RMM Level 2 Gateway)")

# Konfigürasyon
ITEM_SERVICE_URL = os.getenv("ITEM_SERVICE_URL", "http://item_service:8001")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8002")
SECRET_KEY = "super-gizli-anahtar"
ALGORITHM = "HS256"

# --- RMM LEVEL 2: GLOBAL HATA YÖNETİMİ ---
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Herhangi bir serviste hata oluştuğunda standart bir RMM formatı döner."""
    status_code = 500
    message = "Sunucu tarafında beklenmedik bir hata oluştu."
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    
    logger.error(f"HATA | Yol: {request.url.path} | Kod: {status_code} | Mesaj: {message}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": status_code,
            "message": message,
            "path": request.url.path
        }
    )

# --- MERKEZİ YETKİ KONTROLÜ (SECURITY GATEWAY) ---
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

# --- SERVİS YÖNLENDİRMELERİ ---

@app.get("/items")
async def proxy_get_items():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{ITEM_SERVICE_URL}/items")
            # RMM Level 2: Servis ayakta değilse 502 Bad Gateway döner
            if response.status_code >= 500:
                raise HTTPException(status_code=502, detail="Item Service şu an hizmet veremiyor.")
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Item Service zaman aşımına uğradı.")

@app.post("/items")
async def proxy_post_items(item: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(f"{ITEM_SERVICE_URL}/items", json=item)
            return JSONResponse(status_code=201, content=response.json()) # 201 Created
        except Exception as e:
            raise HTTPException(status_code=502, detail="Ürün ekleme servisine ulaşılamadı.")

@app.post("/register")
async def proxy_register(user: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user)
        # RMM: Kullanıcı zaten varsa 400 döner (veya servisten gelen kodu iletir)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

@app.post("/login")
async def proxy_login(user: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/token", json=user)
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre.")
        return response.json()

BID_SERVICE_URL = os.getenv("BID_SERVICE_URL", "http://bid_service:8003")

@app.post("/bids")
async def proxy_place_bid(bid_data: dict, user_data: dict = Depends(verify_access)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Güvenlik: User ID'yi kullanıcının gönderdiği veriden değil, TOKEN'dan alıyoruz!
        bid_data["user_id"] = user_data["sub"]
        
        response = await client.post(f"{BID_SERVICE_URL}/bids", json=bid_data)
        
        if response.status_code >= 400:
            return response.json()
        return JSONResponse(status_code=201, content=response.json())
    
# dispatcher/main.py içine eklenecek GET rotası

@app.get("/bids/{item_id}")
async def proxy_get_bids(item_id: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # İsteği iç ağdaki Bid Service'e (8003) paslıyoruz
            response = await client.get(f"{BID_SERVICE_URL}/bids/{item_id}")
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Bu ürün için henüz teklif bulunamadı.")
                
            return response.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Bid Service'e ulaşılamıyor.")