from logging import Logger

from telebot import TeleBot

from src.storage import Storage, AddToCartResult
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    cart_keyboard,
    cart_control_edit_mode_keyboard,
    cart_edit_product_keyboard,
    common_main_menu_keyboard
)
from src.states.cart_session import (
    get_cart_session, 
    set_cart_session, 
    edit_cart_session,
    add_control_edit_message_id,
    delete_cart_session
)

def register_cart_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart.message)
    def show_cart(message): 
        logger.debug("show_cart CALL")
               
        user_id = message.from_user.id
        cart_products = db.get_cart_products(user_id)
        
        if not cart_products:
            bot.send_message(message.chat.id, content_cfg.cart.is_empty.message)
            return
        
        total = 0
        cart_text = content_cfg.cart.user.header_text
        
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
        
        sent = bot.send_message(
            message.chat.id,
            cart_text,
            reply_markup=cart_keyboard(content_cfg),
            parse_mode="Markdown"
        )
        
        set_cart_session(user_id, cart_text_message_id=message.id, cart_message_id=sent.message_id)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
    def add_to_cart(call):
        logger.debug("add_to_cart CALL")
        
        tg_user_id = call.from_user.id
        article_number = int(call.data.split('_')[1])
        
        result, new_quantity = db.add_to_cart(tg_user_id, article_number)
        if result == AddToCartResult.SUCCESS:
            message = content_cfg.get_cart_product_added_message(new_quantity)
            show_alert = False
        elif result == AddToCartResult.LIMIT_EXCEEDED:
            message = content_cfg.product.prod_limit_exceeded.message
            show_alert = True
        elif result == AddToCartResult.PRODUCT_NOT_FOUND:
            message = content_cfg.product.not_found.message
            show_alert = False
        else:
            message = content_cfg.cart.add_error_user_not_found.message
            show_alert = False
        bot.answer_callback_query(call.id, message, show_alert=show_alert)
        
    def delete_message(chat_id: int, message_id: int):
        logger.debug("delete_message CALL")
        
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            logger.warning(f"Failed to delete message: {e}")
        
    def delete_all_edit_messages(chat_id: int, user_id: int):
        logger.debug("delete_all_edit_messages CALL")
        
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.cart.session_not_found.message)
            return 
        
        for message_id in session["article_number_to_message_id_map"].values():
            delete_message(chat_id, message_id)
                
        for message_id in session["cart_control_edit_message_ids"]:
            delete_message(chat_id, message_id)
        
    def delete_all_messages(chat_id: int, user_id: int):
        logger.debug("delete_all_messages CALL")
        
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.cart.session_not_found.message)
            return 
        
        delete_message(chat_id, session["cart_text_message_id"])
        delete_message(chat_id, session["cart_message_id"])
        delete_all_edit_messages(chat_id, user_id)
        
    @bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
    def clear_cart(call):
        logger.debug("clear_cart CALL")
        
        tg_user_id = call.from_user.id
        success = db.clear_cart(tg_user_id)
        if success:
            session = get_cart_session(tg_user_id)
            if not session:
                bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
                return
            bot.answer_callback_query(call.id, content_cfg.cart.completely_cleared.message, show_alert=False)
            delete_all_messages(call.message.chat.id, tg_user_id)
            delete_cart_session(tg_user_id)
        else:
            bot.answer_callback_query(call.id, content_cfg.cart.is_empty_or_failed_to_clear.message, show_alert=True)
            
    @bot.callback_query_handler(func=lambda call: call.data == "edit_cart")
    def start_edit_cart(call):
        logger.debug("start_edit_cart CALL")
        
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return 
        
        bot.answer_callback_query(call.id)
        
        cart_products = db.get_cart_products(user_id)
        if not cart_products:
            bot.send_message(call.message.chat.id, content_cfg.cart.is_empty.message)
            return
        
        article_numbers = []
        article_number_to_product_map = {}
        for product in cart_products:
            article_number = product["article_number"]
            article_numbers.append(article_number)
            article_number_to_product_map[article_number] = product
        success = edit_cart_session(user_id, article_numbers, article_number_to_product_map)
        if not success:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        sent = bot.send_message(
            call.message.chat.id,
            content_cfg.cart.edit.text,
            reply_markup=cart_control_edit_mode_keyboard(content_cfg)
        )
        
        success = add_control_edit_message_id(user_id, sent.message_id)
        if not success:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        send_next_product(call.message, user_id)
        
    def send_next_product(message, user_id: int):
        logger.debug("send_next_product CALL")
        
        chat_id = message.chat.id
        
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.cart.session_not_found.message)
            return
        
        article_numbers = session["article_numbers"]
        index = session["index"]
        if index >= len(article_numbers):
            bot.send_message(chat_id, content_cfg.cart.control_edit.no_other_products.message)
            return
        
        article_number = article_numbers[index]
        product = session["article_number_to_product_map"].get(article_number)
        if product:
            name = product["name"]
            price = product["price"]
            quantity = product["quantity"]
            product_total = price * quantity
            text = content_cfg.get_cart_product_text(name, article_number, price, quantity, product_total)
            sent = bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=cart_edit_product_keyboard(content_cfg, article_number, quantity)
            )
            session["article_number_to_message_id_map"][article_number] = sent.message_id
        else:
            bot.send_message(chat_id, content_cfg.cart.edit.product.not_found.message)
        
        session["index"] += 1
        if session["index"] >= session["total"]:
            send_no_other_products_message(message, user_id)
        
    def edit_product(chat_id: int, user_id: int, article_number: int):
        logger.debug("edit_product CALL")
        
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.cart.session_not_found.message)
            return 
        product = session["article_number_to_product_map"].get(article_number)
        if product:
            name = product["name"]
            price = product["price"]
            quantity = product["quantity"]
            product_total = price * quantity
            text = content_cfg.get_cart_product_text(name, article_number, price, quantity, product_total)
            if session["article_number_to_message_id_map"].get(article_number):
                try:
                    bot.edit_message_text(
                        text,
                        chat_id,
                        session["article_number_to_message_id_map"][article_number],
                        parse_mode="Markdown",
                        reply_markup=cart_edit_product_keyboard(content_cfg, article_number, quantity)
                    )
                    return
                except Exception as e:
                    logger.warning(f"Failed to edit the cart message: {e}")
                    bot.send_message(chat_id, content_cfg.cart.edit.product.error.message)
        else:
            bot.send_message(chat_id, content_cfg.cart.edit.product.not_found.message)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('increase_product_'))
    def increase_product(call):
        logger.debug("increase_product CALL")
        
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        product = session["article_number_to_product_map"].get(article_number)
        if product:
            new_quantity = product["quantity"] + 1
            db.update_cart_quantity(user_id, article_number, new_quantity)
            product["quantity"] = new_quantity
            edit_product(call.message.chat.id, user_id, article_number)
            bot.answer_callback_query(call.id)
        else:
            bot.send_message(call.message.chat.id, content_cfg.cart.edit.product.not_found.message)
        
    def clear_product_info(chat_id: int, session, user_id: int, article_number: int):
        logger.debug("clear_product_info CALL")
        
        db.remove_cart_product(user_id, article_number)
        if session["article_number_to_product_map"].get(article_number):
            del session["article_number_to_product_map"][article_number]
            session["article_numbers"].remove(article_number)
            
        session["total"] = len(session["article_numbers"])
        if session["index"] >= session["total"]:
            session["index"] = max(0, session["total"] - 1)
        
        if article_number in session["article_number_to_message_id_map"]:
            delete_message(chat_id, session["article_number_to_message_id_map"][article_number])
            del session["article_number_to_message_id_map"][article_number]
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('decrease_product_'))  
    def decrease_product(call):
        logger.debug("decrease_product CALL")
        
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        product = session["article_number_to_product_map"].get(article_number)
        if product:
            if product["quantity"] > 1:
                new_quantity = product['quantity'] - 1
                db.update_cart_quantity(user_id, article_number, new_quantity)
                product["quantity"] = new_quantity
            else:
                clear_product_info(call.message.chat.id, session, user_id, article_number)
                if not session["article_number_to_product_map"]:
                    bot.send_message(call.message.chat.id, content_cfg.cart.is_empty.message, show_alert=False)
                    return

            edit_product(call.message.chat.id, user_id, article_number)
            bot.answer_callback_query(call.id)
        else:
            bot.send_message(call.message.chat.id, content_cfg.cart.edit.product.not_found.message)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_product_'))
    def delete_product(call):
        logger.debug("delete_product CALL")
        
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.cart.session_not_found.message)
            return
        if session["total"] > 0:
            clear_product_info(call.message.chat.id, session, user_id, article_number) 
            if not session["article_number_to_product_map"]:
                bot.send_message(call.message.chat.id, content_cfg.cart.is_empty.message)
                return
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data == "ignore")
    def ignore_callback(call):
        logger.debug("ignore_callback CALL")
        
        bot.answer_callback_query(call.id)
        
    def send_no_other_products_message(message, user_id: int):
        logger.debug("send_no_other_products_message CALL")
        
        sent = bot.send_message(message.chat.id, content_cfg.cart.control_edit.no_other_products.message)
        success = add_control_edit_message_id(user_id, sent.message_id)
        if not success:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
        
    def send_products(message, count):
        logger.debug("send_products CALL")
        
        user_id = message.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        total = session["total"]
        index = session["index"]
        
        if index >= total:
            send_no_other_products_message(message, user_id)
            return
        
        to_send = min(count, total-index)        
        for _ in range(to_send):
            send_next_product(message, user_id)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart.control_edit.next.message)
    def send_next_one(message):
        logger.debug("send_next_one CALL")
        
        user_id = message.from_user.id
        success = add_control_edit_message_id(user_id, message.id)
        if not success:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        send_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart.control_edit.next5.message)
    def send_next_five(message):
        logger.debug("send_next_five CALL")
        
        user_id = message.from_user.id
        success = add_control_edit_message_id(user_id, message.id)
        if not success:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        send_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart.control_edit.stop.message)
    def stop_edit(message):
        logger.debug("stop_edit CALL")
        
        user_id = message.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        success = add_control_edit_message_id(user_id, message.id)
        if not success:
            bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
            return
        
        delete_all_messages(message.chat.id, user_id)
        delete_cart_session(user_id)
        show_cart(message)
        bot.send_message(
            message.chat.id, 
            content_cfg.cart.main_menu.message,
            reply_markup=common_main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart.control_edit.go_back_to_main_menu.message)
    def go_back_to_main_menu(message):
        logger.debug("go_back_to_main_menu CALL")
        
        user_id = message.from_user.id
        session = get_cart_session(user_id)
        if session:
            success = add_control_edit_message_id(user_id, message.id)
            if not success:
                bot.send_message(message.chat.id, content_cfg.cart.session_not_found.message)
                return
            
            delete_all_messages(message.chat.id, user_id)
            delete_cart_session(user_id)
        bot.send_message(
            message.chat.id, 
            content_cfg.cart.main_menu.message,
            reply_markup=common_main_menu_keyboard(content_cfg)
        )