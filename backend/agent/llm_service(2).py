import os
import json
import base64
import httpx
from typing import Optional

from backend.config import config


class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.chat_model = "qwen-plus"
        self.vision_model = "qwen-vl-max"
    
    async def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.chat_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"LLM API Error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"LLM Request Error: {e}")
            return None
    
    async def vision_chat(self, image_url: str, prompt: str = None, max_tokens: int = 2000) -> Optional[str]:
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        default_prompt = """分析这张衣服图片，提取以下信息并以JSON格式返回：
- style: 服装风格（如：休闲、商务、运动、韩系、复古、学院等）
- color: 主色调（如：黑色、白色、蓝色、红色等）
- category: 服装类别（如：上衣、下装、连衣裙、外套、鞋子、配件等）
- season: 适合季节（如：春夏、秋冬、春夏秋冬）
- description: 简单的风格描述

只返回JSON格式，不要其他内容。"""
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt or default_prompt
                    }
                ]
            }
        ]
        
        data = {
            "model": self.vision_model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"Vision API Error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"Vision Request Error: {e}")
            return None


llm_service = LLMService()

STYLE_MAPPING = {
    '甜美': '韩系',
    '可爱': '韩系',
    '性感': '商务',
    '成熟': '商务',
    '清新': '休闲',
    '文艺': '复古',
    '少女': '韩系',
    '通勤': '商务',
    '法式': '复古',
    '法国': '复古',
    '法式复古': '复古',
    '日系': '韩系',
    '欧美': '复古',
    '运动': '运动',
    '街头': '休闲',
    '学院': '学院',
    '优雅': '复古',
}

DB_STYLES = ['休闲', '商务', '运动', '学院', '复古', '韩系']

CATEGORY_MAPPING = {
    '上装': '上衣',
    '下装': '下装',
    '裤装': '下装',
    '裙装': '连衣裙',
    '鞋子': '鞋子',
    '鞋': '鞋子',
    '配饰': '配件',
    '配': '配件',
}


def map_style_to_db(style: str) -> str:
    if style in DB_STYLES:
        return style
    if style in STYLE_MAPPING:
        return STYLE_MAPPING[style]
    
    style_lower = style.lower()
    if '法' in style or 'french' in style_lower or ' france' in style_lower:
        return '复古'
    if '韩' in style or 'korean' in style_lower or ' korean' in style_lower:
        return '韩系'
    if '日' in style or 'japanese' in style_lower:
        return '韩系'
    if '欧美' in style or 'western' in style_lower or 'european' in style_lower:
        return '复古'
    if '运动' in style or 'sport' in style_lower or 'athletic' in style_lower:
        return '运动'
    if '学院' in style or 'preppy' in style_lower or 'academic' in style_lower:
        return '学院'
    if '商务' in style or 'business' in style_lower or 'formal' in style_lower:
        return '商务'
    if '休闲' in style or 'casual' in style_lower or 'leisure' in style_lower:
        return '休闲'
    
    return '休闲'


def map_category_to_db(category: str) -> str:
    if category in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[category]
    if category in ['上衣', '下装', '连衣裙', '鞋子', '配件']:
        return category
    
    cat_lower = category.lower()
    if '上' in category or 'shirt' in cat_lower or 'top' in cat_lower or 'tee' in cat_lower:
        return '上衣'
    if '下' in category or '裤' in category or 'pants' in cat_lower or 'bottom' in cat_lower:
        return '下装'
    if '裙' in category or 'dress' in cat_lower or 'skirt' in cat_lower:
        return '连衣裙'
    if '鞋' in category or 'shoe' in cat_lower or 'sneaker' in cat_lower or 'boot' in cat_lower:
        return '鞋子'
    if '配' in category or 'bag' in cat_lower or 'hat' in cat_lower or 'accessory' in cat_lower:
        return '配件'
    
    return category


async def classify_intent_with_llm(message: str, user_profile: dict = None) -> dict:
    profile_info = ""
    if user_profile:
        profile_info = f"\n用户信息：性别{user_profile.get('gender', '')}，年龄{user_profile.get('age', '')}岁，身高{user_profile.get('height', '')}cm，体重{user_profile.get('weight', '')}kg，身材{user_profile.get('body_type', '')}"
    
    system_prompt = """你是一个智能服装穿搭助手。用户会输入一句话，你需要判断用户的意图。

可能的意图：
1. search - 用户想搜索/查找商品
2. recommendation - 用户想要穿搭推荐/搭配建议
3. image_search - 用户上传了图片，想要找类似的衣服
4. virtual_tryon - 用户想要虚拟试穿/生成效果图
5. general - 一般对话/打招呼

请以JSON格式返回结果，包含：
- intent: 意图类型
- confidence: 置信度(0-1)
- conditions: 提取的搜索条件，包括category(商品类别如上衣/下装/鞋子/配件/连衣裙)、color(颜色)、style(风格如休闲/商务/运动/韩系)、occasion(场合如约会/上班/日常)

只返回JSON，不要其他内容。"""

    user_prompt = f"用户输入：{message}{profile_info}"

    try:
        response = await llm_service.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.1)
        
        if response:
            result = json.loads(response)
            return {
                "intent": result.get("intent", "general"),
                "confidence": result.get("confidence", 0.5),
                "conditions": result.get("conditions", {})
            }
    except Exception as e:
        print(f"Intent classification error: {e}")
    
    return {
        "intent": "general",
        "confidence": 0.5,
        "conditions": {}
    }


async def analyze_clothing_image(image_url: str) -> dict:
    try:
        response = await llm_service.vision_chat(
            image_url,
            prompt="""分析这张衣服图片，提取以下信息并以JSON格式返回：
- style: 服装风格（如：休闲、商务、运动、韩系、复古、学院等）
- color: 主色调（如：黑色、白色、蓝色、红色等）
- category: 服装类别（如：上衣、下装、连衣裙、外套、鞋子、配件等）
- season: 适合季节（如：春夏、秋冬、春夏秋冬）
- description: 简单的风格描述

只返回JSON格式，不要其他内容。"""
        )
        
        if response:
            result = json.loads(response)
            conditions = {}
            
            if result.get("style"):
                conditions["style"] = map_style_to_db(result["style"])
            if result.get("color"):
                conditions["color"] = result["color"]
            if result.get("category"):
                conditions["category"] = result["category"]
            if result.get("season"):
                conditions["season"] = result["season"]
            
            return {
                "success": True,
                "conditions": conditions,
                "description": result.get("description", ""),
                "raw_result": result
            }
    except Exception as e:
        print(f"Image analysis error: {e}")
    
    return {
        "success": False,
        "conditions": {},
        "description": "",
        "error": str(e)
    }


async def generate_recommendation_reason(message: str, outfit_items: list, user_profile: dict = None) -> str:
    if not outfit_items:
        return "为您找到以下商品"
    
    profile_info = ""
    if user_profile:
        profile_info = f"用户是{user_profile.get('gender', '')}性，{user_profile.get('body_type', '')}身材，"
    
    item_names = "、".join([item.get("name", "")[:20] for item in outfit_items[:3]])
    
    system_prompt = """你是一个专业的服装搭配顾问。请用2-3句话解释为什么推荐这些衣服给用户。语言要自然、亲切。"""
    
    user_prompt = f"{profile_info}推荐了以下商品：{item_names}。请解释推荐理由。"

    try:
        response = await llm_service.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=200)
        
        if response:
            return response
    except:
        pass
    
    return f"为您推荐这些精选商品"
