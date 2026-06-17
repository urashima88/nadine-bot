
import telebot

from src.handlers.catalog import register_catalog_handlers
from src.handlers.cart import register_cart_handlers
from src.handlers.common import register_common_handlers
from src.handlers.product import register_product_handlers
from src.handlers.order import register_order_handlers
from src.handlers.statistics import register_statistics_handlers
from src.handlers.settings import register_settings_handlers
from src.logging.logger import setup_logger
from src.storage import Storage
from src.config.config import Config, load_config
from src.config.content_config import ContentConfig

def main():
    cfg: Config = load_config()    

    logger = setup_logger(
        cfg.log_level,
        cfg.use_stream_handler,
        cfg.use_file_handler,
        cfg.logs_dir
    )
    
    conn_args = {
        "host": cfg.db_host,
        "port": cfg.db_port,
        "dbname": cfg.db_name,
        "user": cfg.db_user,
        "password":cfg.db_password
    }
    
    db = Storage(conn_args, logger)
    
    logger.info("Connected to db")

    bot = telebot.TeleBot(cfg.token)

    content_cfg: ContentConfig = ContentConfig(cfg.content_config_path, logger)

    register_common_handlers(bot, db, cfg, content_cfg, logger)
    register_catalog_handlers(bot, db, cfg, content_cfg, logger)
    register_product_handlers(bot, db, cfg, content_cfg, logger)
    register_cart_handlers(bot, db, cfg, content_cfg, logger)
    register_order_handlers(bot, db, cfg, content_cfg, logger)
    register_statistics_handlers(bot, db, cfg, content_cfg, logger)
    register_settings_handlers(bot, db, cfg, content_cfg, logger)
    
    logger.info("Starting bot...")
    bot.polling(none_stop=True, interval=2, timeout=40)

if __name__ == '__main__':
    main()