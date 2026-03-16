from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI(title="Müzayede Sistemi - Auth Service")

# Şifre hashleme ayarı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

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

from datetime import datetime, timedelta
from jose import jwt

# Güvenlik için gizli anahtar (Hocaya sunarken bunu bir değişkenle yönettiğini söyleyebilirsin)
SECRET_KEY = "super-gizli-anahtar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.post("/token")
async def login(user: User):
    # Kullanıcıyı bul
    db_user = await user_collection.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre")
    
    # Token oluştur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": user.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}