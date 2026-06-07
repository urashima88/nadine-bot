import os
from logging import Logger

from telebot import TeleBot, types

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.keyboards import product_keyboard
from src.utils.content import get_production_time_days_ru_format
from src.utils.wrappers import error_handler

def register_product_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
    @err_handler
    def show_product_details(call):
        logger.debug("show_product_details CALL")
        
        bot.answer_callback_query(call.id)
        
        article_number = int(call.data.split('_')[1])
        product = db.get_product_by_article_number(article_number)
        
        if not product:
            bot.send_message(call.message.chat.id, content_cfg.product.not_found.message)
            return

        name = product['name']
        description = product['description']
        price = product['price']
        category = product['category']
        production_time = product['production_time']
        prod_limit = product['prod_limit']
        image_dir = product['image_dir']
        materials_list = product['materials_list']
        
        text = content_cfg.get_product_details_text(
            name,
            article_number,
            description,
            price,
            materials_list,
            category,
            production_time,
            prod_limit,
            get_production_time_days_ru_format(
                production_time, 
                content_cfg.product.production_time.unit_1,
                content_cfg.product.production_time.unit_234,
                content_cfg.product.production_time.unit_other
            )
        )
        
        if os.path.exists(image_dir):
            image_filenames = os.listdir(image_dir)
            if image_filenames:
                media = []
                for image_filename in image_filenames:
                    with open(os.path.join(image_dir, image_filename), 'rb') as f:
                        media.append(types.InputMediaPhoto(f.read()))
                if media:
                    bot.send_media_group(call.message.chat.id, media)
        bot.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=product_keyboard(content_cfg, article_number),
            parse_mode="Markdown"
        )