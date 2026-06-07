from logging import Logger
from typing import Tuple

from telebot import TeleBot

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.utils.wrappers import error_handler
from src.states.order_session import (
    set_order_session,
    get_order_session,
    delete_order_session,
)
from src.keyboards import (
    order_user_profile_field_keyboard,
    order_final_summary_keyboard,
    order_set_delivery_price_keyboard,
    order_send_keyboard
)
from src.utils.profile import check_and_update_user_profile_field
from src.utils.clean import delete_message
from src.handlers.shared import get_cart_content
from src.utils.content import get_production_time_days_ru_format, str_to_numeric_range

def register_order_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data == "start_order")
    @err_handler
    def start_order_placement(call):
        logger.debug("place_order CALL")
        
        bot.answer_callback_query(call.id)
        
        user_id = call.from_user.id
        
        if not db.can_user_create_order(user_id, max_orders_per_day=content_cfg.order.limit_per_day):
            bot.send_message(
                call.message.chat.id,
                content_cfg.order.exceed_limit.message,
            )
            return
        else:
            today_orders_count = db.get_user_today_orders_count(user_id)
            remaining = content_cfg.order.limit_per_day - today_orders_count
            bot.send_message(
                call.message.chat.id,
                content_cfg.get_order_start_message(remaining)
            )
        
        start_order_chain(call)       
            
    def start_order_chain(call):
        logger.debug("start_order_chain CALL")
        
        user_id = call.from_user.id

        full_name, phone, delivery_company, delivery_point_address = db.get_user_profile_data(user_id)
        field_values = [full_name, phone, delivery_company, delivery_point_address]
        set_order_session(user_id, call.message.chat.id, field_values, 0)
        check_order_chain(call)

    def get_field_name_and_prompt(index: int) -> Tuple[str, str]:
        logger.debug("get_field_name_and_prompt CALL")

        if index == 0:
            return "full_name", content_cfg.common.user.profile.edit.full_name.text
        elif index == 1:
            return "phone", content_cfg.common.user.profile.edit.phone.text
        elif index == 2:
            return "delivery_company", content_cfg.common.user.profile.edit.delivery_company.text
        return "delivery_point_address", content_cfg.common.user.profile.edit.delivery_point_address.text
        
    def update_user_profile_field(message, call, index: int):
        logger.debug("update_user_profile_field CALL")
        
        name, _ = get_field_name_and_prompt(index)
        success, success_message = check_and_update_user_profile_field(
            message, 
            bot, 
            db, 
            call.from_user.id, 
            "edit_" + name,
            content_cfg
        )
            
        if success:
            bot.send_message(message.chat.id, success_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            if index < 4:
                session = get_order_session(call.from_user.id)
                if not session:
                    bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
                    return
                session["index"] += 1
                check_order_chain(call)
        else:
            delete_order_session(call.from_user.id)
            bot.send_message(message.chat.id, content_cfg.common.user.profile.edit.update_error.message)
       
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_field_'))
    @err_handler
    def handle_edit_field_callback(call):
        logger.debug("handle_edit_field_callback CALL")
        
        session = get_order_session(call.from_user.id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        index = session["index"]
        
        choice = call.data.split("_")[2]
        if choice == "yes":
            _, prompt = get_field_name_and_prompt(index)
            message = bot.send_message(call.message.chat.id, prompt)
            bot.register_next_step_handler(
                message,
                update_user_profile_field,
                call,
                index
            )
        else:
            if index < 4:
                session["index"] += 1
                check_order_chain(call)
            
    def get_delivery_field_question(index: int, field_value: str) -> str:
        logger.debug("get_delivery_field_question CALL")
        
        if index == 2:
            return content_cfg.get_common_user_profile_edit_delivery_company_question_message(field_value)
        elif index == 3:
            return content_cfg.get_common_user_profile_edit_delivery_point_address_question_message(field_value)
        
    def check_order_chain(call):
        logger.debug("check_order_chain CALL")
        
        user_id = call.from_user.id
        session = get_order_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        field_values = session["field_values"]
        index = session["index"]
        if index < len(field_values):
            field_value = field_values[index]
            if not field_value:
                _, prompt = get_field_name_and_prompt(index)
                message = bot.send_message(call.message.chat.id, prompt)
                bot.register_next_step_handler(
                    message,
                    update_user_profile_field,
                    call,
                    index
                )
            else:
                if index <= 1:
                    session["index"] += 1
                    check_order_chain(call)
                else:
                    bot.send_message(
                        call.message.chat.id,
                        get_delivery_field_question(index, field_value),
                        parse_mode="Markdown",
                        reply_markup=order_user_profile_field_keyboard(content_cfg)
                    )
        else:
            show_final_order_summary(call)

    def show_final_order_summary(call):
        logger.debug("show_final_order_summary CALL")
        
        user_id = call.from_user.id
        session = get_order_session(user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        chat_id = session["chat_id"]
        header_text = content_cfg.order.place.final.header_text
        cart_text = get_cart_content(
            user_id, db, content_cfg, logger, header_text
        )
        
        if not cart_text:
            delete_order_session(user_id)
            bot.send_message(chat_id, content_cfg.cart.is_empty.message)
            return
        
        bot.send_message(
            chat_id,
            cart_text,
            reply_markup=order_final_summary_keyboard(content_cfg),
            parse_mode="Markdown"
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "place_order")
    @err_handler
    def place_order(call):
        logger.debug("place_order CALL")
        
        bot.answer_callback_query(call.id)
        tg_user_id = call.from_user.id
        
        session = get_order_session(tg_user_id)
        if not session:
            bot.send_message(call.message.chat.id, content_cfg.order.session_not_found.message)
            return
        
        cart_products = db.get_cart_products(tg_user_id)
        if not cart_products:
            delete_order_session(tg_user_id)
            bot.send_message(call.message.chat.id, content_cfg.cart.is_empty.message)
            return
        
        full_name, phone, delivery_company, delivery_point_address = db.get_user_profile_data(tg_user_id)
        empty_fields = []
        if not full_name:
            empty_fields.append("full_name")
        if not phone:
            empty_fields.append("phone")
        if not delivery_company:
            empty_fields.append("delivery_company")
        if not delivery_point_address:
            empty_fields.append("delivery_point_address")
        if empty_fields:
            delete_order_session(tg_user_id)
            bot.send_message(call.message.chat.id, content_cfg.get_order_place_empty_fields_message(empty_fields))
            return
        
        tg_username, tg_full_name = db.get_user_tg_data(tg_user_id)
        
        total_price = sum(product["price"] * product["quantity"] for product in cart_products)
        order_id = db.create_order(tg_user_id, total_price, delivery_company, delivery_point_address)
        if not order_id:
            delete_order_session(tg_user_id)
            bot.send_message(call.message.chat.id, content_cfg.order.place.error.message)
            return
        
        bot.send_message(call.message.chat.id, content_cfg.order.place.transfer_to_admin.message)
        
        admin_user_id = db.get_admin_user_id()
        if admin_user_id:
            products_details = []
            for product in cart_products:
                product_data = db.get_product_by_article_number(product["article_number"])
                if product_data:
                    details = content_cfg.get_order_admin_product_details_long_text(
                        product["name"],
                        product["article_number"],
                        product["price"],
                        product["quantity"],
                        product["price"] * product["quantity"],
                        product_data["category"],
                        product_data["materials_list"],
                        product_data["production_time"],
                        get_production_time_days_ru_format(
                            product_data["production_time"], 
                            content_cfg.product.production_time.unit_1,
                            content_cfg.product.production_time.unit_234,
                            content_cfg.product.production_time.unit_other
                        )
                    )
                else:
                    details = content_cfg.get_order_admin_product_details_short_text(
                        product["name"],
                        product["article_number"],
                        product["price"],
                        product["quanity"],
                        product["price"] * product["quanity"]
                    )
                products_details.append(details)
                
            products_text = "\n\n".join(products_details)
            new_order_text = content_cfg.get_order_admin_new_text(
                order_id,
                tg_username,
                tg_full_name,
                full_name,
                phone,
                delivery_company,
                delivery_point_address,
                products_text,
                total_price
            )
            delete_order_session(tg_user_id)
            bot.send_message(
                admin_user_id,
                new_order_text,
                parse_mode="Markdown",
                reply_markup=order_set_delivery_price_keyboard(content_cfg, order_id)
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_delivery_price_"))
    @err_handler
    def set_delivery_price(call):
        logger.debug("set_delivery_price CALL")
        
        bot.answer_callback_query(call.id)
        order_id = (call.data.split("_")[3])
        
        prompt = content_cfg.order.admin.new.set_delivery_price.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            add_delivery_price,
            order_id
        )
        
    def add_delivery_price(message, order_id: str):
        new_value = float(message.text.strip().replace(',', '.'))
        if not new_value:
            bot.send_message(message.chat.id, content_cfg.order.admin.new.set_delivery_price.incorrect_value.message)
            return
        
        success = db.set_delivery_price(order_id, new_value)
        success_message = content_cfg.order.admin.new.set_delivery_price.success.message   
        if success:
            bot.send_message(message.chat.id, success_message)
            delete_message(bot, message.chat.id, message.message_id, logger)
            show_order(message.chat.id, order_id)
        else:
            bot.send_message(message.chat.id, content_cfg.order.admin.new.set_delivery_price.error.message)
    
    def show_order(chat_id: int, order_id: str):
        logger.debug("show_order CALL")
        
        order = db.get_order(order_id)
        products_details = []
        for product in order["products"]:
            production_time_range = str_to_numeric_range(product.get('production_time'))
            details = content_cfg.get_order_admin_product_details_long_text(
                product["name"],
                product["article_number"],
                product["price_at_order"],
                product["quantity"],
                product["price_at_order"] * product["quantity"],
                product["category"],
                product["materials"],
                production_time_range,
                get_production_time_days_ru_format(
                    production_time_range, 
                    content_cfg.product.production_time.unit_1,
                    content_cfg.product.production_time.unit_234,
                    content_cfg.product.production_time.unit_other
                )
            )
            products_details.append(details)

        products_text = "\n\n".join(products_details)
        order_text = content_cfg.get_order_admin_new_text(
                order_id,
                order["tg_username"] ,
                order["tg_full_name"],
                order["full_name"],
                order["phone"],
                order["delivery_company"],
                order["delivery_point_address"],
                products_text,
                order["order_price"] + order["delivery_price"],
                order["delivery_price"]
            )
        bot.send_message(
            chat_id,
            order_text,
            parse_mode="Markdown",
            reply_markup=order_send_keyboard(content_cfg, order_id)
        )