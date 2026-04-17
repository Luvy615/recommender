import requests
from typing import Optional


def get_weather(city: str) -> dict:
    return {
        'city': city,
        'weather': '晴',
        'temperature': 25,
        'description': '天气晴朗'
    }


def get_weather_suggestion(weather: str, temperature: float) -> str:
    if temperature < 10:
        return '天气较冷，建议穿厚外套、羽绒服等保暖衣物'
    elif temperature < 20:
        return '天气微凉，建议穿外套、毛衣等'
    elif temperature < 28:
        return '天气温暖，适合穿轻薄衣物'
    else:
        return '天气炎热，建议穿短袖、短裤等清凉衣物'
