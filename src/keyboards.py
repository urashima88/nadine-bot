from telebot import types

from src.config.content_config import ContentConfig

def main_menu_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog_message),
        types.KeyboardButton(content_cfg.cart_message),
        types.KeyboardButton(content_cfg.contact_with_message),
        types.KeyboardButton(content_cfg.about_message)
    ]
    markup.add(*buttons)
    return markup

def catalog_menu_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog_menu_all_products_text, callback_data='catalog_all'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_bracelets_category, callback_data='catalog_bracelets'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_earrings_category, callback_data='catalog_earrings'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_necklaces_category, callback_data='catalog_necklaces'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_brooches_category, callback_data='catalog_brooches'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_pendants_category, callback_data='catalog_pendants'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_chains_category, callback_data='catalog_chains'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_rings_category, callback_data='catalog_rings')
    ]
    markup.add(*buttons)
    return markup

def catalog_control_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog_control_next_message),
        types.KeyboardButton(content_cfg.catalog_control_next5_message),
        types.KeyboardButton(content_cfg.catalog_control_stop_message),
        types.KeyboardButton(content_cfg.catalog_control_back_to_main_menu_message)
    ]
    markup.add(*buttons)
    return markup

def catalog_product_keyboard(content_cfg: ContentConfig, article_number):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.more_detailed_message, callback_data=f'detail_{article_number}'),
        types.InlineKeyboardButton(content_cfg.add_to_cart_message, callback_data=f'add_{article_number}')
    ]
    markup.add(*buttons)
    return markup

def product_keyboard(content_cfg: ContentConfig, article_number):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.add_to_cart_message, callback_data=f'add_{article_number}'),
    ]
    markup.add(*buttons)
    return markup

def cart_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.edit_cart_message, callback_data='edit_cart'),
        types.InlineKeyboardButton(content_cfg.clear_cart_message, callback_data='clear_cart'),
        types.InlineKeyboardButton(content_cfg.place_order_message, callback_data='checkout'),
    ]
    markup.add(*buttons)
    return markup

def edit_cart_control_keyboard(content_cfg: ContentConfig) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.cart_control_next_message),
        types.KeyboardButton(content_cfg.cart_control_next5_message),
        types.KeyboardButton(content_cfg.cart_control_stop_message),
        types.KeyboardButton(content_cfg.cart_control_back_to_main_menu_message)
    ]
    markup.add(*buttons)
    return markup

def edit_product_keyboard(content_config: ContentConfig, article_number: int, quantity: str):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(content_config.edit_cart_decrease_product_message, callback_data=f"edit_decrease_{article_number}"),
        types.InlineKeyboardButton(quantity, callback_data="ignore"),
        types.InlineKeyboardButton(content_config.edit_cart_increase_product_message, callback_data=f"edit_increase_{article_number}"),
        types.InlineKeyboardButton(content_config.edit_cart_delete_product_message, callback_data=f"edit_delete_{article_number}")
    ]
    markup.add(*buttons)
    return markup