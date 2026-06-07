from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.content_config import ContentConfig

def get_cart_content(
    user_id: int, 
    db: Storage, 
    content_cfg: ContentConfig, 
    logger: Logger,
    header_text: str
) -> str:
    logger.debug("get_cart_content CALL")
    
    cart_products = db.get_cart_products(user_id)
    
    if not cart_products:
        return ""
    
    total = 0
    cart_text = header_text
    
    for product in cart_products:
        article_number = product["article_number"]
        name = product["name"]
        price = product["price"]
        quantity = product["quantity"]
        
        product_total = price * quantity
        total += product_total
        cart_text += content_cfg.get_cart_product_text(
            name, article_number, price, quantity, product_total
        )
        
    cart_text += content_cfg.get_cart_total_text(total)
    return cart_text