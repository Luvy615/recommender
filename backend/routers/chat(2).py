from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
import uuid

from backend.agent.agent import run_agent
from backend.agent.llm_service import analyze_clothing_image, map_style_to_db, map_category_to_db
from backend.agent.skills.recommendation import search_products_by_conditions
from backend.agent.intent_classifier import extract_search_conditions

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    session_id: Optional[str] = None
    image_url: Optional[str] = None


class ImageSearchRequest(BaseModel):
    image_url: str
    user_id: str = "default"
    session_id: Optional[str] = None


@router.post("/")
async def chat(request: ChatRequest):
    if request.session_id is None:
        session_id = str(uuid.uuid4())
    else:
        session_id = request.session_id
    
    if request.image_url:
        analysis_result = await analyze_clothing_image(request.image_url)
        
        if analysis_result.get("success"):
            conditions = analysis_result.get("conditions", {})
            
            if conditions.get('style'):
                conditions['style'] = map_style_to_db(conditions['style'])
            if conditions.get('category'):
                conditions['category'] = map_category_to_db(conditions['category'])
            
            text_conditions = extract_search_conditions(request.message)
            
            for key, value in text_conditions.items():
                if key not in conditions:
                    conditions[key] = value
            
            # Search with style only first
            search_conditions = {'style': conditions.get('style')}
            products = search_products_by_conditions(search_conditions, limit=20)
            
            # If no results, try with color
            if not products and conditions.get('color'):
                search_conditions = {'style': conditions.get('style'), 'color': conditions.get('color')}
                products = search_products_by_conditions(search_conditions, limit=20)
            
            # If still no results, try just category
            if not products and conditions.get('category'):
                search_conditions = {'category': conditions.get('category')}
                products = search_products_by_conditions(search_conditions, limit=20)
            
            items = [
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
            
            from backend.agent.llm_service import generate_recommendation_reason
            message = await generate_recommendation_reason(request.message, items)
            
            return {
                'intent': 'image_search',
                'session_id': session_id,
                'filters': conditions,
                'items': items,
                'total': len(items),
                'analysis': analysis_result.get("description", ""),
                'message': f"{message}\n\n📷 图片分析：{analysis_result.get('description', '')}"
            }
    
    result = run_agent(request.message, request.user_id, session_id)
    return result


@router.post("/image-search")
async def image_search(request: ImageSearchRequest):
    if request.session_id is None:
        session_id = str(uuid.uuid4())
    else:
        session_id = request.session_id
    
    analysis_result = await analyze_clothing_image(request.image_url)
    
    if not analysis_result.get("success"):
        raise HTTPException(status_code=400, detail="图片分析失败，请更换图片重试")
    
    conditions = analysis_result.get("conditions", {})
    print(f"DEBUG: Raw conditions = {conditions}")
    
    if conditions.get('style'):
        old_style = conditions['style']
        conditions['style'] = map_style_to_db(conditions['style'])
        print(f"DEBUG: Style mapped {old_style} -> {conditions['style']}")
    if conditions.get('category'):
        old_cat = conditions['category']
        conditions['category'] = map_category_to_db(conditions['category'])
        print(f"DEBUG: Category mapped {old_cat} -> {conditions['category']}")
    
    # Search with style only (category from vision often doesn't match DB)
    search_conditions = {'style': conditions.get('style')}
    products = search_products_by_conditions(search_conditions, limit=20)
    
    # If no results, try with color
    if not products and conditions.get('color'):
        search_conditions = {'style': conditions.get('style'), 'color': conditions.get('color')}
        products = search_products_by_conditions(search_conditions, limit=20)
    
    # If still no results, try just category
    if not products and conditions.get('category'):
        search_conditions = {'category': conditions.get('category')}
        products = search_products_by_conditions(search_conditions, limit=20)
    
    items = [
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
    
    return {
        'intent': 'image_search',
        'session_id': session_id,
        'filters': conditions,
        'items': items,
        'total': len(items),
        'analysis': analysis_result.get("description", ""),
        'message': f"根据图片分析，为您找到风格相似的商品（{analysis_result.get('description', '')}）"
    }


@router.post("/tryon")
async def virtual_tryon(message: str, cloth_image: Optional[str] = None, user_id: str = "default"):
    return {
        'intent': 'virtual_tryon',
        'message': '虚拟试穿功能正在开发中，敬请期待！',
        'outfit_image': None
    }
