from typing import List, Optional
from backend.models.product import ProductSearch
from backend.services.product_service import ProductService


def search_products(keyword: str, filters: dict = None, limit: int = 20) -> List[dict]:
    service = ProductService()
    try:
        search = ProductSearch(
            category=filters.get('category') if filters else None,
            color=filters.get('color') if filters else None,
            style=filters.get('style') if filters else None,
            season=filters.get('season') if filters else None,
            keyword=keyword,
            limit=limit
        )
        products = service.search_products(search)
        
        return [
            {
                'name': p.name,
                'price': p.price or 0,
                'image_url': p.image_url or '',
                'product_url': p.product_url or '',
                'category': p.category,
                'color': p.color,
                'style': p.style
            }
            for p in products
        ]
    finally:
        service.close()


def search_by_image(image_url: str, limit: int = 20) -> List[dict]:
    return []
