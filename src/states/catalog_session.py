from typing import Dict, List

user_catalog_show_sessions: Dict[int, Dict] = {}

def get_catalog_session(user_id: int) -> Dict | None:
    return user_catalog_show_sessions.get(user_id)

def set_catalog_session(user_id: int, products: List[Dict], category: str):
    user_catalog_show_sessions[user_id] = {
        'products': products,
        'total': len(products),
        'sent': 0,
        'category': category
    }
    
def delete_catalog_session(user_id: int):
    if user_id in user_catalog_show_sessions:
        del user_catalog_show_sessions[user_id]
        
def set_edit_product_catalog_session(user_id: int, article_number: int, product_message_id: int, image_message_ids: List[int]):
    if user_id in user_catalog_show_sessions:
        if "edit_products" not in user_catalog_show_sessions[user_id]:
            user_catalog_show_sessions[user_id]["edit_products"] = {} 
        user_catalog_show_sessions[user_id]["edit_products"][article_number] = {
            "product_message_id": product_message_id,
            "image_message_ids": image_message_ids,
            "edit_images_message_id": None
    }

