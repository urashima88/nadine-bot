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
        
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=keyboards.main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog_message)
    def show_catalog(message):
        text = content_cfg.catalog_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.catalog_menu_keyboard(content_cfg),
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
            article_number = item['article_number']
            price = item['price']
            quantity = item['quantity']
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
        bot.answer_callback_query(call.id)
        
        if call.data.startswith('catalog_'):
            category = call.data.split('_')[1]
            if category == 'all':
                products = db.get_all_products()
            else:
                products = db.get_category_products(content_cfg.eng2ru_category_map[category])
        
            if not products:
                bot.send_message(call.message.chat.id, content_cfg.catalog_is_empty_message)
                return
            
            bot.send_message(
                call.message.chat.id,
                content_cfg.category2text_map[category],
                parse_mode='Markdown'
            )
            
            for product in products:
                article_number = product['article_number']
                name = product['name']
                price = product['price']
                image_dir = product['image_dir']
                product_text = content_cfg.get_product_text(name, article_number, price)
                if os.path.exists(image_dir):
                    image_filenames = os.listdir(image_dir)
                    if image_filenames:
                        media = []
                        for image_filename in image_filenames:
                            with open(os.path.join(image_dir, image_filename), 'rb') as f:
                                media.append(types.InputMediaPhoto(f.read()))
                        if media:
                            bot.send_media_group(call.message.chat.id, media)
                bot.send_message(
                    call.message.chat.id,
                    text=product_text,
                    reply_markup=keyboards.catalog_product_keyboard(content_cfg, article_number),
                    parse_mode='Markdown'
                )
                
    @bot.callback_query_handler(func=lambda call: call.data.startswith('detail_'))
    def show_product_details(call):
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[1])
        product = db.get_product_by_article_number(article_number)
        
        if not product:
            bot.send_message(call.message.chat.id, content_cfg.product_not_found_message)
            return
    
        description = product['description']
        price = product['price']
        category = product['category']
        image_dir = product['image_dir']
        materials_list = product['materials_list']
        
        text = content_cfg.get_product_details_text(
            article_number,
            description,
            price,
            materials_list,
            category
        )
        
        if os.path.exists(image_dir):
            image_filenames = os.listdir(image_dir)
            if image_filenames:
                media = []
                for image_filename in image_filenames:
                    with open(os.path.join(image_dir, image_filename), 'rb') as f:
                        media.append(types.InputMediaPhoto(f.read()))
                if media:
                    bot.send_media_group(call.message.chat.id, media)
        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=keyboards.product_keyboard(content_cfg, article_number),
            parse_mode='Markdown'
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
    def add_to_cart(call):
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[1])
        
        db.add_to_cart(user_id, article_number)
        
        bot.answer_callback_query(
            call.id,
            content_cfg.product_added_to_cart_message
        )
        