from typing import Dict, List

user_order_show_sessions: Dict[int, Dict] = {}

def user_order_show_get_session(user_id: int) -> Dict | None:
    return user_order_show_sessions.get(user_id)

def user_order_show_set_session(user_id: int, orders: List[Dict]):
    user_order_show_sessions[user_id] = {
        'orders': orders,
        'total': len(orders),
        'sent': 0,
    }
    
def user_order_show_delete_session(user_id: int):
    if user_id in user_order_show_sessions:
        del user_order_show_sessions[user_id]
        
    