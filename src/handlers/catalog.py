import os
from logging import Logger

from telebot import TeleBot, types

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    catalog_category_menu_keyboard,
    catalog_control_show_mode_keyboard, 
    common_main_menu_keyboard, 
    catalog_product_keyboard
)
from src.states.catalog_session import set_session, delete_session, get_session
from src.utils.wrappers import error_handler

def register_catalog_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.message)
    @err_handler
    def show_catalog(message):
        logger.debug("show_catalog CALL")
        
        header_text = content_cfg.catalog.category_menu.header_text
        bot.send_message(
            message.chat.id,
            header_text,
            reply_markup=catalog_category_menu_keyboard(content_cfg),
            parse_mode="Markdown"
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('catalog_'))
    @err_handler
    def handle_catalog_choice(call):
        logger.debug("handle_catalog_choice CALL")
        
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        category = call.data.split('_')[1]
        if category == "all":
            products = db.get_all_products()
        else:
            products = db.get_category_products(content_cfg.catalog.eng2ru_category_map.get(category))
            
        if not products:
            bot.send_message(call.message.chat.id, content_cfg.catalog.is_empty.message)
            return
        
        set_session(user_id, products, category)
        
        control_show_text = content_cfg.get_catalog_control_show_text(category, len(products))
        
        bot.send_message(
            call.message.chat.id,
            control_show_text,
            parse_mode="Markdown",
            reply_markup=catalog_control_show_mode_keyboard(content_cfg)
        )
        
        send_next_products(call.message.chat.id, user_id, count=1)
    
    def send_all_products_displayed_message(chat_id: int, user_id: int):
        logger.debug("send_all_products_displayed CALL")
        
        bot.send_message(chat_id, content_cfg.catalog.all_displayed.message)
        bot.send_message(
            chat_id, 
            content_cfg.cart.main_menu.message, 
            reply_markup=common_main_menu_keyboard(content_cfg)
        )
        delete_session(user_id)
        
    def send_next_products(chat_id: int, user_id: int, count: int):
        logger.debug("send_next_products CALL")
        
        session = get_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.catalog.session_not_found.message)
            return
        
        products = session["products"]
        sent = session["sent"]
        total = session["total"]
        
        if sent >= total:
            send_all_products_displayed_message(chat_id, user_id)
            return
        
        to_send = min(count, total-sent)
        for i in range(to_send):
            idx = sent + i
            product = products[idx]
            
            article_number = product["article_number"]
            name = product["name"]
            price = product["price"]
            image_dir = product["image_dir"]
            
            product_text = content_cfg.get_product_text(name, article_number, price)
            if os.path.exists(image_dir):
                image_filenames = os.listdir(image_dir)
                if image_filenames:
                    media = []
                    for image_filename in image_filenames:
                        with open(os.path.join(image_dir, image_filename), 'rb') as f:
                            media.append(types.InputMediaPhoto(f.read()))
                    if media:
                        bot.send_media_group(chat_id, media)
            bot.send_message(
                chat_id,
                text=product_text,
                reply_markup=catalog_product_keyboard(content_cfg, article_number),
                parse_mode="Markdown"
            )
        
        session["sent"] = sent + to_send
        if session["sent"] >= total:
            send_all_products_displayed_message(chat_id, user_id)
            
    def send_products(message, count):
        logger.debug("send_products CALL")
        
        user_id = message.from_user.id
        session = get_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        send_next_products(message.chat.id, user_id, count)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.next.message)
    @err_handler
    def send_next_one(message):
        logger.debug("send_next_one CALL")
        
        send_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.next5.message)
    @err_handler
    def send_next_five(message):
        logger.debug("send_next_five CALL")
        
        send_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.stop.message)
    @err_handler
    def stop_show_catalog(message):
        logger.debug("stop_show_catalog CALL")
        
        user_id = message.from_user.id
        session = get_session(user_id)
        if session:
            delete_session(user_id)
            
        bot.send_message(
            message.chat.id,
            content_cfg.cart.main_menu.message,
            reply_markup=common_main_menu_keyboard(content_cfg)
        )
        
        text = content_cfg.catalog.category_menu.header_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=catalog_category_menu_keyboard(content_cfg),
            parse_mode="Markdown"
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.go_back_to_main_menu.message)
    @err_handler
    def go_back_to_main_menu(message):
        logger.debug("go_back_to_main_menu CALL")
        
        user_id = message.from_user.id
        delete_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.cart.main_menu.message,
            reply_markup=common_main_menu_keyboard(content_cfg)
        )