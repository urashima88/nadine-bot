from logging import Logger
from typing import List, Dict, Any, Tuple

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
    return get_content(cart_products, content_cfg, logger, header_text)

def get_order_content(
    order_id: str,
    db: Storage,
    content_cfg: ContentConfig,
    logger: Logger,
    header_text: str
) -> str:
    logger.debug("get_order_content CALL")
    
    order_products = db.get_order_products(order_id)
    if not order_products:
        return ""
    return get_content(order_products, content_cfg, logger, header_text)
        
def get_content(products: List[Dict[str, Any]], content_cfg: ContentConfig, logger: Logger, header_text: str) -> str:
    logger.debug("get_content CALL")
    
    total = 0
    content = header_text
    
    products_text, total = get_products_text_and_total_price(products, content_cfg, logger)
    
    content += products_text
    content += content_cfg.get_cart_total_text(total)
    return content

def get_products_text_and_total_price(products: List[Dict[str, Any]], content_cfg: ContentConfig, logger: Logger) -> Tuple[str, int]:
    logger.debug("get_products_text CALL")

    product_texts = []   
    total = 0
    
    for product in products:
        article_number = product["article_number"]
        name = product["name"]
        price = product["price"]
        quantity = product["quantity"]
        
        product_total = price * quantity
        total += product_total
        product_texts.append(
            content_cfg.get_cart_product_text(
                name, 
                article_number, 
                price, 
                quantity, 
                product_total
            )
        )
        
    products_text = "\n\n".join(product_texts)
        
    return products_text, total
        
        
    