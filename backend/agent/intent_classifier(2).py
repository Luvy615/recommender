from typing import Literal
from pydantic import BaseModel


class IntentResult(BaseModel):
    intent: str
    confidence: float
    details: dict = {}


def classify_intent(message: str) -> IntentResult:
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['生成', '试穿', '虚拟', '效果图', '穿上', '生成图片']):
        return IntentResult(
            intent='virtual_tryon',
            confidence=0.9,
            details={'type': 'tryon'}
        )
    
    if any(word in message_lower for word in ['找', '搜索', '有没有', '想找', '想买', '想买', '看看', '帮我', '给我']):
        return IntentResult(
            intent='search',
            confidence=0.85,
            details={'type': 'search'}
        )
    
    if any(word in message_lower for word in ['搭配', '穿什么', '穿啥', '怎么搭', '推荐穿', '应该', '穿搭', '穿法']):
        return IntentResult(
            intent='recommendation',
            confidence=0.9,
            details={'type': 'recommendation'}
        )
    
    return IntentResult(
        intent='general',
        confidence=0.5,
        details={'type': 'chat'}
    )


def extract_search_conditions(message: str) -> dict:
    conditions = {}
    message_lower = message.lower()
    
    categories = {
        '衬衫': '上衣', 't恤': '上衣', 't恤': '上衣', '卫衣': '上衣', '毛衣': '上衣',
        '外套': '上衣', '大衣': '上衣', 'polo': '上衣', '背心': '上衣',
        '裤子': '下装', '短裤': '下装', '牛仔裤': '下装', '裙子': '下装', '休闲裤': '下装',
        '连衣裙': '连衣裙',
        '休闲鞋': '鞋子', '运动鞋': '鞋子', '帆布鞋': '鞋子', 
        '高跟鞋': '鞋子', '凉鞋': '鞋子', '靴子': '鞋子',
        '包包': '配件', '帽子': '配件', '围巾': '配件', '腰带': '配件'
    }
    
    for keyword, category in categories.items():
        if keyword in message_lower:
            conditions['category'] = category
            break
    
    colors = [
        '白色', '黑色', '蓝色', '红色', '绿色', '黄色', '粉色', '紫色',
        '灰色', '棕色', '卡其色', '米色', '奶白色', '藏青色', '牛仔蓝'
    ]
    for color in colors:
        if color in message:
            conditions['color'] = color
            break
    
    styles = ['商务', '休闲', '运动', '学院', '复古', '韩系', '洛丽塔', '甜美', '性感']
    for style in styles:
        if style in message:
            conditions['style'] = style
            break
    
    seasons = ['春天', '春季', '夏天', '夏季', '秋天', '秋季', '冬天', '冬季']
    for season in seasons:
        if season in message:
            if '春' in season:
                conditions['season'] = '春夏'
            elif '夏' in season:
                conditions['season'] = '春夏'
            elif '秋' in season:
                conditions['season'] = '秋冬'
            elif '冬' in season:
                conditions['season'] = '秋冬'
            break
    
    occasions = ['商务', '出差', '约会', '日常', '上班', '聚会', '运动']
    for occasion in occasions:
        if occasion in message:
            conditions['occasion'] = occasion
            break
    
    return conditions
