from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OutfitItem(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    product_price: float
    product_image_url: str
    product_url: str
    sort_order: int = 0


class Outfit(BaseModel):
    id: str
    user_id: str
    name: Optional[str] = None
    occasion: Optional[str] = None
    weather: Optional[str] = None
    style: Optional[str] = None
    rating: int = 0
    is_favorite: bool = False
    outfit_image: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[OutfitItem] = []


class OutfitCreate(BaseModel):
    user_id: str
    name: Optional[str] = None
    occasion: Optional[str] = None
    weather: Optional[str] = None
    style: Optional[str] = None
    items: List[OutfitItem]
    outfit_image: Optional[str] = None
    is_favorite: bool = True


class OutfitResponse(BaseModel):
    outfit_name: str
    items: List[OutfitItem]
    outfit_image: Optional[str] = None
