from typing import Dict, List

order_show_sessions: Dict[int, Dict] = {}

def order_show_get_session(user_id: int) -> Dict | None:
    return order_show_sessions.get(user_id)

def order_show_set_session(user_id: int, orders: List[Dict]):
    order_show_sessions[user_id] = {
        'orders': orders,
        'total': len(orders),
        'sent': 0,
    }
    
def order_show_delete_session(user_id: int):
    if user_id in order_show_sessions:
        del order_show_sessions[user_id]
        
    