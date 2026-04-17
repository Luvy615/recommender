from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Product(BaseModel):
    id: str
    source: str
    source_id: str
    name: str
    category: str
    sub_category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    created_at: Optional[datetime] = None


class ProductSearch(BaseModel):
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    keyword: Optional[str] = None
    limit: int = 20


class ProductItem(BaseModel):
    name: str
    price: float
    image_url: str
    product_url: str
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
