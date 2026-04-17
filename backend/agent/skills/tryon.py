import base64
from typing import Optional


async def generate_tryon_image(
    cloth_image: str,
    style: str = '休闲',
    user_profile: dict = None
) -> Optional[str]:
    return None


def parse_cloth_description(message: str) -> dict:
    description = {
        'color': None,
        'style': None,
        'type': None
    }
    
    colors = ['白色', '黑色', '蓝色', '红色', '绿色', '黄色', '粉色', '紫色', '灰色', '棕色']
    for color in colors:
        if color in message:
            description['color'] = color
            break
    
    styles = ['商务', '休闲', '运动', '学院', '复古', '韩系']
    for style in styles:
        if style in message:
            description['style'] = style
            break
    
    types = ['衬衫', 'T恤', '裤子', '裙子', '连衣裙', '外套']
    for t in types:
        if t in message:
            description['type'] = t
            break
    
    return description
