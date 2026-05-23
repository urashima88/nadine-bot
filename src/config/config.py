from dataclasses import dataclass
import os

from dotenv import load_dotenv

@dataclass
class Config:
    token: str
    
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    db_port: str

    pg_admin_email: str
    pg_admin_password: str
    pg_admin_port: str

    migrations_dir: str

    product_images_path: str

    log_level: str
    use_stream_handler: bool
    use_file_handler: bool
    logs_dir: str
    
def load_config() -> Config:
    load_dotenv()
    
    cfg = Config(
        token = os.getenv("TOKEN"),
        db_host = os.getenv("DB_HOST"),
        db_user = os.getenv("DB_USER"),
        db_password = os.getenv("DB_PASSWORD"),
        db_name = os.getenv("DB_NAME"),
        db_port = os.getenv("DB_PORT"),
        pg_admin_email = os.getenv("PG_ADMIN_EMAIL", ""),
        pg_admin_password = os.getenv("PG_ADMIN_PASSWORD"),
        pg_admin_port = os.getenv("PG_ADMIN_PORT"),
        migrations_dir = os.getenv("MIGRATIONS_DIR", "migrations"),
        product_images_path = os.getenv("PRODUCT_IMAGES_PATH", "images/products"),
        log_level = os.getenv("LOG_LEVEL", "INFO"),
        use_stream_handler = bool(int(os.getenv("USE_STREAM_HANDLER", 1))),
        use_file_handler = bool(int(os.getenv("USE_FILE_HANDLER", 1))),
        logs_dir = os.getenv("LOGS_DIR", "logs"),
    )
    
    return cfg
