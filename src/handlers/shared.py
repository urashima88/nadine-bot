from logging import Logger
import os
import re
from typing import List, Dict, Any, Tuple

from telebot import TeleBot, types
from telebot.types import Message

from src.storage import Storage
from src.config.content_config import ContentConfig
from src.utils.content import get_production_time_days_ru_format

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
    db: Storage, 
    tg_user_id: int, 
    call_data: str,
    content_cfg: ContentConfig,
    logger: Logger
) -> Tuple[bool, str]:
    logger.debug("check_and_update_user_profile_field CALL")
    
    new_value = message.text.strip()
    if not new_value:
        return False, content_cfg.common.profile.edit.empty_value.message
    
    if call_data == "edit_phone" and not re.match(r"^\+?[0-9\s\-\(\)]{10,20}$", new_value):      
        return False, content_cfg.common.profile.edit.phone.wrong_format.message
    
    if call_data == "edit_timezone":
        if new_value.startswith('+') or new_value.startswith('-'):
            sign = new_value[0]
            try:
                hours = int(new_value[1:])
            except:
                return False, content_cfg.common.profile.edit.timezone.wrong_format.message
        else:
            try:
                hours = int(new_value)
                sign = '+' if hours >= 0 else '-'
                hours = abs(hours)
            except:
                return False, content_cfg.common.profile.edit.timezone.wrong_format.message
        if hours > 12:
            return False, content_cfg.common.profile.edit.timezone.offset_exceed.message
        timezone_str = f"UTC{sign}{hours}"
        
        
    if call_data == "edit_full_name":
        success = db.update_user_full_name(tg_user_id, new_value)
        update_error_message = content_cfg.common.profile.edit.full_name.update_error.message
        success_message = content_cfg.common.profile.edit.full_name.success.message
    elif call_data == "edit_phone":
        success = db.update_user_phone(tg_user_id, new_value)
        update_error_message = content_cfg.common.profile.edit.phone.update_error.message
        success_message = content_cfg.common.profile.edit.phone.success.message
    elif call_data == "edit_timezone":
        success = db.update_user_timezone(tg_user_id, timezone_str)
        update_error_message = content_cfg.common.profile.edit.timezone.update_error.message
        success_message = content_cfg.common.profile.edit.timezone.success.message
    elif call_data == "edit_delivery_company":
        success = db.update_delivery_company(tg_user_id, new_value)
        update_error_message = content_cfg.common.profile.edit.delivery_company.update_error.message
        success_message = content_cfg.common.profile.edit.delivery_company.success.message
    else:
        success = db.update_delivery_point_address(tg_user_id, new_value)
        update_error_message = content_cfg.common.profile.edit.delivery_point_address.update_error.message
        success_message = content_cfg.common.profile.edit.delivery_point_address.success.message
        
    if not success:
        return False, update_error_message
    return success, success_message
    
def process_product(
    product: Dict[str, Any], 
    bot: TeleBot, 
    chat_id: int, 
    content_cfg: ContentConfig, 
    logger: Logger
) -> Tuple[str, List[Message]]:
    logger.debug("process_product CALL")
    
    text = prepare_product_text(
        product,
        content_cfg,
        logger
    )
    
    image_dir = product['image_dir']
    image_messages: List[Message] = []
    
    if os.path.exists(image_dir):
        image_filenames = os.listdir(image_dir)
        if image_filenames:
            media = []
            for image_filename in image_filenames:
                with open(os.path.join(image_dir, image_filename), 'rb') as f:
                    media.append(types.InputMediaPhoto(f.read()))
            if media:
                image_messages = bot.send_media_group(chat_id, media)
                
    return text, image_messages

def prepare_product_text(product: Dict[str, Any], content_cfg: ContentConfig, logger: Logger) -> str:
    logger.debug("prepare_product_text CALL")
    
    name = product['name']
    article_number = product['article_number']
    description = product['description']
    price = product['price']
    category = product['category']
    production_time = product['production_time']
    prod_limit = product['prod_limit']
    materials_list = product['materials_list']
    
    text = content_cfg.get_product_details_text(
        name,
        article_number,
        description,
        price,
        materials_list,
        category,
        production_time,
        prod_limit,
        get_production_time_days_ru_format(
            production_time, 
            content_cfg.product.production_time.unit_1,
            content_cfg.product.production_time.unit_234,
            content_cfg.product.production_time.unit_other
        )
    )
    
    return text

def prepare_product_info(
    chat_id: int, 
    bot: TeleBot, 
    db: Storage, 
    content_cfg: ContentConfig, 
    logger: Logger, 
    article_number: int
) -> Tuple[str, List[Message]]:
    product = db.get_product_by_article_number(article_number)
    
    if not product:
        bot.send_message(chat_id, content_cfg.product.not_found.message)
        return
    
    text, image_messages = process_product(
        product,
        bot,
        chat_id,
        content_cfg,
        logger
    )
    return text, image_messages