from typing import Dict, Any, Optional
from psycopg2.extras import NumericRange

create_product_sessions: Dict[int, Dict[str, Any]] = {}

def get_init_product_data() -> Dict[str, Any]:
    return {
        "data": {
            "name": "",
            "article_number": 0,
            "description": "",
            "price": 0,
            "category": "", 
            "production_time": None,
            "prod_limit": 0,
            "materials": [],
            "image_dir": ""
        },
        "product_message_id": None
    }

def get_create_product_session(user_id: int) -> Optional[Dict]:
    return create_product_sessions.get(user_id)

def set_create_product_session(user_id: int) -> Dict[str, Any]:
    if user_id not in create_product_sessions:
        create_product_sessions[user_id] = get_init_product_data()
    return create_product_sessions[user_id]
    
def clear_create_product_session(user_id: int):
    if user_id in create_product_sessions:
        create_product_sessions[user_id] = get_init_product_data()
    return create_product_sessions[user_id]