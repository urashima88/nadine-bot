import telebot
from telebot import types
import os
from logging import Logger

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
import src.keyboards as keyboards


def setup_handlers(bot: telebot.TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name
        db.register_user(user_id, username, full_name)
        
        welcome_text = content_cfg.get_welcome_message(full_name)
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=keyboards.main_menu(content_cfg))
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_message)
    def show_catalog(message):
        text = content_cfg.catalog_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.catalog_menu(content_cfg),
            parse_mode='Markdown'
        )
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_message)
    def show_cart(message):
        user_id = message.from_user.id
        cart_items = db.get_cart_items(user_id)
        
        if not cart_items:
            bot.send_message(message.chat.id, content_cfg.catalog_is_empty_message)
            return
        
        total = 0
        cart_text = content_cfg.user_cart_text
        
        for item in cart_items:
            article_number, price, quantity = item
            item_total = price * quantity
            total += item_total
            cart_text += content_cfg.get_cart_item_text(
                article_number, price, quantity, item_total
            )
            
        cart_text += content_cfg.get_cart_total_text(total)
        
        bot.send_message(
            message.chat.id,
            cart_text,
            reply_markup=keyboards.cart_keyboard(content_cfg),
            parse_mode='Markdown'
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('catalog_'))
    def handle_catalog(call):
        if call.data == 'catalog_all':
            products = db.get_all_products()
            
            if not products:
                bot.answer_callback_query(call.id, content_cfg.catalog_is_empty_message)
                return
            
            text = content_cfg.all_product_text
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            for product in products:
                article_number, price, image_dir_path = product
                product_text = content_cfg.get_product_text(article_number, price)
                
                image_dir_path = os.path.join(cfg.product_images_path, image_dir_path)
                
                if os.path.exists(image_dir_path):
                    image_filenames = os.listdir(image_dir_path)
                    if image_filenames:
                        media = []
                        for filename in image_filenames:
                            media.append(types.InputMediaPhoto(open(os.path.join(image_dir_path, filename), 'rb')))
  
                        bot.send_media_group(call.message.chat.id, media)
                        bot.send_message(
                            call.message.chat.id,
                            text=product_text,
                            reply_markup=keyboards.catalog_product_keyboard(content_cfg, article_number),
                            parse_mode='Markdown'
                        )
                    else:
                        bot.send_message(
                            call.message.chat.id,
                            text=product_text,
                            reply_markup=keyboards.catalog_product_keyboard(content_cfg, article_number),
                            parse_mode='Markdown'
                        )
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
                
    @bot.callback_query_handler(func=lambda call: call.data.startswith('detail_'))
    def show_product_details(call):
        article_number = int(call.data.split('_')[1])
        product = db.get_product_by_article_number(article_number)
        
        if not product:
            bot.answer_callback_query(call.id, content_cfg.product_not_found_message)
            return
        
        description, price, category, image_dir_path, materials = product
        
        text = content_cfg.get_product_details_text(
            article_number,
            description,
            price,
            materials,
            category
        )
        
        image_dir_path = os.path.join(cfg.product_images_path, image_dir_path)
        
        if os.path.exists(image_dir_path):
            image_filenames = os.listdir(image_dir_path)
            if image_filenames:
                media = []
                for filename in image_filenames:
                    media.append(types.InputMediaPhoto(open(os.path.join(image_dir_path, filename), 'rb')))

                bot.send_media_group(call.message.chat.id, media)
                bot.send_message(
                    call.message.chat.id,
                    text=text,
                    reply_markup=keyboards.product_keyboard(content_cfg, article_number),
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    text,
                    reply_markup=keyboards.product_keyboard(content_cfg, article_number),
                    parse_mode='Markdown'
                )
                
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
    def add_to_cart(call):
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[1])
        
        db.add_to_cart(user_id, article_number)
        
        bot.answer_callback_query(
            call.id,
            content_cfg.product_added_to_cart_message
        )
        