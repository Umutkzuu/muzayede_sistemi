from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Müzayede Sistemi - Dispatcher")

# Servis adreslerini şimdilik değişken olarak tutalım (Docker'da güncelleyeceğiz)
ITEM_SERVICE_URL = "http://localhost:8001" 

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/items")
async def proxy_items():
    """Gelen isteği Item Service'e yönlendirir."""
    async with httpx.AsyncClient() as client:
        try:
            # İsteyi diğer servise paslıyoruz
            response = await client.get(f"{ITEM_SERVICE_URL}/items")
            return response.json()
        except httpx.ConnectError:
            # Servis henüz ayakta olmadığı için bu hatayı almamız normal
            raise HTTPException(status_code=502, detail="Item Service'e ulaşılamıyor.")