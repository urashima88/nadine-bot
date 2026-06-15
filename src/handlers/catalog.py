import os
from logging import Logger
from typing import Tuple
from pathlib import Path

from telebot import TeleBot, types
from psycopg2.extras import NumericRange

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    catalog_category_menu_keyboard,
    catalog_control_show_mode_keyboard, 
    main_menu_keyboard, 
    catalog_product_keyboard,
    admin_catalog_category_menu_keyboard,
    admin_catalog_control_show_mode_keyboard,
    admin_catalog_product_keyboard,
    admin_main_menu_keyboard,
    catalog_edit_product_keyboard,
    catalog_edit_product_category_keyboard,
    catalog_edit_product_images_keyboard
)
from src.states.catalog_session import (
    set_catalog_session, 
    delete_catalog_session, 
    get_catalog_session,
    set_edit_product_catalog_session
)
from src.utils.wrappers import error_handler
from src.handlers.shared import process_product, prepare_product_text, prepare_product_info
from src.utils.clean import delete_message
from src.utils.file import download_image_bytes

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
        
        set_catalog_session(user_id, products, category)
        
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
        if db.is_admin(user_id):
            keyboard = admin_main_menu_keyboard(content_cfg)
        else:
            keyboard = main_menu_keyboard(content_cfg)
            
        bot.send_message(
            chat_id, 
            content_cfg.catalog.main_menu.message, 
            reply_markup=keyboard
        )
        delete_catalog_session(user_id)
        
    def send_next_products(chat_id: int, user_id: int, count: int):
        logger.debug("send_next_products CALL")
        
        session = get_catalog_session(user_id)
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
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        send_next_products(message.chat.id, user_id, count)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.next.message)
    @err_handler
    def send_next_one_product(message):
        logger.debug("send_next_one_product CALL")
        
        send_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.next5.message)
    @err_handler
    def send_next_five_products(message):
        logger.debug("send_next_five_products CALL")
        
        send_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.control_show.stop.message)
    @err_handler
    def stop_show_catalog(message):
        logger.debug("stop_show_catalog CALL")
        
        user_id = message.from_user.id
        session = get_catalog_session(user_id)
        if session:
            delete_catalog_session(user_id)
            
        bot.send_message(
            message.chat.id,
            content_cfg.catalog.main_menu.message,
            reply_markup=main_menu_keyboard(content_cfg)
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
        delete_catalog_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.cart.main_menu.message,
            reply_markup=main_menu_keyboard(content_cfg)
        )

    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.admin.message)
    @err_handler
    def admin_show_catalog(message):
        logger.debug("admin_show_catalog CALL")
        
        header_text = content_cfg.catalog.admin.category_menu.header_text
        bot.send_message(
            message.chat.id,
            header_text,
            reply_markup=admin_catalog_category_menu_keyboard(content_cfg),
            parse_mode="Markdown"
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_catalog_'))
    @err_handler
    def admin_handle_catalog_choice(call):
        logger.debug("admin_handle_catalog_choice CALL")
        
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        category = call.data.split('_')[2]
        if category == "all":
            products = db.admin_get_all_products()
        else:
            products = db.admin_get_category_products(content_cfg.catalog.eng2ru_category_map.get(category))
            
        if not products:
            bot.send_message(call.message.chat.id, content_cfg.catalog.is_empty.message)
            return
        
        set_catalog_session(user_id, products, category)
        
        control_show_text = content_cfg.get_catalog_control_show_text(category, len(products))
        
        bot.send_message(
            call.message.chat.id,
            control_show_text,
            parse_mode="Markdown",
            reply_markup=admin_catalog_control_show_mode_keyboard(content_cfg)
        )
        
        admin_send_next_products(call.message.chat.id, user_id, count=1)
        
    def admin_send_next_products(chat_id: int, user_id: int, count: int):
        logger.debug("admin_send_next_products CALL")
        
        session = get_catalog_session(user_id)
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
            article_number = product['article_number']
            
            text = process_product(
                product,
                bot,
                chat_id,
                content_cfg,
                logger
            )
            
            bot.send_message(
                chat_id,
                text=text,
                reply_markup=admin_catalog_product_keyboard(content_cfg, article_number),
                parse_mode="Markdown"
            )
        
        session["sent"] = sent + to_send
        if session["sent"] >= total:
            send_all_products_displayed_message(chat_id, user_id)
            
    def admin_send_products(message, count):
        logger.debug("admin_send_products CALL")
        
        user_id = message.from_user.id
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        admin_send_next_products(message.chat.id, user_id, count)
            
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.admin.control_show.next.message)
    @err_handler
    def admin_send_next_one_product(message):
        logger.debug("admin_send_next_one_product CALL")
        
        admin_send_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.admin.control_show.next5.message)
    @err_handler
    def admin_send_next_five_products(message):
        logger.debug("admin_send_next_five_products CALL")
        
        admin_send_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.admin.control_show.stop.message)
    @err_handler
    def admin_stop_show_catalog(message):
        logger.debug("admin_stop_show_catalog CALL")
        
        user_id = message.from_user.id
        session = get_catalog_session(user_id)
        if session:
            delete_catalog_session(user_id)
            
        bot.send_message(
            message.chat.id,
            content_cfg.catalog.main_menu.message,
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )
        
        text = content_cfg.catalog.category_menu.header_text
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=admin_catalog_category_menu_keyboard(content_cfg),
            parse_mode="Markdown"
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.catalog.admin.control_show.go_back_to_main_menu.message)
    @err_handler
    def go_back_to_main_menu(message):
        logger.debug("admin_go_back_to_main_menu CALL")
        
        user_id = message.from_user.id
        delete_catalog_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.cart.main_menu.message,
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_product_'))
    @err_handler
    def edit_product(call):
        logger.debug("edit_product CALL")
        
        user_id = call.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
            
        article_number = int(call.data.split('_')[2])
        prepare_edit_product(call.message.chat.id, user_id, article_number)
        
    def prepare_edit_product(chat_id: int, user_id: int, article_number: int):
        logger.debug("prepare_edit_product CALL")
        
        text, image_messages = prepare_product_info(chat_id, bot, db, content_cfg, logger, article_number)
        
        image_message_ids = []
        for image_message in image_messages:
            image_message_ids.append(image_message.message_id)
        
        sent = bot.send_message(
            chat_id,
            text=text,
            reply_markup=catalog_edit_product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )
        
        set_edit_product_catalog_session(user_id, article_number, sent.message_id, image_message_ids)
        
        
    def edit_product_text(article_number: int, chat_id: int, product_message_id: int) -> Tuple[bool, str]:
        logger.debug("edit_product_text CALL")
    
        product = db.get_product_by_article_number(article_number)
    
        if not product:
            return False, content_cfg.catalog.admin.edit.not_found.message
        
        product_text = prepare_product_text(product, content_cfg, logger)
        
        bot.edit_message_text(
            product_text,
            chat_id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=catalog_edit_product_keyboard(content_cfg, article_number)
        )
        return True, ""
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_name_"))
    @err_handler
    def edit_name(call):
        logger.debug("edit_name CALL")
        
        user_id = call.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        article_number = int(call.data.split('_')[2])
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.name.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_name,
            article_number,
            product_message_id
        )
        
    def save_name(message, article_number: int, product_message_id: int):
        logger.debug("save_name CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_name = message.text.strip()
        if not new_name:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return

        success = db.update_product_name(article_number, new_name)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.name.success.message,
                    parse_mode="Markdown",
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.name.update_error.message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_description_"))
    @err_handler
    def edit_description(call):
        logger.debug("edit_description CALL")
        
        user_id = call.from_user.id
        
        article_number = int(call.data.split('_')[2])
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.description.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_description,
            article_number,
            product_message_id
        )
        
    def save_description(message, article_number: int, product_message_id: int):
        logger.debug("save_description CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_description = message.text.strip()
        if not new_description:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return

        success = db.update_product_description(article_number, new_description)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.description.success.message,
                    parse_mode="Markdown",
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.description.update_error.message)
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_price_"))
    @err_handler
    def edit_price(call):
        logger.debug("edit_price CALL")
        
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[2])
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.price.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_price,
            article_number,
            product_message_id
        )
        
    def save_price(message, article_number: int, product_message_id: int):
        logger.debug("save_price CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_price = message.text.strip().replace(',', '.')
        if not new_price:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return
        
        try:
            new_price = float(new_price)
        except:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.price.not_number.message)
            return
        
        if new_price < 0:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.price.negative.message)
            return

        success = db.update_product_price(article_number, new_price)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.price.success.message,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.price.update_error.message)
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_category_"))
    @err_handler
    def edit_category(call):
        logger.debug("edit_category CALL")
        
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[2])
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return

        prompt = content_cfg.catalog.admin.edit.category.text
        bot.send_message(
            call.message.chat.id, 
            prompt,
            parse_mode="Markdown",
            reply_markup=catalog_edit_product_category_keyboard(content_cfg, article_number)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_"))
    @err_handler
    def choose_category(call):
        logger.debug("choose_category CALL")
        
        call_data = call.data.split('_')
        new_category = call_data[1]
        article_number = int(call_data[2])
        user_id = call.from_user.id
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        new_category = content_cfg.catalog.eng2ru_category_map[new_category]
        success = db.update_product_category(article_number, new_category)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                call.message.chat.id,
                product_message_id
            )
            
            delete_message(bot, call.message.chat.id, call.message.message_id, logger)
            if edit_success:
                bot.send_message(
                    call.message.chat.id, 
                    content_cfg.catalog.admin.edit.category.success.message,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(call.message.chat.id, msg)
        else:
            bot.send_message(call.message.chat.id, content_cfg.catalog.admin.edit.price.update_error.message)
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_production_time_"))
    @err_handler
    def edit_production_time(call):
        logger.debug("edit_production_time CALL")
        
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[3])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.production_time.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_production_time,
            article_number,
            product_message_id
        )
        
    def save_production_time(message, article_number: int, product_message_id: int):
        logger.debug("save_production_time CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_production_time_str = message.text.strip()
        if not new_production_time_str:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return
        
        if '-' in new_production_time_str:
            parts = new_production_time_str.split('-')
            try:
                lower = int(parts[0].strip())
            except:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.lower.not_number.message
                )
                return
            
            if lower < 0:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.lower.negative.message
                )
                return
            
            try:
                upper = int(parts[1].strip())
            except:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.upper.not_number.message
                )
                return
            
            if upper < 0:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.upper.negative.message
                )
                return
            
            new_production_time = NumericRange(lower, upper, bounds="[]")

        else:
            try:
                upper = int(new_production_time_str)
            except:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.upper.not_number.message
                )
                return
            
            if upper < 0:
                bot.send_message(
                    message.chat.id,
                    content_cfg.catalog.admin.edit.production_time.upper.negative.message
                )
                return
            
            new_production_time = NumericRange(upper, upper, bounds="[]")

        success = db.update_product_production_time(article_number, new_production_time)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.production_time.success.message,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.production_time.update_error.message)
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_prod_limit_"))
    @err_handler
    def edit_prod_limit(call):
        logger.debug("edit_prod_limit CALL")
        
        user_id = call.from_user.id
        
        article_number = int(call.data.split('_')[3])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.prod_limit.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_prod_limit,
            article_number,
            product_message_id
        )
        
    def save_prod_limit(message, article_number: int, product_message_id: int):
        logger.debug("save_prod_limit CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_prod_limit = message.text.strip()
        if not new_prod_limit:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return
        
        try:
            new_prod_limit = int(new_prod_limit)
        except:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.prod_limit.not_number.message)
            return
        
        if new_prod_limit < 0:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.prod_limit.negative.message)
            return

        success = db.update_product_price(article_number, new_prod_limit)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.prod_limit.success.message,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.prod_limit.update_error.message)
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_materials_"))
    @err_handler
    def edit_materials(call):
        logger.debug("edit_materials CALL")
        
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[2])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        product_message_id = session["edit_products"][article_number]["product_message_id"]

        prompt = content_cfg.catalog.admin.edit.materials.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_materials,
            article_number,
            product_message_id
        )
        
    def save_materials(message, article_number: int, product_message_id: int):
        logger.debug("save_materials CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        new_materials_str = message.text.strip()
        if not new_materials_str:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.empty_value.message
            )
            return

        new_materials = []
        for material in new_materials_str.split(','):
            new_materials.append(material.strip())
            
        success = db.update_product_materials(article_number, new_materials)
        
        if success:
            edit_success, msg = edit_product_text(
                article_number,
                message.chat.id,
                product_message_id
            )
            
            delete_message(bot, message.chat.id, message.message_id, logger)
            if edit_success:
                bot.send_message(
                    message.chat.id, 
                    content_cfg.catalog.admin.edit.materials.success.message,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.materials.update_error.message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_images_"))
    @err_handler
    def edit_images(call):
        logger.debug("edit_images CALL")
        
        user_id = call.from_user.id
        article_number = int(call.data.split('_')[2])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        prompt = content_cfg.catalog.admin.edit.images.text
        sent = bot.send_message(
            call.message.chat.id,
            prompt,
            parse_mode="Markdown",
            reply_markup=catalog_edit_product_images_keyboard(
                content_cfg, 
                article_number, 
                len(session["edit_products"][article_number]["image_message_ids"])
            )
        )
        session["edit_products"][article_number]["edit_images_message_id"] = sent.message_id
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_image_"))
    @err_handler
    def edit_image(call):
        logger.debug("edit_image CALL")
        
        user_id = call.from_user.id
        call_data = call.data.split('_')
        article_number = int(call_data[2])
        image_idx = int(call_data[3])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        prompt = content_cfg.catalog.admin.edit.images.current.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_image,
            article_number,
            image_idx
        )
        
    def process_image(message, article_number: int, image_idx: int):
        logger.debug("process_image CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        image_file_id = None
        if message.photo:
            image_file_id = message.photo[-1].file_id
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.images.current.incorrect_file_format.message)
            return
        
        image_number = image_idx + 1
        image_dir = Path(db.get_product_image_dir(article_number))
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"img{image_number}.jpg"
        
        if image_path.exists():
            image_bytes = download_image_bytes(cfg.token, image_file_id)
            image_path.write_bytes(image_bytes)
        else:
            bot.send_message(
                message.chat.id,
                content_cfg.catalog.admin.edit.images.current.failed_to_load.message
            )
            return
        
        new_media = types.InputMediaPhoto(media=image_bytes)
        
        bot.edit_message_media(
            new_media,
            message.chat.id,
            session["edit_products"][article_number]["image_message_ids"][image_idx]
        )
        
        bot.send_message(
            message.chat.id,
            content_cfg.get_catalog_admin_edit_images_current_success_message(image_number),
            parse_mode="Markdown"
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_image_"))
    @err_handler
    def delete_image(call):
        logger.debug("delete_image CALL")
        
        user_id = call.from_user.id
        call_data = call.data.split('_')
        article_number = int(call_data[2])
        image_idx = int(call_data[3])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        image_number = image_idx + 1
        
        image_dir = Path(db.get_product_image_dir(article_number))
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"img{image_number}.jpg"
        
        if os.path.exists(image_path):
            image_path.unlink()
        else:
            bot.send_message(
                call.message.chat.id,
                content_cfg.catalog.admin.edit.images.current.delete.error.message
            )
            return
        
        image_message_ids = session["edit_products"][article_number]["image_message_ids"]
        image_quantity = len(image_message_ids)
        
        for i in range(image_number, image_quantity):
            old_name = image_dir / f"img{i + 1}.jpg"
            new_name = image_dir / f"img{i}.jpg"
            if old_name.exists():
                old_name.rename(new_name)
        
        remaining_count = image_quantity - 1
        new_image_message_ids = image_message_ids[:remaining_count]
        
        for idx in range(image_idx, remaining_count):
            current_file = image_dir / f"img{idx+1}.jpg"
            with open(current_file, 'rb') as f:
                image_bytes = f.read()
                
            new_media = types.InputMediaPhoto(media=image_bytes)
            bot.edit_message_media(
                new_media,
                call.message.chat.id,
                new_image_message_ids[idx]
            )
        
        last_message_id = image_message_ids[-1]
        bot.delete_message(call.message.chat.id, last_message_id)
        
        session["edit_products"][article_number]["image_message_ids"] = new_image_message_ids
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            session["edit_products"][article_number]["edit_images_message_id"],
            reply_markup=catalog_edit_product_images_keyboard(
                content_cfg, 
                article_number, 
                len(session["edit_products"][article_number]["image_message_ids"])
            )
        )
        
        bot.send_message(
            call.message.chat.id,
            content_cfg.catalog.admin.edit.images.current.delete.success.message
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_image_"))
    @err_handler
    def add_image(call):
        logger.debug("add_image CALL")

        user_id = call.from_user.id
        article_number = int(call.data.split('_')[2])
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        current_image_quantity = len(session["edit_products"][article_number]["image_message_ids"])
        if current_image_quantity + 1 > 10:
            bot.send_message(call.message.chat.id, content_cfg.catalog.admin.edit.images.add.exceed_limit.message)
            return
        
        prompt = content_cfg.catalog.admin.edit.images.add.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_added_image,
            article_number
        )
        
    def process_added_image(message: types.Message, article_number: int):
        logger.debug("process_added_image CALL")
        
        user_id = message.from_user.id
        
        session = get_catalog_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.catalog.session_not_found.message)
            return
        
        image_file_id = None
        if message.photo:
            image_file_id = message.photo[-1].file_id
        else:
            bot.send_message(message.chat.id, content_cfg.catalog.admin.edit.images.add.incorrect_file_format.message)
            return
        
        image_dir = Path(db.get_product_image_dir(article_number))
        image_dir.mkdir(parents=True, exist_ok=True)
        
        current_image_quantity = len(session["edit_products"][article_number]["image_message_ids"])
        
        image_number = current_image_quantity + 1
        
        image_path = image_dir / f"img{image_number}.jpg"
        
        image_bytes = download_image_bytes(cfg.token, image_file_id)
        image_path.write_bytes(image_bytes)
        
        bot.send_message(
            message.chat.id,
            content_cfg.catalog.admin.edit.images.add.success.message
        )
        
        prepare_edit_product(message.chat.id, user_id, article_number)

        prompt = content_cfg.catalog.admin.edit.images.text
        sent = bot.send_message(
            message.chat.id,
            prompt,
            parse_mode="Markdown",
            reply_markup=catalog_edit_product_images_keyboard(
                content_cfg, 
                article_number, 
                len(session["edit_products"][article_number]["image_message_ids"])
            )
        )
        session["edit_products"][article_number]["edit_images_message_id"] = sent.message_id
        
