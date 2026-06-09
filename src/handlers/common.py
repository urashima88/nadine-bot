from logging import Logger
import re

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    main_menu_keyboard,
    common_user_profile_edit_keyboard
)
from src.utils.wrappers import error_handler
from src.utils.clean import delete_message
from src.handlers.shared import check_and_update_user_profile_field

def register_common_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.message_handler(commands=['start'])
    @err_handler
    def start(message):
        logger.debug("start CALL")
        
        tg_user_id = message.from_user.id
        tg_username = message.from_user.username
        tg_full_name = message.from_user.full_name
        db.register_user(tg_user_id, tg_username, tg_full_name)
        
        welcome_text = content_cfg.get_common_welcome_message(tg_full_name)
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.contacts.message)
    @err_handler
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
    @err_handler
    def send_about_information(message):
        logger.debug("send_about_information CALL")
        
        about_text = content_cfg.common.admin.about.text
        
        bot.send_message(
            message.chat.id,
            about_text,
            parse_mode="Markdown"
        )
        
    def show_profile(chat_id: int, user_id: int):
        logger.debug("show_profile CALL")
        
        full_name, phone, timezone, delivery_company, delivery_point_address = db.get_user_profile_data(user_id)
        profile_text = content_cfg.get_common_user_profile_text(full_name, phone, timezone, delivery_company, delivery_point_address)    
        
        bot.send_message(
            chat_id, 
            profile_text, 
            parse_mode="Markdown", 
            reply_markup=common_user_profile_edit_keyboard(content_cfg)
        )

    @bot.message_handler(func=lambda message: message.text == content_cfg.common.user.personal_data.message)
    @err_handler
    def handle_profile(message):
        logger.debug("handle_profile CALL")
        
        show_profile(message.chat.id, message.from_user.id)
    
    @bot.callback_query_handler(func=lambda call: call.data in ("edit_full_name", "edit_phone", "edit_timezone", "edit_delivery_company", "edit_delivery_point_address"))
    @err_handler
    def ask_for_new_value(call):
        logger.debug("ask_for_new_value CALL")
        
        bot.answer_callback_query(call.id)
        call_data = call.data
        if call_data == "edit_full_name":
            prompt = content_cfg.common.user.profile.edit.full_name.text
        elif call_data == "edit_phone":
            prompt = content_cfg.common.user.profile.edit.phone.text
        elif call_data == "edit_timezone":
            prompt = content_cfg.common.user.profile.edit.timezone.text
        elif call_data == "edit_delivery_company":
            prompt = content_cfg.common.user.profile.edit.delivery_company.text
        else:
            prompt = content_cfg.common.user.profile.edit.delivery_point_address.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_user_profile_field,
            call.from_user.id,
            call_data
        )
            
    def save_user_profile_field(message, tg_user_id: int, call_data: str):
        logger.debug("save_user_profile_field CALL (common)")
        
        success, success_message = check_and_update_user_profile_field(
            message, 
            bot, 
            db, 
            tg_user_id, 
            call_data,
            content_cfg
        )
            
        if success:
            bot.send_message(message.chat.id, success_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            show_profile(message.chat.id, tg_user_id)
        else:
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.update_error.message)
        