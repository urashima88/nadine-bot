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
        types.InlineKeyboardButton(content_cfg.catalog_menu_rings_category, callback_data='catalog_rings'),
        types.InlineKeyboardButton(content_cfg.catalog_menu_back, callback_data='back_to_main')
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
        types.InlineKeyboardButton(content_cfg.back_to_catalog_message, callback_data='back_to_catalog')
    ]
    markup.add(*buttons)
    return markup

def cart_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.empty_cart_message, callback_data='clear_cart'),
        types.InlineKeyboardButton(content_cfg.place_order_message, callback_data='checkout'),
        types.InlineKeyboardButton(content_cfg.back_message, callback_data='back_to_main')
    ]
    markup.add(*buttons)
    return markup