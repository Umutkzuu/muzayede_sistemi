import os
from fastapi import FastAPI, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId 

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
    # Veritabanindaki tum urunler listeye eklenir
    cursor = item_collection.find().to_list(length=100)
    for doc in await cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    new_item = item.model_dump()
    result = await item_collection.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return new_item


@app.put("/items/{item_id}")
async def update_item(item_id: str, item_data: Item):
    """
    RMM Seviye 2: Kaynak URI üzerinden ({item_id}) belirtilir 
    ve işlem uygun HTTP metodu (PUT) ile yapılır.
    """
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Geçersiz Ürün ID formatı")

    update_result = await item_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item_data.model_dump()}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Güncellenecek ürün bulunamadı")
    
    return {"message": "Ürün başarıyla güncellendi", "id": item_id}


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    """
    RMM Seviye 2: Başarılı silme işlemi sonrası içerik dönmediği için 
    204 No Content kodu döndürülür.
    """
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Geçersiz Ürün ID formatı")

    delete_result = await item_collection.delete_one({"_id": ObjectId(item_id)})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Silinecek ürün bulunamadı")
    
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)