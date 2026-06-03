from typing import Dict, List, Any

USER_CATALOG_SESSIONS: Dict[int, Dict] = {}

def get_session(user_id: int) -> Dict | None:
    return USER_CATALOG_SESSIONS.get(user_id)

def set_session(user_id: int, products: List[Dict], category: str):
    USER_CATALOG_SESSIONS[user_id] = {
        'products': products,
        'total': len(products),
        'sent': 0,
        'category': category
    }
    
def delete_session(user_id: int):
    if user_id in USER_CATALOG_SESSIONS:
        del USER_CATALOG_SESSIONS[user_id]