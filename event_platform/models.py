from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Ticket(BaseModel):
    type: str  # e.g., "VIP", "General"
    price: float
    total_slots: int
    sold: int = 0

class Review(BaseModel):
    user: str
    comment: str
    rating: int

class Event(BaseModel):
    title: str
    category: str
    date: str
    location: str
    tickets: List[Ticket] # EMBEDDED
    reviews: List[Review] = [] # EMBEDDED
    tags: List[str] = []