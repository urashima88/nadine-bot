from logging import Logger

from telebot import TeleBot

from src.storage import Storage, AddToCartResult
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import cart_keyboard

def register_cart_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
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
        