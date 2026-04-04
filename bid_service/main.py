import os
from fastapi import FastAPI, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI(title="Müzayede Sistemi - Bid Service (NoSQL)")


MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.bid_db 
bid_collection = database.get_collection("bids")

class Bid(BaseModel):
    item_id: str
    user_id: str
    amount: float
    timestamp: datetime = None

@app.post("/bids", status_code=201)
async def place_bid(item_id: str = Body(...), amount: float = Body(...), user_id: str = Body("system")):
    
    new_bid = {
        "item_id": item_id,
        "amount": amount,
        "user_id": user_id,
        "timestamp": datetime.utcnow()
    }
    result = await bid_collection.insert_one(new_bid)
    new_bid["_id"] = str(result.inserted_id)
    return new_bid

@app.get("/bids/{item_id}")
async def get_bids(item_id: str):
   
    bids = []
    cursor = bid_collection.find({"item_id": item_id}).sort("amount", -1)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        bids.append(doc)
    return bids