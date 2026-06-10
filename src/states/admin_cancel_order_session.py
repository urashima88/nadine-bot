from typing import Dict, List

admin_cancel_order_sessions: Dict[int, Dict] = {}

def admin_cancel_order_get_session(user_id: int) -> Dict | None:
    return admin_cancel_order_sessions.get(user_id)

def admin_cancel_order_set_session(user_id: int, order_id: str):
    admin_cancel_order_sessions[user_id] = {
        'order_id': order_id,
    }
    
def admin_cancel_order_delete_session(user_id: int):
    if user_id in admin_cancel_order_sessions:
        del admin_cancel_order_sessions[user_id]