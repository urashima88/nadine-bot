from typing import Dict, Optional, Any, List

user_cart_edit_sessions: Dict[int, Dict] = {}

def get_cart_session(user_id: int) -> Optional[Dict]:
    return user_cart_edit_sessions.get(user_id)

def set_cart_session(user_id: int, cart_message_id: int):
    user_cart_edit_sessions[user_id] = {
        "article_numbers": [],
        "article_number_to_product_map": {},
        "total": 0,
        "index": 0,
        "article_number_to_message_id_map": {},
        "cart_message_id": cart_message_id,
    }
    
def edit_cart_session(
    user_id: int,
    article_numbers: List[int] = None, 
    article_number_to_product_map: Dict[int, Dict[str, Any]] = None,
) -> bool:
    if user_id in user_cart_edit_sessions:
        user_cart_edit_sessions[user_id]["article_numbers"] = article_numbers
        user_cart_edit_sessions[user_id]["article_number_to_product_map"] = article_number_to_product_map
        user_cart_edit_sessions[user_id]["total"] = len(article_numbers)
        return True
    return False

def delete_cart_session(user_id: int):
    if user_id in user_cart_edit_sessions:
        del user_cart_edit_sessions[user_id]