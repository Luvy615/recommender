from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.models.product import Product, ProductSearch
from backend.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str):
    service = ProductService()
    try:
        product = service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        service.close()


@router.post("/search", response_model=List[Product])
def search_products(search: ProductSearch):
    service = ProductService()
    try:
        products = service.search_products(search)
        return products
    finally:
        service.close()


@router.get("/category/{category}", response_model=List[Product])
def get_products_by_category(category: str, limit: int = 20):
    service = ProductService()
    try:
        products = service.get_products_by_category(category, limit)
        return products
    finally:
        service.close()


@router.get("/count/all")
def count_products():
    service = ProductService()
    try:
        count = service.count_products()
        return {"count": count}
    finally:
        service.close()
