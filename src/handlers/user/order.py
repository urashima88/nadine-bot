from logging import Logger

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.utils.wrappers import error_handler
from src.states.order_session import (
    set_order_session,
    get_order_session
)
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
        
    def save_user_profile_field(message, tg_user_id: int, call_data: str):
        logger.debug("save_user_profile_field CALL (order)")
        
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
        else:
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.update_error.message)
            
    def check_user_profile_fields(call):
        logger.debug("check_user_profile_fields CALL")
        
        user_id = call.from_user.id

        full_name, phone, delivery_company, delivery_point_address = db.get_user_contact_info(user_id)
        if not full_name:
            prompt = content_cfg.common.user.profile.edit.full_name.text
            message = bot.send_message(call.message.chat.id, prompt)
            bot.register_next_step_handler(
                message,
                save_user_profile_field,
                call.from_user.id,
                call.data
            )
        if not phone:
            prompt = content_cfg.common.user.profile.edit.phone.text
            message = bot.send_message(call.message.chat.id, prompt)
            bot.register_next_step_handler(
                message,
                save_user_profile_field,
                call.from_user.id,
                call.data
            )

        if not delivery_company:
            prompt = content_cfg.common.user.profile.edit.delivery_company.text
        else:
            ...
        
        if not delivery_point_address:
            prompt = content_cfg.common.user.profile.edit.delivery_point_address.text
        else:
            ...