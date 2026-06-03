import os
from logging import Logger

from telebot import TeleBot, types

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    catalog_menu_keyboard,
    catalog_control_keyboard, 
    main_menu_keyboard, 
    catalog_product_keyboard
)
from src.states.catalog_session import set_session, delete_session, get_session

def register_catalog_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_message)
    def handle_show_catalog(message):
        text = content_cfg.catalog_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=catalog_menu_keyboard(content_cfg),
            parse_mode='Markdown'
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('catalog_'))
    def handle_catalog_choice(call):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        
        category = call.data.split('_')[1]
        if category == "all":
            products = db.get_all_products()
        else:
            products = db.get_category_products(content_cfg.eng2ru_category_map.get(category))
            
        if not products:
            bot.send_message(call.message.chat.id, content_cfg.catalog_is_empty_message)
            return
        
        set_session(user_id, products, category)
        
        bot.send_message(
            call.message.chat.id,
            content_cfg.get_catalog_category_text(category, len(products)),
            parse_mode="Markdown",
            reply_markup=catalog_control_keyboard(content_cfg)
        )
        
        send_next_products(
            call.message.chat.id, user_id, count=1
        )
    
    def send_all_products_displayed_message(chat_id: int, user_id: int):
        bot.send_message(chat_id, content_cfg.all_products_displayed_message)
        bot.send_message(
            chat_id, 
            content_cfg.main_menu_message, 
            reply_markup=main_menu_keyboard(content_cfg)
        )
        delete_session(user_id)
        
    def send_next_products(chat_id: int, user_id: int, count: int):
        session = get_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.session_not_found_message)
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
                parse_mode='Markdown'
            )
        
        session['sent'] = sent + to_send
        if session['sent'] >= total:
            send_all_products_displayed_message(chat_id, user_id)
            
    def handle_products(message, count):
        user_id = message.from_user.id
        session = get_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.session_not_found_message)
            return
        
        send_next_products(message.chat.id, user_id, count)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_control_next_message)
    def handle_next_one(message):
        handle_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_control_next5_message)
    def handle_next_five(message):
        handle_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_control_stop_message)
    def handle_stop_catalog(message):
        user_id = message.from_user.id
        session = get_session(user_id)
        if session:
            delete_session(user_id)
            
        bot.send_message(
            message.chat.id,
            content_cfg.main_menu_message,
            reply_markup=main_menu_keyboard(content_cfg)
        )
        
        text = content_cfg.catalog_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=catalog_menu_keyboard(content_cfg),
            parse_mode="Markdown"
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_control_back_to_main_menu_message)
    def handle_back_to_main_menu(message):
        user_id = message.from_user.id
        delete_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.main_menu_message,
            reply_markup=main_menu_keyboard(content_cfg)
        )