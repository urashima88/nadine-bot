from logging import Logger

from telebot import TeleBot

from src.storage import Storage, AddToCartResult
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    cart_keyboard,
    edit_cart_control_keyboard,
    edit_product_keyboard,
    main_menu_keyboard
)
from src.states.cart_session import (
    get_cart_session, 
    set_cart_session, 
    delete_cart_session
)

def register_cart_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_message)
    def show_cart(message):        
        user_id = message.from_user.id
        cart_items = db.get_cart_items(user_id)
        
        if not cart_items:
            bot.send_message(message.chat.id, content_cfg.cart_is_empty_message)
            return
        
        total = 0
        cart_text = content_cfg.user_cart_text
        
        for item in cart_items:
            article_number = item["article_number"]
            name = item["name"]
            price = item["price"]
            quantity = item["quantity"]
            item_total = price * quantity
            total += item_total
            cart_text += content_cfg.get_cart_item_text(
                name, article_number, price, quantity, item_total
            )
            
        cart_text += content_cfg.get_cart_total_text(total)
        
        bot.send_message(
            message.chat.id,
            cart_text,
            reply_markup=cart_keyboard(content_cfg),
            parse_mode='Markdown'
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
    def add_to_cart(call):
        tg_user_id = call.from_user.id
        article_number = int(call.data.split('_')[1])
        
        result, new_quantity = db.add_to_cart(tg_user_id, article_number)
        if result == AddToCartResult.SUCCESS:
            message = content_cfg.get_product_addded_to_cart_message(new_quantity)
            show_alert = False
        elif result == AddToCartResult.LIMIT_EXCEEDED:
            message = content_cfg.prod_limit_exceeded_message
            show_alert = True
        elif result == AddToCartResult.PRODUCT_NOT_FOUND:
            message = content_cfg.product_not_found_message
            show_alert = False
        else:
            message = content_cfg.add_error_user_not_found_message
            show_alert = False
        bot.answer_callback_query(call.id, message, show_alert=show_alert)
        
    @bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
    def clear_cart(call):
        tg_user_id = call.from_user.id
        success = db.clear_cart(tg_user_id)
        if success:
            bot.answer_callback_query(call.id, content_cfg.completely_cleared_cart_message, show_alert=False)
        else:
            bot.answer_callback_query(call.id, content_cfg.cart_is_empty_or_failed_to_clear_message, show_alert=True)
            
    @bot.callback_query_handler(func=lambda call: call.data == "edit_cart")
    def start_edit_cart(call):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        cart_items = db.get_cart_items(user_id)
        if not cart_items:
            bot.send_message(call.message.chat.id, content_cfg.cart_is_empty_message)
            return
        article_numbers = []
        article_number_to_item = {}
        for item in cart_items:
            article_number = item["article_number"]
            article_numbers.append(article_number)
            article_number_to_item[article_number] = item
        set_cart_session(user_id, article_numbers, article_number_to_item)
        bot.send_message(
            call.message.chat.id,
            content_cfg.edit_cart_text,
            reply_markup=edit_cart_control_keyboard(content_cfg)
        )
        send_next_product(call.message.chat.id, user_id)
        
    def send_next_product(chat_id: int, user_id: int):
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.session_not_found_message)
            return
        article_numbers = session["article_numbers"]
        idx = session["index"]
        if idx >= len(article_numbers):
            show_final_cart(chat_id, user_id)
            return
        article_number = article_numbers[idx]
        item = session["article_number_to_item"].get(article_number)
        if item:
            name = item['name']
            price = item['price']
            quantity = item['quantity']
            item_total = price * quantity
            text = content_cfg.get_cart_item_text(name, article_number, price, quantity, item_total)
            sent = bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=edit_product_keyboard(content_cfg, article_number, quantity)
            )
            session["article_number_to_message_id"][article_number] = sent.message_id
        
    def edit_product(chat_id: int, user_id: int, article_number: int):
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.session_not_found_message)
            return 
        item = session["article_number_to_item"].get(article_number)
        name = item['name']
        price = item['price']
        quantity = item['quantity']
        item_total = price * quantity
        text = content_cfg.get_cart_item_text(name, article_number, price, quantity, item_total)
        if session["article_number_to_message_id"].get(article_number):
            try:
                bot.edit_message_text(
                    text,
                    chat_id,
                    session["article_number_to_message_id"][article_number],
                    parse_mode="Markdown",
                    reply_markup=edit_product_keyboard(content_cfg, article_number, quantity)
                )
                return
            except Exception as e:
                logger.warning(f"Failed to edit the cart message: {e}")
                session["message_ids"][article_number] = None
        
    def show_final_cart(chat_id: int, user_id: int):
        class FakeMessage:
            def __init__(self, chat_id, user_id):
                self.chat = type('obj', (object,), {'id': chat_id})
                self.from_user = type('obj', (object,), {'id': user_id})
        show_cart(FakeMessage(chat_id, user_id))
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_increase_'))
    def edit_increase(call):
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.session_not_found_message)
            return
        
        item = session["article_number_to_item"].get(article_number)
        new_quantity = item["quantity"] + 1
        db.update_cart_quantity(user_id, article_number, new_quantity)
        item["quantity"] = new_quantity
        edit_product(call.message.chat.id, user_id, article_number)
        bot.answer_callback_query(call.id)
        
    def clear_product_info(chat_id: int, session, user_id: int, article_number: int):
        db.remove_cart_item(user_id, article_number)
        del session["article_number_to_item"][article_number]
        session["article_numbers"].remove(article_number)
        session["total"] = len(session["article_numbers"])
        if session["index"] >= session["total"]:
            session["index"] = max(0, session["total"] - 1)
        try:
            bot.delete_message(chat_id, session["article_number_to_message_id"][article_number])
        except:
            pass
        del session["article_number_to_message_id"][article_number]
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_decrease_'))  
    def edit_decrease(call):
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.session_not_found_message)
            return
        
        item = session["article_number_to_item"].get(article_number)
        if item["quantity"] > 1:
            new_quantity = item['quantity'] - 1
            db.update_cart_quantity(user_id, article_number, new_quantity)
            item["quantity"] = new_quantity
        else:
            clear_product_info(call.message.chat.id, session, user_id, article_number)
            if not session["article_number_to_item"]:
                show_final_cart(call.message.chat.id, user_id)
                bot.send_message(call.message.chat.id, content_cfg.cart_is_empty_message, show_alert=False)
                return

        edit_product(call.message.chat.id, user_id, article_number)
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_delete_'))
    def edit_delete(call):
        article_number = int(call.data.split('_')[2])
        user_id = call.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.session_not_found_message)
            return
        clear_product_info(call.message.chat.id, session, user_id, article_number) 
        if not session["article_number_to_item"]:
            show_final_cart(call.message.chat.id, user_id)
            bot.send_message(call.message.chat.id, content_cfg.cart_is_empty_message)
            return
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data == "ignore")
    def ignore_callback(call):
        bot.answer_callback_query(call.id)
        
    def send_products(message, count):
        user_id = message.from_user.id
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.session_not_found_message)
            return
        new_index = session["index"] + count
        if new_index >= session["total"]:
            new_index = session["total"] - 1
        if new_index < 0:
            new_index = 0
        session["index"] = new_index
        send_next_product(message.chat.id, user_id)
        
    def delete_all_edit_product_messages(chat_id: int, user_id: int):
        session = get_cart_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.session_not_found_message)
            return 
        for message_id in session[user_id]["article_number_to_message_id"].values():
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                logger.warning(f"Failed to delete message: {e}")
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_control_next_message)
    def edit_next_one(message):
        send_products(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_control_next5_message)
    def edit_next_five(message):
        send_products(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_control_stop_message)
    def edit_stop(message):
        user_id = message.from_user.id
        delete_all_edit_product_messages(message.chat.id, user_id)
        delete_cart_session(user_id)
        show_cart(message)
        bot.send_message(
            message.chat.id, 
            content_cfg.main_menu_message,
            reply_markup=main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.cart_control_back_to_main_menu_message)
    def handle_back_to_main_menu(message):
        user_id = message.from_user.id
        delete_all_edit_product_messages(message.chat.id, user_id)
        delete_cart_session(user_id)
        bot.send_message(
            message.chat.id, 
            content_cfg.main_menu_message,
            reply_markup=main_menu_keyboard(content_cfg)
        )