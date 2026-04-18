from langgraph.graph import StateGraph, END
import operator
import asyncio

from backend.agent.intent_classifier import classify_intent, extract_search_conditions
from backend.agent.skills.recommendation import search_products_by_conditions, generate_outfit_from_products
from backend.agent.skills.search import search_products
from backend.agent.tools.weather import get_weather, get_weather_suggestion
from backend.agent.llm_service import classify_intent_with_llm, generate_recommendation_reason, map_style_to_db


class AgentState(dict):
    pass


def intent_node(state: AgentState) -> AgentState:
    result = classify_intent(state['message'])
    state['intent'] = result
    return state


async def intent_node_llm(state: AgentState) -> AgentState:
    try:
        result = await classify_intent_with_llm(state['message'], state.get('user_profile'))
        from backend.agent.intent_classifier import IntentResult
        state['intent'] = IntentResult(
            intent=result.get("intent", "general"),
            confidence=result.get("confidence", 0.5),
            details={"conditions": result.get("conditions", {})}
        )
        state['conditions'] = result.get("conditions", {})
    except Exception as e:
        print(f"LLM intent error: {e}")
        result = classify_intent(state['message'])
        state['intent'] = result
        state['conditions'] = {}
    return state


def extract_conditions_node(state: AgentState) -> AgentState:
    intent_obj = state['intent']
    if hasattr(intent_obj, 'details') and intent_obj.details.get('conditions'):
        for key, value in intent_obj.details['conditions'].items():
            if key not in state['conditions']:
                state['conditions'][key] = value
    else:
        conditions = extract_search_conditions(state['message'])
        for key, value in conditions.items():
            if key not in state['conditions']:
                state['conditions'][key] = value
    
    if 'style' in state['conditions']:
        state['conditions']['style'] = map_style_to_db(state['conditions']['style'])
    
    return state


def search_node(state: AgentState) -> AgentState:
    conditions = state['conditions']
    products = search_products_by_conditions(conditions, limit=20)
    state['products'] = [
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
    return state


def recommend_node(state: AgentState) -> AgentState:
    products = search_products_by_conditions(state['conditions'], limit=30)
    state['outfit'] = generate_outfit_from_products(
        products,
        style=state['conditions'].get('style', '休闲')
    )
    return state


async def format_response_node(state: AgentState) -> AgentState:
    intent_obj = state['intent']
    intent = intent_obj.intent if hasattr(intent_obj, 'intent') else str(intent_obj)
    
    if intent == 'search':
        state['response'] = {
            'intent': 'search',
            'session_id': state['session_id'],
            'keyword': state['message'],
            'filters': state['conditions'],
            'items': state['products'],
            'total': len(state['products'])
        }
    elif intent == 'recommendation':
        outfit_items = []
        for item in state['outfit'].get('items', []):
            p = item['product']
            outfit_items.append({
                'name': p.name,
                'price': p.price or 0,
                'image_url': p.image_url or '',
                'product_url': p.product_url or ''
            })
        
        style = state['conditions'].get('style', '时尚')
        try:
            message = await generate_recommendation_reason(state['message'], outfit_items, state.get('user_profile'))
        except:
            message = f"为您推荐这套{style}风格的搭配："
        
        state['response'] = {
            'intent': 'recommendation',
            'session_id': state['session_id'],
            'outfit_name': state['outfit'].get('outfit_name', '时尚搭配'),
            'items': outfit_items,
            'outfit_image': None,
            'filters': state['conditions'],
            'message': message
        }
    else:
        state['response'] = {
            'intent': 'general',
            'session_id': state['session_id'],
            'message': '您好！我是您的智能服装穿搭助手，请问有什么可以帮您的？'
        }
    
    return state


def should_continue(state: AgentState) -> str:
    intent = state['intent'].intent if hasattr(state['intent'], 'intent') else state['intent']
    if intent in ['search', 'recommendation']:
        return "search"
    return "end"


def run_agent(message: str, user_id: str = "default", session_id: str = None):
    if session_id is None:
        import uuid
        session_id = str(uuid.uuid4())
    
    initial_state = {
        'message': message,
        'user_id': user_id,
        'session_id': session_id,
        'intent': None,
        'conditions': {},
        'products': [],
        'outfit': {},
        'response': {},
        'user_profile': {}
    }
    
    return asyncio.run(_run_agent(initial_state))


async def _run_agent(initial_state: dict):
    from backend.agent.intent_classifier import IntentResult
    
    await intent_node_llm(initial_state)
    
    extract_conditions_node(initial_state)
    
    search_node(initial_state)
    
    recommend_node(initial_state)
    
    await format_response_node(initial_state)
    
    return initial_state['response']
