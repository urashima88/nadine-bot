from logging import Logger
import json

from telebot import TeleBot, types

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.utils.wrappers import error_handler
from src.keyboards import settings_admin_keyboard, admin_main_menu_keyboard

def register_settings_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.settings.admin.message)
    @err_handler
    def show_settings(message: types.Message):
        logger.debug("show_settings CALL")
        
        bot.send_message(
            message.chat.id,
            content_cfg.settings.admin.text,
            parse_mode="Markdown",
            reply_markup=settings_admin_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "change_content_config")
    @err_handler
    def change_content_config(call):    
        logger.debug("change_content_config CALL")
        
        bot.answer_callback_query(call.id)
        
        prompt = content_cfg.settings.admin.content.config.text
        message = bot.send_message(call.message.chat.id, prompt, parse_mode="Markdown")
        bot.register_next_step_handler(
            message,
            process_content_config
        )
        
    def process_content_config(message: types.Message):
        logger.debug("process_content_config CALL")
        
        if not message.document or message.document.mime_type != "application/json":
            bot.send_message(
                message.chat.id, 
                content_cfg.settings.admin.content.config.incorrect_file_format.message,
                parse_mode="Markdown"
            )
            return
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        try:
            new_config = json.loads(downloaded_file.decode('utf-8'))
        except json.JSONDecodeError as e:
            bot.send_message(
                message.chat.id, 
                content_cfg.settings.admin.content.config.parsing_error.message,
                parse_mode="Markdown"
            )
            
        config_path = content_cfg.config_path
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save content config: {e}")
            bot.send_message(
                message.chat.id, 
                content_cfg.settings.admin.content.config.failed_to_save.message,
                parse_mode="Markdown"
            )
            
        content_cfg.reload()
        bot.send_message(
            message.chat.id, 
            content_cfg.settings.admin.content.config.success.message,
            parse_mode="Markdown",
            reply_markup=admin_main_menu_keyboard(content_cfg)
        )
            