from typing import List, Optional
from backend.models.product import Product, ProductSearch
from backend.services.product_service import ProductService


def search_products_by_conditions(conditions: dict, limit: int = 20) -> List[Product]:
    service = ProductService()
    try:
        search = ProductSearch(
            category=conditions.get('category'),
            color=conditions.get('color'),
            style=conditions.get('style'),
            season=conditions.get('season'),
            keyword=conditions.get('keyword'),
            limit=limit
        )
        return service.search_products(search)
    finally:
        service.close()


def get_complementary_products(base_product: Product, limit: int = 5) -> List[Product]:
    service = ProductService()
    try:
        conditions = {}
        if base_product.category:
            opposite_categories = {
                '上衣': ['下装', '裤子', '裙子'],
                '下装': ['上衣', '鞋子'],
                '鞋子': ['上衣'],
                '配件': ['上衣', '下装']
            }
            cats = opposite_categories.get(base_product.category, [])
            conditions['category'] = cats[0] if cats else None
        
        if base_product.style:
            conditions['style'] = base_product.style
        
        search = ProductSearch(
            category=conditions.get('category'),
            style=conditions.get('style'),
            limit=limit
        )
        return service.search_products(search)
    finally:
        service.close()


def generate_outfit_from_products(top_products: List[Product], style: str = '休闲') -> dict:
    outfit_items = []
    
    tops = [p for p in top_products if p.category in ['上衣']]
    bottoms = [p for p in top_products if p.category in ['下装', '裤子', '裙子']]
    shoes = [p for p in top_products if p.category == '鞋子']
    accessories = [p for p in top_products if p.category == '配件']
    
    if tops:
        outfit_items.append({
            'type': '上衣',
            'product': tops[0],
            'sort_order': 1
        })
    
    if bottoms:
        outfit_items.append({
            'type': '下装',
            'product': bottoms[0],
            'sort_order': 2
        })
    
    if shoes:
        outfit_items.append({
            'type': '鞋子',
            'product': shoes[0],
            'sort_order': 3
        })
    
    if accessories:
        outfit_items.append({
            'type': '配件',
            'product': accessories[0],
            'sort_order': 4
        })
    
    return {
        'outfit_name': f'{style}搭配',
        'items': outfit_items,
        'total_price': sum(item['product'].price or 0 for item in outfit_items)
    }
