from typing import Dict, List

admin_order_show_sessions: Dict[int, Dict] = {}

def admin_order_show_get_session(user_id: int) -> Dict | None:
    return admin_order_show_sessions.get(user_id)

def admin_order_show_set_session(user_id: int, orders: List[Dict]):
    admin_order_show_sessions[user_id] = {
        'orders': orders,
        'total': len(orders),
        'sent': 0,
    }
    
def admin_order_show_delete_session(user_id: int):
    if user_id in admin_order_show_sessions:
        del admin_order_show_sessions[user_id]
        