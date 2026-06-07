import functools
from logging import Logger

import psycopg2
from telebot import TeleBot

from src.config.content_config import ContentConfig
from src.storage import Storage

def error_handler(bot: TeleBot, content_cfg: ContentConfig, logger: Logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(handler_args):
            try:
                return func(handler_args)
            except psycopg2.Error as e:
                logger.exception(f"Database error in {func.__name__}: {e}")
                _send_error_message(
                    bot, 
                    handler_args,
                    content_cfg.db.error.message, 
                    logger
                )
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                _send_error_message(
                    bot,
                    handler_args,
                    content_cfg.common.error.message,
                    logger
                )
        return wrapper
    return decorator
                
def _send_error_message(bot: TeleBot, handler_args, text: str, logger: Logger):
    if hasattr(handler_args, "message"):
        chat_id = handler_args.message.chat.id
        bot.send_message(chat_id, text)
    elif hasattr(handler_args, "chat"):
        chat_id = handler_args.chat.id
        bot.send_message(chat_id, text)
    else:
        logger.error(f"Unknown handler arguments type: {type(handler_args)}")
            
def is_admin(bot: TeleBot, db: Storage, is_for_admin: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(handler_args):
            if hasattr(handler_args, "from_user"):
                user_id = handler_args.from_user.id
            else:
                return func(handler_args)

            is_admin_flag = db.is_admin(user_id)

            if is_admin_flag == is_for_admin:
                return func(handler_args)
            else:
                if hasattr(handler_args, "id"):
                    bot.answer_callback_query(handler_args.id)
                return
        return wrapper
    return decorator