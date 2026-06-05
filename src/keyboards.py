from telebot import types

from src.config.content_config import ContentConfig

def main_menu_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog.message),
        types.KeyboardButton(content_cfg.cart.message),
        types.KeyboardButton(content_cfg.common.user.personal_data.message),
        types.KeyboardButton(content_cfg.common.user.orders.message),
        types.KeyboardButton(content_cfg.common.admin.contacts.message),
        types.KeyboardButton(content_cfg.common.admin.about.message)
    ]
    markup.add(*buttons)
    return markup

def catalog_category_menu_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.all_products.message, callback_data='catalog_all'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.bracelets.message, callback_data='catalog_bracelets'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.earrings.message, callback_data='catalog_earrings'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.necklaces.message, callback_data='catalog_necklaces'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.brooches.message, callback_data='catalog_brooches'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.pendants.message, callback_data='catalog_pendants'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.chains.message, callback_data='catalog_chains'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.rings.message, callback_data='catalog_rings')
    ]
    markup.add(*buttons)
    return markup

def catalog_control_show_mode_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog.control_show.next.message),
        types.KeyboardButton(content_cfg.catalog.control_show.next5.message),
        types.KeyboardButton(content_cfg.catalog.control_show.stop.message),
        types.KeyboardButton(content_cfg.catalog.control_show.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def catalog_product_keyboard(content_cfg: ContentConfig, article_number):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.product.details.message, callback_data=f'details_{article_number}'),
        types.InlineKeyboardButton(content_cfg.product.add_to_cart.message, callback_data=f'add_{article_number}')
    ]
    markup.add(*buttons)
    return markup

def product_keyboard(content_cfg: ContentConfig, article_number):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.product.add_to_cart.message, callback_data=f'add_{article_number}'),
    ]
    markup.add(*buttons)
    return markup

def cart_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.cart.edit.message, callback_data='edit_cart'),
        types.InlineKeyboardButton(content_cfg.cart.clear.message, callback_data='clear_cart'),
        types.InlineKeyboardButton(content_cfg.order.place.message, callback_data='checkout'),
    ]
    markup.add(*buttons)
    return markup

def cart_control_edit_mode_keyboard(content_cfg: ContentConfig) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.cart.control_edit.next.message),
        types.KeyboardButton(content_cfg.cart.control_edit.next5.message),
        types.KeyboardButton(content_cfg.cart.control_edit.stop.message),
        types.KeyboardButton(content_cfg.cart.control_edit.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def cart_edit_product_keyboard(content_config: ContentConfig, article_number: int, quantity: str):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(content_config.cart.edit.product.decrease.message, callback_data=f"decrease_product_{article_number}"),
        types.InlineKeyboardButton(quantity, callback_data="ignore"),
        types.InlineKeyboardButton(content_config.cart.edit.product.increase.message, callback_data=f"increase_product_{article_number}"),
        types.InlineKeyboardButton(content_config.cart.edit.product.delete.message, callback_data=f"delete_product_{article_number}")
    ]
    markup.add(*buttons)
    return markup

def common_user_profile_edit_keyboard(content_config: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_config.common.user.profile.edit.full_name.message, callback_data="edit_full_name"),
        types.InlineKeyboardButton(content_config.common.user.profile.edit.phone.message, callback_data="edit_phone"),
        types.InlineKeyboardButton(content_config.common.user.profile.edit.delivery_company.message, callback_data="edit_delivery_company"),
        types.InlineKeyboardButton(content_config.common.user.profile.edit.delivery_point_address.message, callback_data="edit_delivery_point_address"),
    ]
    markup.add(*buttons)
    return markup