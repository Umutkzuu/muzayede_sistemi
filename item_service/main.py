import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from pydantic import BaseModel # Bunu ekledik

app = FastAPI(title="Müzayede Sistemi - Item Service")

# ÖNEMLİ: Docker içindeki ağ ismini (mongodb) kullanıyoruz
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.auction
item_collection = database.get_collection("items")

# Eser Modeli
class Item(BaseModel):
    name: str
    description: str
    starting_price: float

@app.get("/items", response_model=List[dict])
async def get_items():
    items = []
    cursor = item_collection.find()
    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)
    return items

@app.post("/items")
async def create_item(item: Item):
    new_item = item.dict()
    result = await item_collection.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return new_item