from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from backend.models.product import ProductSearch
from backend.services.product_service import ProductService

router = APIRouter(prefix="/api/search", tags=["search"])


def extract_search_filters(message: str) -> dict:
    filters = {}
    message_lower = message.lower()
    
    categories = {
        '衬衫': '上衣', 't恤': '上衣', '卫衣': '上衣', '毛衣': '上衣',
        '外套': '上衣', '大衣': '上衣', 'polo': '上衣',
        '裤子': '下装', '短裤': '下装', '牛仔裤': '下装', '裙子': '下装',
        '连衣裙': '连衣裙', '休闲鞋': '鞋子', '运动鞋': '鞋子',
        '帆布鞋': '鞋子', '高跟鞋': '鞋子', '凉鞋': '鞋子', '靴子': '鞋子',
        '包包': '配件', '帽子': '配件', '围巾': '配件', '腰带': '配件'
    }
    
    for keyword, category in categories.items():
        if keyword in message_lower:
            filters['category'] = category
            break
    
    colors = ['白色', '黑色', '蓝色', '红色', '绿色', '黄色', '粉色', '紫色', '灰色', '棕色', '卡其色', '米色', '奶白色', '藏青色']
    for color in colors:
        if color in message:
            filters['color'] = color
            break
    
    styles = ['商务', '休闲', '运动', '学院', '复古', '韩系', '洛丽塔']
    for style in styles:
        if style in message:
            filters['style'] = style
            break
    
    return filters


@router.post("/")
async def search_products(message: str, user_id: str = "default"):
    service = ProductService()
    try:
        filters = extract_search_filters(message)
        
        search = ProductSearch(
            category=filters.get('category'),
            color=filters.get('color'),
            style=filters.get('style'),
            keyword=message,
            limit=20
        )
        
        products = service.search_products(search)
        
        items = []
        for p in products:
            items.append({
                'name': p.name,
                'price': p.price or 0,
                'image_url': p.image_url or '',
                'product_url': p.product_url or '',
                'category': p.category,
                'color': p.color,
                'style': p.style
            })
        
        return {
            'keyword': message,
            'filters': filters,
            'items': items,
            'total': len(items)
        }
    finally:
        service.close()
