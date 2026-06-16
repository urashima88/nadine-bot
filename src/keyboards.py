from telebot import types
from typing import List

from src.config.content_config import ContentConfig

def main_menu_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog.message),
        types.KeyboardButton(content_cfg.cart.message),
        types.KeyboardButton(content_cfg.common.user.personal_data.message),
        types.KeyboardButton(content_cfg.order.user.message),
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

def admin_catalog_category_menu_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.all_products.message, callback_data='admin_catalog_all'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.bracelets.message, callback_data='admin_catalog_bracelets'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.earrings.message, callback_data='admin_catalog_earrings'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.necklaces.message, callback_data='admin_catalog_necklaces'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.brooches.message, callback_data='admin_catalog_brooches'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.pendants.message, callback_data='admin_catalog_pendants'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.chains.message, callback_data='admin_catalog_chains'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.rings.message, callback_data='admin_catalog_rings')
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
        types.InlineKeyboardButton(content_cfg.order.place.message, callback_data='start_order'),
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

def cart_edit_product_keyboard(content_cfg: ContentConfig, article_number: int, quantity: str):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(content_cfg.cart.edit.product.decrease.message, callback_data=f"decrease_product_{article_number}"),
        types.InlineKeyboardButton(quantity, callback_data="ignore"),
        types.InlineKeyboardButton(content_cfg.cart.edit.product.increase.message, callback_data=f"increase_product_{article_number}"),
        types.InlineKeyboardButton(content_cfg.cart.edit.product.delete.message, callback_data=f"delete_product_{article_number}")
    ]
    markup.add(*buttons)
    return markup

def common_user_profile_edit_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.common.profile.edit.full_name.message, callback_data="edit_full_name"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.phone.message, callback_data="edit_phone"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.timezone.message, callback_data="edit_timezone"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.delivery_company.message, callback_data="edit_delivery_company"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.delivery_point_address.message, callback_data="edit_delivery_point_address"),
    ]
    markup.add(*buttons)
    return markup

def common_admin_profile_edit_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.common.profile.edit.full_name.message, callback_data="edit_full_name"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.phone.message, callback_data="edit_phone"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.timezone.message, callback_data="edit_timezone")
    ]
    markup.add(*buttons)
    return markup

def order_user_profile_field_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.common.profile.edit.yes.message, callback_data="edit_field_yes"),
        types.InlineKeyboardButton(content_cfg.common.profile.edit.no.message, callback_data="edit_field_no")
    ]
    markup.add(*buttons)
    return markup

def order_final_summary_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.place.final.message, callback_data="place_order")
    ]
    markup.add(*buttons)
    return markup

def order_set_delivery_price_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.admin.new.set_delivery_price.message, callback_data=f"set_delivery_price_{order_id}"),
        types.InlineKeyboardButton(content_cfg.order.admin.new.cancel.message, callback_data=f"admin_cancel_order_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def order_send_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.admin.new.send.for_payment.message, callback_data=f"send_for_payment_{order_id}"),
        types.InlineKeyboardButton(content_cfg.order.admin.new.send.receipt.message, callback_data=f"send_receipt_{order_id}"),
        types.InlineKeyboardButton(content_cfg.order.admin.new.cancel.message, callback_data=f"admin_cancel_order_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def order_user_cancel_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.user.cancel.message, callback_data=f"user_cancel_order_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def order_user_control_show_mode_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.order.user.all.control_show.next.message),
        types.KeyboardButton(content_cfg.order.user.all.control_show.next5.message),
        types.KeyboardButton(content_cfg.order.user.all.control_show.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def order_user_show_current_review_status_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.user.all.control_show.current.copy_to_cart.message, callback_data=f"copy_to_cart_{order_id}"),
        types.InlineKeyboardButton(content_cfg.order.user.all.control_show.current.cancel.message, callback_data=f"show_user_cancel_order_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def order_user_show_current_not_review_status_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.user.all.control_show.current.copy_to_cart.message, callback_data=f"copy_to_cart_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def admin_main_menu_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog.admin.message),
        types.KeyboardButton(content_cfg.product.admin.create.message),
        types.KeyboardButton(content_cfg.order.admin.all.message),
        types.KeyboardButton(content_cfg.common.admin.user_data.all.message),
        types.KeyboardButton(content_cfg.statistics.admin.message),
        types.KeyboardButton(content_cfg.common.admin.personal_data.message),
        types.KeyboardButton(content_cfg.settings.admin.message)
    ]
    markup.add(*buttons)
    return markup

def order_admin_control_show_mode_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.order.admin.all.control_show.next.message),
        types.KeyboardButton(content_cfg.order.admin.all.control_show.next5.message),
        types.KeyboardButton(content_cfg.order.admin.all.control_show.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def order_admin_show_current_review_status_keyboard(content_cfg: ContentConfig, order_id: str):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.order.admin.all.control_show.current.cancel.message, callback_data=f"show_admin_cancel_order_{order_id}")
    ]
    markup.add(*buttons)
    return markup

