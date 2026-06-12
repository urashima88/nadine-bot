from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import product_keyboard, edit_product_keyboard
from src.utils.wrappers import error_handler
from src.handlers.shared import process_product

def register_product_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
    @err_handler
    def show_product_details(call):
        logger.debug("show_product_details CALL")
        
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[1])
        text = prepare_product_info(call, article_number)

        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )
        
    def prepare_product_info(call, article_number: int) -> str:
        product = db.get_product_by_article_number(article_number)
        
        if not product:
            bot.send_message(call.message.chat.id, content_cfg.product.not_found.message)
            return
        
        text = process_product(
            product,
            bot,
            call.message.chat.id,
            content_cfg,
            logger
        )
        return text
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_product_'))
    @err_handler
    def edit_product(call):
        logger.debug("edit_product CALL")
        
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[2])
        text = prepare_product_info(call, article_number)
        
        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=edit_product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )
        
        