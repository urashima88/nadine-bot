from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import common_main_menu_keyboard


def register_common_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    
    @bot.message_handler(commands=['start'])
    def start(message):
        logger.debug("start CALL")
        
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name
        db.register_user(user_id, username, full_name)
        
        welcome_text = content_cfg.get_common_welcome_message(full_name)
        
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=common_main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.contacts.message)
    def send_admin_contacts(message):
        logger.debug("send_admin_contacts CALL")
        
        contacts = db.get_admin_contacts()
        contacts_text = content_cfg.get_common_admin_contacts_text(contacts["tg_username"], contacts["phone"])
        bot.send_message(
            message.chat.id,
            contacts_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.about.message)
    def send_about_information(message):
        logger.debug("send_about_information CALL")
        
        about_text = content_cfg.common.admin.about.text
        
        bot.send_message(
            message.chat.id,
            about_text,
            parse_mode="Markdown"
        )