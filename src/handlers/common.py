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

def register_common_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.message_handler(commands=['start'])
    @err_handler
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
        
    def show_profile(chat_id: int, user_id: int, message_id: int = None):
        logger.debug("show_profile CALL")
        
        full_name, phone, delivery_company, delivery_point_address = db.get_user_contact_info(user_id)
        profile_text = content_cfg.get_common_user_profile_text(full_name, phone, delivery_company, delivery_point_address)    
        
        if message_id:
            bot.send_message(
                chat_id, 
                profile_text, 
                parse_mode="Markdown", 
                reply_markup=common_user_profile_edit_keyboard(content_cfg)
            )
        else:
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
    
    @bot.callback_query_handler(func=lambda call: call.data in ("edit_full_name", "edit_phone", "edit_delivery_company", "edit_delivery_point_address"))
    @err_handler
    def ask_for_new_value(call):
        logger.debug("ask_for_new_value CALL")
        
        bot.answer_callback_query(call.id)
        call_data = call.data
        if call_data == "edit_full_name":
            prompt = content_cfg.common.user.profile.edit.full_name.text
        elif call_data == "edit_phone":
            prompt = content_cfg.common.user.profile.edit.phone.text
        elif call_data == "edit_delivery_company":
            prompt = content_cfg.common.user.profile.edit.delivery_company.text
        else:
            prompt = content_cfg.common.user.profile.edit.delivery_point_address.text
        msg = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            msg,
            save_profile_field,
            call.from_user.id,
            call_data,
            call.message.message_id
        )
            
    def save_profile_field(message, tg_user_id: int, call_data: str, profile_message_id: int):
        logger.debug("save_profile_field CALL")
        
        new_value = message.text.strip()
        if not new_value:
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.empty_value.message)
            return
        
        if call_data == "edit_phone" and not re.match(r"^\+?[0-9\s\-\(\)]{10,20}$", new_value):
            bot.send_message(
                message.chat.id,
                content_cfg.common.user.profile.edit.wrong_phone_format.message
            )
            return
            
        if call_data == "edit_full_name":
            success = db.update_user_full_name(tg_user_id, new_value)
            success_message = content_cfg.common.user.profile.edit.full_name.update.message
        elif call_data == "edit_phone":
            success = db.update_user_phone(tg_user_id, new_value)
            success_message = content_cfg.common.user.profile.edit.phone.update.message
        elif call_data == "edit_delivery_company":
            success = db.update_delivery_company(tg_user_id, new_value)
            success_message = content_cfg.common.user.profile.edit.delivery_company.update.message
        else:
            success = db.update_delivery_point_address(tg_user_id, new_value)
            success_message = content_cfg.common.user.profile.edit.delivery_point_address.update.message
            
        if success:
            bot.send_message(message.chat.id, success_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            show_profile(message.chat.id, tg_user_id, profile_message_id)
        else:
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.update_error.message)
        