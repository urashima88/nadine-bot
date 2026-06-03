from typing import Dict, Optional, Any, List

user_cart_edit_sessions: Dict[int, Dict] = {}

def get_cart_session(user_id: int) -> Optional[Dict]:
    return user_cart_edit_sessions.get(user_id)

def set_cart_session(user_id: int, article_numbers: List[int], article_number_to_item: Dict[int, Dict[str, Any]]):
    user_cart_edit_sessions[user_id] = {
        "article_numbers": article_numbers,
        "article_number_to_item": article_number_to_item,
        "total": len(article_number_to_item),
        "index": 0,
        "article_number_to_message_id": {}
    }

def delete_cart_session(user_id: int):
    if user_id in user_cart_edit_sessions:
        del user_cart_edit_sessions[user_id]