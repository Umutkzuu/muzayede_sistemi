import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI(title="Müzayede Sistemi - Item Service (Internal)")

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongodb:27017")
client_db = AsyncIOMotorClient(MONGO_DETAILS)
item_collection = client_db.auction.items

class Item(BaseModel):
    name: str
    description: str
    starting_price: float

@app.get("/items")
async def get_items():
    items = []
    cursor = item_collection.find().to_list(length=100)
    for doc in await cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items

@app.post("/items")
async def create_item(item: Item):
    # Yetki kontrolü Dispatcher'da yapıldı, burası sadece kayıt yapar
    new_item = item.model_dump()
    result = await item_collection.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return new_item