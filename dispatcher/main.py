from fastapi import FastAPI

# Uygulamayı tanımlıyoruz
app = FastAPI(title="Müzayede Sistemi - Dispatcher")

@app.get("/health")
async def health_check():
    """Sistemin ayakta olduğunu doğrulayan endpoint"""
    return {"status": "ok"}