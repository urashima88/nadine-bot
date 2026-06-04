from typing import Dict, List

user_catalog_show_sessions: Dict[int, Dict] = {}

def get_session(user_id: int) -> Dict | None:
    return user_catalog_show_sessions.get(user_id)

def set_session(user_id: int, products: List[Dict], category: str):
    user_catalog_show_sessions[user_id] = {
        'products': products,
        'total': len(products),
        'sent': 0,
        'category': category
    }
    
def delete_session(user_id: int):
    if user_id in user_catalog_show_sessions:
        del user_catalog_show_sessions[user_id]
        
    