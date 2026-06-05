from typing import Dict, Any, Optional

user_order_sessions: Dict[int, Dict[str, Any]] = {}

def get_order_session(user_id: int) -> Optional[Dict]:
    return user_order_sessions.get(user_id)

def set_order_session(user_id: int, data: Dict):
    user_order_sessions[user_id] = data
    
def delete_order_session(user_id: int):
    if user_id in user_order_sessions:
        del user_order_sessions[user_id]
    
def update_order_session(user_id: int, **kwargs) -> bool:
    session = get_order_session(user_id)
    if session:
        session.update(kwargs)
        return True
    return False