from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from jose import jwt

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.EventDB
SECRET_KEY = "SUPER_SECRET_KEY"

# Fixed Admin Credentials
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "123" 

# Optimization: Create compound index for category and date filtering
@app.on_event("startup")
async def startup_db():
    # Index helps with fast sorting and searching by category/date
    await db.events.create_index([("category", 1), ("date", -1)])

# 1. Register User
@app.post("/register")
async def register(data: dict):
    data["role"] = "user" 
    user_exists = await db.users.find_one({"username": data['username']})
    if user_exists or data['username'] == ADMIN_LOGIN:
        raise HTTPException(status_code=400, detail="User already exists")
    await db.users.insert_one(data)
    return {"message": "Success"}

# 2. Login
@app.post("/login")
async def login(data: dict):
    if data['username'] == ADMIN_LOGIN and data['password'] == ADMIN_PASSWORD:
        token = jwt.encode({"sub": ADMIN_LOGIN, "role": "admin"}, SECRET_KEY, algorithm="HS256")
        return {"token": token, "role": "admin", "username": ADMIN_LOGIN}
    
    user = await db.users.find_one({"username": data['username'], "password": data['password']})
    if user:
        token = jwt.encode({"sub": user["username"], "role": "user"}, SECRET_KEY, algorithm="HS256")
        return {"token": token, "role": "user", "username": user["username"]}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 3. Add Event (CRUD - Create)
@app.post("/events")
async def add_event(event: dict):
    event["reviews"] = []
    # If date is not provided in the request, default to today
    if "date" not in event:
        event["date"] = datetime.now().strftime("%Y-%m-%d")
    
    event["tickets"] = event.get("tickets", [{"type": "General", "price": 50, "sold": 0}])
    result = await db.events.insert_one(event)
    return {"id": str(result.inserted_id)}

# 4. List Events (CRUD - Read)
@app.get("/events")
async def list_events():
    # Sort events by date descending so newer ones appear first
    events = await db.events.find().sort("date", -1).to_list(100)
    for e in events: e["_id"] = str(e["_id"])
    return events

# 5. Get Event (CRUD - Read Single)
@app.get("/events/{id}")
async def get_event(id: str):
    event = await db.events.find_one({"_id": ObjectId(id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event["_id"] = str(event["_id"])
    return event

# 6. Delete Event (Admin Only)
@app.delete("/events/{id}")
async def delete_event(id: str, authorization: str = Header(None)):
    if not authorization: raise HTTPException(status_code=403)
    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if payload.get("role") != "admin": raise HTTPException(status_code=403)
    await db.events.delete_one({"_id": ObjectId(id)})
    return {"status": "deleted"}

# 7. Purchase Ticket
@app.post("/purchase/{id}")
async def buy_ticket(id: str, ticket_type: str, authorization: str = Header(None)):
    if not authorization: 
        raise HTTPException(status_code=401, detail="Login required")
    
    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = payload.get("sub")

    await db.events.update_one(
        {"_id": ObjectId(id), "tickets.type": ticket_type},
        {"$inc": {"tickets.$.sold": 1}}
    )
    
    booking = {
        "event_id": ObjectId(id), 
        "username": username, 
        "purchase_timestamp": datetime.utcnow(), # Time of purchase
        "ticket_type": ticket_type
    }
    await db.bookings.insert_one(booking)
    return {"status": "purchased"}

# 8. Add Review
@app.patch("/events/{id}/review")
async def add_review(id: str, review: dict):
    await db.events.update_one({"_id": ObjectId(id)}, {"$push": {"reviews": review}})
    return {"status": "added"}

# 9. Analytics
@app.get("/stats")
async def get_stats(authorization: str = Header(None)):
    if not authorization: raise HTTPException(status_code=403)
    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if payload.get("role") != "admin": raise HTTPException(status_code=403)

    pipeline = [
        {"$unwind": "$tickets"},
        {"$group": {
            "_id": "$category", 
            "total_rev": {"$sum": {"$multiply": ["$tickets.price", "$tickets.sold"]}}
        }},
        {"$sort": {"total_rev": -1}}
    ]
    return await db.events.aggregate(pipeline).to_list(100)