from typing import Dict, List, Any

user_catalog_sessions: Dict[int, Dict] = {}

def get_session(user_id: int) -> Dict | None:
    return user_catalog_sessions.get(user_id)

def set_session(user_id: int, products: List[Dict], category: str):
    user_catalog_sessions[user_id] = {
        'products': products,
        'total': len(products),
        'sent': 0,
        'category': category
    }
    
def delete_session(user_id: int):
    if user_id in user_catalog_sessions:
        del user_catalog_sessions[user_id]
        
    