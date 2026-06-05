from logging import Logger

from telebot import TeleBot

def delete_message(bot: TeleBot, chat_id: int, message_id: int, logger: Logger):
    logger.debug("delete_message CALL")
    
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.warning(f"Failed to delete message: {e}")