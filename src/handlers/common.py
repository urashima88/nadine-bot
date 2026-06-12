from logging import Logger
import re

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    main_menu_keyboard,
    common_user_profile_edit_keyboard,
    admin_main_menu_keyboard,
    common_admin_control_show_user_data_mode_keyboard,
    common_admin_profile_edit_keyboard
)
from src.utils.wrappers import error_handler
from src.utils.clean import delete_message
from src.handlers.shared import check_and_update_user_profile_field
from src.states.cart_session import get_cart_session, delete_cart_session
from src.states.catalog_session import get_catalog_session, delete_catalog_session
from src.states.order_show_session import order_show_get_session, order_show_delete_session
from src.states.admin_cancel_order_session import admin_cancel_order_get_session, admin_cancel_order_delete_session
from src.states.admin_user_data_show_session import (
    admin_user_data_show_set_session, 
    admin_user_data_show_get_session,
    admin_user_data_show_delete_session
)
from src.utils.content import format_local_datetime

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
        
        is_admin = db.is_admin(tg_user_id)
        if is_admin:
            keyboard = admin_main_menu_keyboard(content_cfg)
        else:
            keyboard = main_menu_keyboard(content_cfg)
        
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=keyboard
        )
        
    @bot.message_handler(commands=['main'])
    @err_handler
    def main(message):
        logger.debug("main CALL")
        
        user_id = message.from_user.id
        
        catalog_session = get_catalog_session(user_id)
        if catalog_session:
            delete_catalog_session(user_id)
        
        cart_session = get_cart_session(user_id)
        if cart_session:
            delete_cart_session(user_id)
            
        order_show_session = order_show_get_session(user_id)
        if order_show_session:
            order_show_delete_session(user_id)
        
        bot.send_message(
            message.chat.id, 
            content_cfg.common.main_menu.user.message, 
            reply_markup=main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(commands=['adminmain'])
    @err_handler
    def admin_main(message):
        logger.debug("admin-main CALL")
        
        user_id = message.from_user.id
        
        admin_cancel_order_session = admin_cancel_order_get_session(user_id)
        if admin_cancel_order_session:
            admin_cancel_order_delete_session(user_id)
            
        order_show_session = order_show_get_session(user_id)
        if order_show_session:
            order_show_delete_session(user_id)
            
        admin_user_data_show_session = admin_user_data_show_get_session(user_id)
        if admin_user_data_show_session:
            admin_user_data_show_delete_session(user_id)

        bot.send_message(
            message.chat.id, 
            content_cfg.common.main_menu.admin.message, 
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.contacts.message)
    @err_handler
    def send_admin_contacts(message):
        logger.debug("send_admin_contacts CALL")
        
        contacts = db.get_admin_contacts()
        contacts_text = content_cfg.get_common_admin_contacts_text(
            contacts["tg_username"], 
            contacts["tg_full_name"],
            contacts["full_name"],
            contacts["phone"],
            contacts["timezone"],
        )
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

    @bot.message_handler(func=lambda message: message.text == content_cfg.common.user.personal_data.message)
    @err_handler
    def handle_profile(message):
        logger.debug("handle_profile CALL")
        
        show_profile(message.chat.id, message.from_user.id)
        
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
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.personal_data.message)
    @err_handler
    def handle_admin_profile(message):
        logger.debug("handle_admin_profile CALL")
        
        admin_show_profile(message.chat.id, message.from_user.id)
        
    def admin_show_profile(chat_id: int, user_id: int):
        logger.debug("admin_show_profile CALL")
        
        full_name, phone, timezone, _, _ = db.get_user_profile_data(user_id)
        profile_text = content_cfg.get_common_admin_profile_text(full_name, phone, timezone)    
        
        bot.send_message(
            chat_id, 
            profile_text, 
            parse_mode="Markdown", 
            reply_markup=common_admin_profile_edit_keyboard(content_cfg)
        )
    
    @bot.callback_query_handler(func=lambda call: call.data in ("edit_full_name", "edit_phone", "edit_timezone", "edit_delivery_company", "edit_delivery_point_address"))
    @err_handler
    def ask_for_new_value(call):
        logger.debug("ask_for_new_value CALL")
        
        bot.answer_callback_query(call.id)
        call_data = call.data
        if call_data == "edit_full_name":
            prompt = content_cfg.common.profile.edit.full_name.text
        elif call_data == "edit_phone":
            prompt = content_cfg.common.profile.edit.phone.text
        elif call_data == "edit_timezone":
            prompt = content_cfg.common.profile.edit.timezone.text
        elif call_data == "edit_delivery_company":
            prompt = content_cfg.common.profile.edit.delivery_company.text
        else:
            prompt = content_cfg.common.profile.edit.delivery_point_address.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            save_user_profile_field,
            call.from_user.id,
            call_data
        )
            
    def save_user_profile_field(message, tg_user_id: int, call_data: str):
        logger.debug("save_user_profile_field CALL (common)")
        
        success, result_message = check_and_update_user_profile_field(
            message, 
            db, 
            tg_user_id, 
            call_data,
            content_cfg,
            logger
        )
            
        if success:
            bot.send_message(message.chat.id, result_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            if db.is_admin(tg_user_id):
                admin_show_profile(message.chat.id, tg_user_id)
            else:
                show_profile(message.chat.id, tg_user_id)
        else:
            bot.send_message(message.chat.id, result_message)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.user_data.all.message)
    @err_handler
    def admin_show_user_data(message):
        logger.debug("admin_show_user_data CALL")

        admin_id = message.from_user.id
        users = db.get_all_users()
        
        if not users:
            bot.send_message(message.chat.id, content_cfg.common.admin.user_data.all.is_empty.message)
            return
        
        admin_user_data_show_set_session(admin_id, users)
        
        user_data_all_control_show_text = content_cfg.get_common_admin_user_data_all_control_show_text(len(users))
        
        bot.send_message(
            message.chat.id,
            user_data_all_control_show_text,
            parse_mode="Markdown",
            reply_markup=common_admin_control_show_user_data_mode_keyboard(content_cfg)
        )
        
        admin_send_next_users(message.chat.id, admin_id, count=1)
        
    def admin_send_all_users_displayed_message(chat_id: int, user_id: int):
        logger.debug("admin_send_all_users_displayed_message CALL")
        
        bot.send_message(chat_id, content_cfg.common.admin.user_data.all.displayed.message)
        bot.send_message(
            chat_id, 
            content_cfg.common.admin.user_data.main_menu.message, 
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )
        admin_user_data_show_delete_session(user_id)
        
    def admin_send_next_users(chat_id: int, user_id: int, count: int):
        logger.debug("admin_send_next_users CALL")
        
        session = admin_user_data_show_get_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.common.admin.user_data.all.control_show.session_not_found.message)
            return
        
        users = session["users"]
        sent = session["sent"]
        total = session["total"]
        
        if sent >= total:
            admin_send_all_users_displayed_message(chat_id, user_id)
            return
        
        to_send = min(count, total-sent)
        for i in range(to_send):
            idx = sent + i
            user = users[idx]
            
            user_text = content_cfg.get_common_admin_user_data_all_control_show_current_text(
                user["tg_username"],
                user["tg_full_name"],
                user["full_name"],
                user["phone"],
                user["timezone"],
                user["delivery_company"],
                user["delivery_point_address"],
                format_local_datetime(user["created_at"], user["timezone"])
            )
            
            bot.send_message(
                chat_id,
                text=user_text,
                parse_mode="Markdown"
            )
        
        session["sent"] = sent + to_send
        if session["sent"] >= total:
            admin_send_all_users_displayed_message(chat_id, user_id)
            
    def admin_send_users(message, count):
        logger.debug("admin_send_users CALL")
        
        admin_id = message.from_user.id
        session = admin_user_data_show_get_session(admin_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.common.admin.user_data.all.control_show.session_not_found.message)
            return
        
        admin_send_next_users(message.chat.id, admin_id, count)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.user_data.all.control_show.next.message)
    @err_handler
    def admin_send_next_one_user(message):
        logger.debug("admin_send_next_one_user CALL")
        
        admin_send_users(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.user_data.all.control_show.next5.message)
    @err_handler
    def admin_send_next_five_users(message):
        logger.debug("admin_send_next_five_users CALL")
        
        admin_send_users(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.common.admin.user_data.all.control_show.go_back_to_main_menu.message)
    @err_handler
    def admin_user_data_control_show_go_back_to_main_menu(message):
        logger.debug("admin_user_data_control_show_go_back_to_main_menu CALL")
        
        user_id = message.from_user.id
        admin_user_data_show_delete_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.common.admin.user_data.main_menu.message,
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )