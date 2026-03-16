from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI(title="Müzayede Sistemi - Auth Service")

# Şifre hashleme ayarı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB Bağlantısı (Docker ağına uygun)
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongodb:27017")
client_db = AsyncIOMotorClient(MONGO_DETAILS)
database = client_db.auction
user_collection = database.get_collection("users")

class User(BaseModel):
    username: str
    password: str

@app.post("/register", status_code=201)
async def register(user: User):
    # Kullanıcı zaten var mı kontrol et
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Kullanıcı zaten mevcut")
    
    # Şifreyi hashle ve kaydet
    hashed_password = pwd_context.hash(user.password)
    new_user = {"username": user.username, "password": hashed_password}
    await user_collection.insert_one(new_user)
    return {"message": "Kullanıcı başarıyla oluşturuldu"}