def common_admin_control_show_user_data_mode_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.common.admin.user_data.all.control_show.next.message),
        types.KeyboardButton(content_cfg.common.admin.user_data.all.control_show.next5.message),
        types.KeyboardButton(content_cfg.common.admin.user_data.all.control_show.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def admin_catalog_control_show_mode_keyboard(content_cfg: ContentConfig):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton(content_cfg.catalog.admin.control_show.next.message),
        types.KeyboardButton(content_cfg.catalog.admin.control_show.next5.message),
        types.KeyboardButton(content_cfg.catalog.admin.control_show.stop.message),
        types.KeyboardButton(content_cfg.catalog.admin.control_show.go_back_to_main_menu.message)
    ]
    markup.add(*buttons)
    return markup

def admin_catalog_product_keyboard(content_cfg: ContentConfig, article_number: int):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.message, callback_data=f'edit_product_{article_number}'),
    ]
    markup.add(*buttons)
    return markup

def catalog_edit_product_keyboard(content_cfg: ContentConfig, article_number: int):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.name.message, callback_data=f'edit_name_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.description.message, callback_data=f'edit_description_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.price.message, callback_data=f'edit_price_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.materials.message, callback_data=f'edit_materials_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.category.message, callback_data=f'edit_category_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.production_time.message, callback_data=f'edit_production_time_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.prod_limit.message, callback_data=f'edit_prod_limit_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.images.message, callback_data=f'edit_images_{article_number}')
    ]
    
    markup.add(*buttons)
    return markup

def catalog_edit_product_category_keyboard(content_cfg: ContentConfig, article_number: int):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.bracelets.message, callback_data=f'choose_bracelets_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.earrings.message, callback_data=f'choose_earrings_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.necklaces.message, callback_data=f'choose_necklaces_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.brooches.message, callback_data=f'choose_brooches_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.pendants.message, callback_data=f'choose_pendants_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.chains.message, callback_data=f'choose_chains_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.rings.message, callback_data=f'choose_rings_{article_number}')
    ]
    markup.add(*buttons)
    return markup

def catalog_edit_product_images_keyboard(content_cfg: ContentConfig, article_number: int, image_quantity: int):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for i in range(image_quantity):
        image_number = i+1
        image_idx = i
        buttons.extend([
            types.InlineKeyboardButton(
                content_cfg.get_catalog_admin_edit_images_current_message(image_number=image_number),
                callback_data=f"edit_image_{article_number}_{image_idx}"
            ),
            types.InlineKeyboardButton(
                content_cfg.get_catalog_admin_edit_images_current_delete_message(image_number=image_number),
                callback_data=f"delete_image_{article_number}_{image_idx}"
            )
        ])
    
    buttons.append(
        types.InlineKeyboardButton(content_cfg.catalog.admin.edit.images.add.message, callback_data=f"add_image_{article_number}")
    )
    
    markup.add(*buttons)
    return markup

def product_create_keyboard(content_cfg: ContentConfig, article_number: int):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.bracelets.message, callback_data=f'choose_bracelets_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.earrings.message, callback_data=f'choose_earrings_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.necklaces.message, callback_data=f'choose_necklaces_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.brooches.message, callback_data=f'choose_brooches_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.pendants.message, callback_data=f'choose_pendants_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.chains.message, callback_data=f'choose_chains_{article_number}'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.rings.message, callback_data=f'choose_rings_{article_number}')
    ]
    markup.add(*buttons)
    return markup

def product_create_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.product.admin.create.name.message, callback_data='add_name'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.description.message, callback_data='add_description'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.price.message, callback_data='add_price'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.materials.message, callback_data='add_materials'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.category.message, callback_data='add_category'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.production_time.message, callback_data='add_production_time'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.prod_limit.message, callback_data='add_prod_limit'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.images.add.message, callback_data='create_add_image'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.clear.message, callback_data='clear_product'),
        types.InlineKeyboardButton(content_cfg.product.admin.create.complete.message, callback_data='complete_product')
    ]
    markup.add(*buttons)
    return markup
    
def product_choose_category_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.bracelets.message, callback_data='create_choose_bracelets'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.earrings.message, callback_data='create_choose_earrings'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.necklaces.message, callback_data='create_choose_necklaces'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.brooches.message, callback_data='create_choose_brooches'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.pendants.message, callback_data='create_choose_pendants'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.chains.message, callback_data='create_choose_chains'),
        types.InlineKeyboardButton(content_cfg.catalog.menu.categories.rings.message, callback_data='create_choose_rings')
    ]
    markup.add(*buttons)
    return markup

def statistics_keyboard(content_cfg: ContentConfig):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(content_cfg.statistics.admin.histogram.completed_orders.year.message, callback_data="plot_completed_orders_year"),
        types.InlineKeyboardButton(content_cfg.statistics.admin.histogram.revenue.year.message, callback_data="plot_revenue_year"),
        types.InlineKeyboardButton(content_cfg.statistics.admin.histogram.new_users.year.message, callback_data="plot_new_users_year")
    ]
    markup.add(*buttons)
    return markup