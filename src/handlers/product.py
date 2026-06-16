from logging import Logger
from typing import Dict, Any
from pathlib import Path
import os
import shutil

from telebot import TeleBot
from telebot import types
from psycopg2.extras import NumericRange

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import (
    product_keyboard,
    product_create_keyboard,
    product_choose_category_keyboard
)
from src.utils.wrappers import error_handler
from src.handlers.shared import (
    prepare_product_info,
    check_price,
    check_production_time,
    check_prod_limit,
    PriceCheckResult,
    ProductionTimeCheckResult,
    ProdLimitCheckResult
)
from src.states.create_product_session import (
    set_create_product_session, 
    get_create_product_session, 
    clear_create_product_session
)
from src.utils.content import get_production_time_days_ru_format
from src.utils.clean import delete_message
from src.utils.file import download_image_bytes

def register_product_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
    @err_handler
    def show_product_details(call):
        logger.debug("show_product_details CALL")
        
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[1])
        text, _ = prepare_product_info(call.message.chat.id, bot, db, content_cfg, logger, article_number)

        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.product.admin.create.message)
    @err_handler
    def start_product_creating(message: types.Message):
        logger.debug("start_product_creating CALL") 
        
        user_id = message.from_user.id
        
        session = set_create_product_session(user_id)
        session["data"]["article_number"] = db.get_max_article_number() + 1

        product_text = process_product_data(session)

        sent = bot.send_message(
            message.chat.id,
            product_text,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        session["data"]["product_message_id"] = sent.message_id
        
    def process_product_data(session: Dict[str, Any]) -> str:
        logger.debug("process_product_data CALL")
        
        name = session["data"]["name"]
        article_number = session["data"]["article_number"]
        description = session["data"]["description"]
        price = session["data"]["price"]
        category = session["data"]["category"]
        production_time = session["data"]["production_time"]
        prod_limit = session["data"]["prod_limit"]
        materials = ", ".join(session["data"]["materials"])
        
        production_time_days = ""
        if production_time:
            production_time_days = get_production_time_days_ru_format(
                production_time, 
                content_cfg.product.production_time.unit_1,
                content_cfg.product.production_time.unit_234,
                content_cfg.product.production_time.unit_other
            )
        
        product_text = content_cfg.get_product_details_text(
            name,
            article_number,
            description,
            price,
            materials,
            category,
            production_time,
            prod_limit,
            production_time_days
        )
        
        return product_text
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_name")
    @err_handler
    def add_name(call):
        logger.debug("add_name CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.name.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_name,
        )
        
    def process_name(message: types.Message):
        logger.debug("process_name CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        name = message.text.strip()
        if not name:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        session["data"]["name"] = name
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.name.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
        
    @bot.callback_query_handler(func=lambda call: call.data == "add_description")
    @err_handler
    def add_description(call):
        logger.debug("add_description CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.description.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_description,
        )
        
    def process_description(message: types.Message):
        logger.debug("process_description CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        description = message.text.strip()
        if not description:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        session["data"]["description"] = description
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.description.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_price")
    @err_handler
    def add_price(call):
        logger.debug("add_price CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.price.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_price,
        )
    
    def process_price(message: types.Message):
        logger.debug("process_price CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        price = message.text.strip()
        if not price:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        
        check_result, price = check_price(price, logger)
        if check_result == PriceCheckResult.NOT_NUMBER:
            bot.send_message(message.chat.id, content_cfg.product.admin.create.price.not_number.message)
            return
        elif check_result == PriceCheckResult.NEGATIVE:
            bot.send_message(message.chat.id, content_cfg.product.admin.create.price.negative.message)
            return
        
        session["data"]["price"] = price
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.price.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "add_category")
    @err_handler
    def add_category(call):
        logger.debug("add_category CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.category.text
        bot.send_message(
            call.message.chat.id,
            prompt,
            parse_mode="Markdown",
            reply_markup=product_choose_category_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("create_choose_"))
    @err_handler
    def create_choose_category(call):
        logger.debug("create_choose_category CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        category = content_cfg.catalog.eng2ru_category_map[call.data.split('_')[2]]
        
        session["data"]["category"] = category
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, call.message.chat.id, call.message.message_id, logger)
        
        bot.send_message(
            call.message.chat.id,
            content_cfg.product.admin.create.category.success.message
        )
        
        bot.edit_message_text(
            product_text,
            call.message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "add_production_time")
    @err_handler
    def add_production_time(call):
        logger.debug("add_production_time CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.production_time.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_production_time,
        )
    
    def process_production_time(message: types.Message):
        logger.debug("process_production_time CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        production_time_str = message.text.strip()
        if not production_time_str:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        check_result, production_time = check_production_time(production_time_str)
        if check_result == ProductionTimeCheckResult.LOWER_NOT_NUMBER:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.production_time.lower.not_number.message
            )
            return
        elif check_result == ProductionTimeCheckResult.LOWER_NEGATIVE:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.production_time.lower.negative.message
            )
            return
        elif check_result == ProductionTimeCheckResult.UPPER_NOT_NUMBER:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.production_time.upper.not_number.message
            )
            return
        elif check_result == ProductionTimeCheckResult.UPPER_NEGATIVE:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.production_time.upper.negative.message
            )
            return
        
        production_time = NumericRange(production_time.lower, production_time.upper+1)
        
        session["data"]["production_time"] = production_time
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.production_time.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "add_prod_limit")
    @err_handler
    def add_prod_limit(call):
        logger.debug("add_prod_limit CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.prod_limit.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_prod_limit,
        )
    
    def process_prod_limit(message: types.Message):
        logger.debug("process_prod_limit CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prod_limit = message.text.strip()
        if not prod_limit:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        check_result, prod_limit = check_prod_limit(prod_limit, logger)
        if check_result == ProdLimitCheckResult.NOT_NUMBER:
            bot.send_message(message.chat.id, content_cfg.product.admin.create.prod_limit.not_number.message)
            return
        elif check_result == ProdLimitCheckResult.NEGATIVE:
            bot.send_message(message.chat.id, content_cfg.product.admin.create.prod_limit.negative.message)
            return
        
        session["data"]["prod_limit"] = prod_limit
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.prod_limit.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_materials")
    @err_handler
    def add_materials(call):
        logger.debug("add_materials CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        prompt = content_cfg.product.admin.create.materials.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_materials,
        )
        
    def process_materials(message: types.Message):
        logger.debug("process_materials CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        materials_str = message.text.strip()
        if not materials_str:
            bot.send_message(
                message.chat.id,
                content_cfg.product.admin.create.empty_value.message
            )
            return
        
        materials = []
        for material in materials_str.split(','):
            materials.append(material.strip())
            
        session["data"]["materials"] = materials
        
        product_text = process_product_data(session)
        
        product_message_id = session["data"]["product_message_id"]
        
        delete_message(bot, message.chat.id, message.message_id, logger)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.materials.success.message
        )
        
        bot.edit_message_text(
            product_text,
            message.chat.id,
            product_message_id,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "create_add_image")
    @err_handler
    def create_add_image(call):
        logger.debug("create_add_image CALL")

        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        article_number = session["data"]["article_number"]
        image_dir = f"images/products/{article_number}"
        session["data"]["image_dir"] = image_dir
        image_dir = Path(image_dir)
        image_dir.mkdir(parents=True, exist_ok=True)
        
        all_files = sorted(
            [f for f in os.listdir(image_dir) if f.startswith("img")]
        )
        
        current_image_quantity = len(all_files)
        if current_image_quantity + 1 > 10:
            bot.send_message(call.message.chat.id, content_cfg.product.admin.create.images.add.exceed_limit.message)
            return
        
        prompt = content_cfg.product.admin.create.images.add.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            create_process_image,
            image_dir,
            current_image_quantity
        )
        
    def create_process_image(message: types.Message, image_dir: Path, current_image_quantity: int):
        logger.debug("create_process_image CALL")
        
        user_id = message.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        image_file_id = None
        if message.photo:
            image_file_id = message.photo[-1].file_id
        else:
            bot.send_message(message.chat.id, content_cfg.product.admin.create.images.add.incorrect_file_format.message)
            return
        
        image_number = current_image_quantity + 1
        
        image_path = image_dir / f"img{image_number}.jpg"
        
        image_bytes = download_image_bytes(cfg.token, image_file_id)
        image_path.write_bytes(image_bytes)
        
        bot.send_message(
            message.chat.id,
            content_cfg.product.admin.create.images.add.success.message
        )
        
        image_filenames = os.listdir(image_dir)
        if image_filenames:
            media = []
            for image_filename in image_filenames:
                with open(image_dir / image_filename, 'rb') as f:
                    media.append(types.InputMediaPhoto(f.read()))
            if media:
                bot.send_media_group(message.chat.id, media)
        
        product_text = process_product_data(session)
        
        sent = bot.send_message(
            message.chat.id,
            product_text,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
        session["data"]["product_message_id"] = sent.message_id
        
    @bot.callback_query_handler(func=lambda call: call.data == "clear_product")
    @err_handler
    def clear_product(call):
        logger.debug("clear_product CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        image_dir = Path(session["data"]["image_dir"])
        
        all_files = sorted(
            [f for f in os.listdir(image_dir) if f.startswith("img")]
        )
        
        if image_dir.exists() and len(all_files) > 0:
            try:
                shutil.rmtree(image_dir)
            except Exception as e:
                logger.error(f"Failed to delete directory {image_dir.name}: {e}")
                bot.send_message(
                    call.message.chat.id,
                    content_cfg.product.admin.create.clear.error.message
                )
                return
        
        session = clear_create_product_session(user_id)
        
        bot.send_message(
            call.message.chat.id,
            content_cfg.product.admin.create.clear.success.message
        )
        
        product_text = process_product_data(session)
        
        sent = bot.send_message(
            call.message.chat.id,
            product_text,
            parse_mode="Markdown",
            reply_markup=product_create_keyboard(content_cfg)
        )
        
        session["data"]["product_message_id"] = sent.message_id
        
    @bot.callback_query_handler(func=lambda call: call.data == "complete_product")
    @err_handler
    def complete_product(call):
        logger.debug("complete_product CALL")
        
        user_id = call.from_user.id
        
        session = get_create_product_session(user_id)
        if not session:
            bot.send_message(call.message.message.chat.id, content_cfg.product.admin.create.session_not_found.message)
            return
        
        success = db.create_product(
            session["data"]["article_number"],
            session["data"]["name"],
            session["data"]["price"],
            session["data"]["category"],
            session["data"]["description"],
            session["data"]["production_time"],
            session["data"]["prod_limit"],
            session["data"]["image_dir"]
        )
        
        if success:
            clear_create_product_session(user_id)
            
            bot.send_message(
                call.message.chat.id,
                content_cfg.product.admin.create.complete.success.message
            )
        else:
            bot.send_message(
                call.message.chat.id,
                content_cfg.product.admin.create.complete.error.message
            )
            
            