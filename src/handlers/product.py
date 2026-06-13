from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import product_keyboard
from src.utils.wrappers import error_handler
from src.handlers.shared import prepare_product_info

def register_product_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
    @err_handler
    def show_product_details(call):
        logger.debug("show_product_details CALL")
        
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[1])
        text = prepare_product_info(call, bot, db, content_cfg, logger, article_number)

        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )
        
        
        
