from logging import Logger
import re
from typing import List, Dict, Any, Tuple

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
        price = product.get("price") or product.get("price_at_order")
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

def check_and_update_user_profile_field(
    message, 
    bot: TeleBot, 
    db: Storage, 
    tg_user_id: int, 
    call_data: str,
    content_cfg: ContentConfig
) -> Tuple[bool, str]:
    new_value = message.text.strip()
    if not new_value:
        bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.empty_value.message)
        return
    
    if call_data == "edit_phone" and not re.match(r"^\+?[0-9\s\-\(\)]{10,20}$", new_value):
        bot.send_message(
            message.chat.id,
            content_cfg.common.user.profile.edit.phone.wrong_format.message
        )
        return
    
    if call_data == "edit_timezone":
        if new_value.startswith('+') or new_value.startswith('-'):
            sign = new_value[0]
            try:
                hours = int(new_value[1:])
            except:
                bot.send_message(
                    message.chat.id,
                    content_cfg.common.user.profile.edit.timezone.wrong_format.message
                )
                return
        else:
            try:
                hours = int(new_value)
                sign = '+' if hours >= 0 else '-'
                hours = abs(hours)
            except:
                bot.send_message(
                    message.chat.id,
                    content_cfg.common.user.profile.edit.timezone.wrong_format.message
                )
                return
        if hours > 12:
            bot.send_message(
                message.chat.id,
                content_cfg.common.user.profile.edit.timezone.offset_exceed.message
            )
            return
        timezone_str = f"UTC{sign}{hours}"
        
        
    if call_data == "edit_full_name":
        success = db.update_user_full_name(tg_user_id, new_value)
        success_message = content_cfg.common.user.profile.edit.full_name.update.message
    elif call_data == "edit_phone":
        success = db.update_user_phone(tg_user_id, new_value)
        success_message = content_cfg.common.user.profile.edit.phone.update.message
    elif call_data == "edit_timezone":
        success = db.update_user_timezone(tg_user_id, timezone_str)
        success_message = content_cfg.common.user.profile.edit.timezone.update.message
    elif call_data == "edit_delivery_company":
        success = db.update_delivery_company(tg_user_id, new_value)
        success_message = content_cfg.common.user.profile.edit.delivery_company.update.message
    else:
        success = db.update_delivery_point_address(tg_user_id, new_value)
        success_message = content_cfg.common.user.profile.edit.delivery_point_address.update.message
    return success, success_message
    