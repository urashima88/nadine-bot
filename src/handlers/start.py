from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
import src.keyboards as keyboards
from src.utils.content import get_production_time_days_ru_format


def register_start_handler(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
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
        