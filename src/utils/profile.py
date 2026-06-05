import re
from typing import Tuple

from telebot import TeleBot

from src.storage import Storage
from src.config.content_config import ContentConfig

def check_and_update_user_profile_field(
    message, 
    bot: TeleBot, 
    db: Storage, 
    tg_user_id: int, 
    call_data: str,
    content_cfg: ContentConfig
) -> Tuple[bool, str]:
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
    return success, success_message