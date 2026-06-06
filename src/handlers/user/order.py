from logging import Logger
from typing import List, Tuple

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.utils.wrappers import error_handler
from src.states.order_session import (
    set_order_session,
    get_order_session,
)
from src.keyboards import order_user_profile_field_keyboard
from src.utils.profile import check_and_update_user_profile_field
from src.utils.clean import delete_message

def register_order_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data == "place_order")
    @err_handler
    def place_order(call):
        logger.debug("place_order CALL")
        
        bot.answer_callback_query(call.id)
        
        user_id = call.from_user.id
        
        if not db.can_user_create_order(user_id, max_orders_per_day=content_cfg.order.limit_per_day):
            bot.send_message(
                call.message.chat.id,
                content_cfg.order.exceed_limit.message,
            )
            return
        else:
            today_orders_count = db.get_user_today_orders_count(user_id)
            remaining = content_cfg.order.limit_per_day - today_orders_count
            bot.send_message(
                call.message.chat.id,
                content_cfg.get_order_start_message(remaining)
            )
        
        check_user_profile_fields(call)            
            
    def check_user_profile_fields(call):
        logger.debug("check_user_profile_fields CALL")
        
        user_id = call.from_user.id

        full_name, phone, delivery_company, delivery_point_address = db.get_user_contact_info(user_id)
        field_values = [full_name, phone, delivery_company, delivery_point_address]
        set_order_session(user_id, field_values, 0)
        chain_check_user_profile_field(call)

    def get_field_name_and_prompt(index: int) -> Tuple[str, str]:
        logger.debug("get_field_name_and_prompt CALL")

        if index == 0:
            return "full_name", content_cfg.common.user.profile.edit.full_name.text
        elif index == 1:
            return "phone", content_cfg.common.user.profile.edit.phone.text
        elif index == 2:
            return "delivery_company", content_cfg.common.user.profile.edit.delivery_company.text
        return "delivery_point_address", content_cfg.common.user.profile.edit.delivery_point_address.text
        
    def update_user_profile_field(message, call, index: int):
        logger.debug("update_user_profile_field CALL")
        
        name, _ = get_field_name_and_prompt(index)
        success, success_message = check_and_update_user_profile_field(
            message, 
            bot, 
            db, 
            call.from_user.id, 
            "edit_" + name,
            content_cfg
        )
            
        if success:
            bot.send_message(message.chat.id, success_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            if index < 3:
                session = get_order_session(call.from_user.id)
                if not session:
                    bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
                    return
                session["index"] += 1
                chain_check_user_profile_field(call)
        else:
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.update_error.message)
       
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_field_'))
    @err_handler
    def handle_edit_field_callback(call):
        logger.debug("handle_edit_field_callback CALL")
        
        session = get_order_session(call.from_user.id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        index = session["index"]
        
        choice = call.data.split("_")[2]
        if choice == "yes":
            _, prompt = get_field_name_and_prompt(index)
            message = bot.send_message(call.message.chat.id, prompt)
            bot.register_next_step_handler(
                message,
                update_user_profile_field,
                call,
                index
            )
        else:
            if index < 3:
                session["index"] += 1
                chain_check_user_profile_field(call)
            
    def get_delivery_field_question(index: int, field_value: str) -> str:
        logger.debug("get_delivery_field_question CALL")
        
        if index == 0:
            return content_cfg.get_common_user_profile_edit_delivery_company_question_message(field_value)
        return content_cfg.get_common_user_profile_edit_delivery_point_address_question_message(field_value)
        
    def chain_check_user_profile_field(call):
        logger.debug("chain_check_user_profile_field CALL")
        
        user_id = call.from_user.id
        session = get_order_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        field_values = session["field_values"]
        index = session["index"]
        
        field_value = field_values[index]
        if not field_value:
            _, prompt = get_field_name_and_prompt(index)
            message = bot.send_message(call.message.chat.id, prompt)
            bot.register_next_step_handler(
                message,
                update_user_profile_field,
                call,
                index
            )
        else:
            if index <= 1:
                session["index"] += 1
                chain_check_user_profile_field(call)
            if index == 2 or index == 3:
                bot.send_message(
                    call.message.chat.id,
                    get_delivery_field_question(index, field_value),
                    parse_mode="Markdown",
                    reply_markup=order_user_profile_field_keyboard(content_cfg)
                )

        
    
    