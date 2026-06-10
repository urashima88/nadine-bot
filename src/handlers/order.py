from logging import Logger
from typing import Tuple, Dict, List, Any

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
from src.states.user_order_show_session import (
    user_order_show_set_session,
    user_order_show_get_session,
    user_order_show_delete_session
)
from src.keyboards import (
    order_user_profile_field_keyboard,
    order_final_summary_keyboard,
    order_user_cancel_keyboard,
    order_set_delivery_price_keyboard,
    order_send_keyboard,
    order_user_control_show_mode_keyboard,
    main_menu_keyboard,
    order_user_show_current_review_status_keyboard,
    order_user_show_current_not_review_status_keyboard
)
from src.utils.clean import delete_message
from src.handlers.shared import (
    get_cart_content, 
    get_order_content, 
    get_products_text_and_total_price,
    check_and_update_user_profile_field
)
from src.utils.content import (
    get_production_time_days_ru_format, 
    str_to_numeric_range,
    format_local_datetime
)

def register_order_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.callback_query_handler(func=lambda call: call.data == "start_order")
    @err_handler
    def start_order_placement(call):
        logger.debug("start_order_placement CALL")
        
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

        full_name, phone, timezone, delivery_company, delivery_point_address = db.get_user_profile_data(user_id)
        field_values = [full_name, phone, timezone, delivery_company, delivery_point_address]
        set_order_session(user_id, call.message.chat.id, field_values, 0)
        check_order_chain(call)

    def get_field_name_and_prompt(index: int) -> Tuple[str, str]:
        logger.debug("get_field_name_and_prompt CALL")

        if index == 0:
            return "full_name", content_cfg.common.user.profile.edit.full_name.text
        elif index == 1:
            return "phone", content_cfg.common.user.profile.edit.phone.text
        elif index == 2:
            return "timezone", content_cfg.common.user.profile.edit.timezone.text
        elif index == 3:
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
            if index < 5:
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
            if index < 5:
                session["index"] += 1
                check_order_chain(call)
            
    def get_delivery_field_question(index: int, field_value: str) -> str:
        logger.debug("get_delivery_field_question CALL")
        
        if index == 3:
            return content_cfg.get_common_user_profile_edit_delivery_company_question_message(field_value)
        elif index == 4:
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
                if index <= 2:
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
        
        full_name, phone, timezone, delivery_company, delivery_point_address = db.get_user_profile_data(tg_user_id)
        empty_fields = []
        if not full_name:
            empty_fields.append("full_name")
        if not phone:
            empty_fields.append("phone")
        if not timezone:
            empty_fields.append("timezone")
        if not delivery_company:
            empty_fields.append("delivery_company")
        if not delivery_point_address:
            empty_fields.append("delivery_point_address")
        if empty_fields:
            delete_order_session(tg_user_id)
            bot.send_message(call.message.chat.id, content_cfg.get_order_place_empty_fields_message(empty_fields))
            return
        
        tg_username, tg_full_name = db.get_user_tg_data(tg_user_id)
        
        cart_products = db.get_cart_products(tg_user_id)
        if not cart_products:
            bot.send_message(call.message.chat.id, content_cfg.cart.is_empty.message)
            return
        
        total_price = sum(product["price"] * product["quantity"] for product in cart_products)
        order_id = db.create_order(tg_user_id, total_price, delivery_company, delivery_point_address)
        if not order_id:
            delete_order_session(tg_user_id)
            bot.send_message(call.message.chat.id, content_cfg.order.place.error.message)
            return
        
        order_number = db.get_order_number_by_order_id(order_id)
        bot.send_message(
            call.message.chat.id, 
            content_cfg.get_order_place_transfer_to_admin_message(order_number),
            parse_mode="Markdown",
            reply_markup=order_user_cancel_keyboard(content_cfg, order_id)
        )
        
        order = db.get_order(order_id)
        
        admin_user_id = db.get_admin_user_id()
        if admin_user_id:
            products_details = get_order_products_details(order["products"])
            products_text = "\n\n".join(products_details)
            
            new_order_text = content_cfg.get_order_admin_new_text(
                order["order_number"],
                format_local_datetime(order["created_at"], order["timezone"]),
                tg_username,
                tg_full_name,
                full_name,
                phone,
                delivery_company,
                delivery_point_address,
                products_text,
                total_price,
                order["delivery_price"]
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
        products_details = get_order_products_details(order["products"])
        products_text = "\n\n".join(products_details)
        
        order_text = content_cfg.get_order_admin_new_text(
                order["order_number"],
                format_local_datetime(order["created_at"], order["timezone"]),
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
        
    def get_order_products_details(products: Dict[str, Any]) -> List[Any]:
        logger.debug("get_order_products_details CALL")
        
        products_details = []
        for product in products:
            production_time_range = str_to_numeric_range(product.get('production_time'))
            details = content_cfg.get_order_admin_product_details_text(
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
        return products_details
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_cancel_order_"))
    @err_handler
    def admin_cancel_order(call):
        logger.debug("admin_cancel_order CALL")
        
        order_id = (call.data.split("_")[3])
        
        prompt = content_cfg.order.admin.new.cancel.reason.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            execute_admin_cancel_order,
            call.id,
            order_id
        )
        
    def execute_admin_cancel_order(message, call_id, order_id: str):
        logger.debug("execute_admin_cancel_order CALL")
        
        cancel_reason = message.text.strip()
        
        order_data_for_notification = db.get_order_info_for_notification(order_id)
        order_number = order_data_for_notification["order_number"]
        created_at = order_data_for_notification["created_at"]
        timezone = order_data_for_notification["timezone"]
        tg_user_id = order_data_for_notification["tg_user_id"]
        
        success = db.cancel_order(order_id)
        if success:
            bot.answer_callback_query(
                call_id, 
                content_cfg.get_order_admin_new_cancel_success_message(order_number),
                show_alert=False
            )
            if tg_user_id:
                header_text = content_cfg.order.place.final.header_text
                order_text = get_order_content(
                    order_id, db, content_cfg, logger, header_text
                )
                bot.send_message(
                    tg_user_id, 
                    content_cfg.get_order_admin_new_cancel_reason_message(
                        order_number, 
                        format_local_datetime(created_at, timezone), 
                        cancel_reason, 
                        order_text
                    ),
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(
                    message.chat.id, 
                    content_cfg.order.admin.new.user_not_found.message,
                    show_alert=False
                )
        else:
            bot.answer_callback_query(
                call_id, 
                content_cfg.get_order_admin_new_cancel_error_message(order_number),
                show_alert=False
            )
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("send_for_payment_"))
    @err_handler
    def send_for_payment(call):
        logger.debug("send_for_payment CALL")
        
        order_id = (call.data.split("_")[3])
        
        prompt = content_cfg.order.admin.new.send.for_payment.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_invoice,
            order_id
        )

    def process_invoice(message, order_id: str):
        logger.debug("process_invoice CALL")
        
        admin_chat_id = message.chat.id
        
        invoice_file =  None
        if message.document:
            invoice_file = message.document.file_id
            file_type = "document"
        elif message.photo:
            invoice_file = message.photo[-1].file_id
            file_type = "photo"
        else:
            bot.send_message(admin_chat_id, content_cfg.order.admin.new.send.incorrect_file_format.message)
            return
        
        tg_user_id, timezone = db.get_tg_user_id_and_timezone(order_id)
        if not tg_user_id:
            bot.send_message(admin_chat_id, content_cfg.order.admin.new.user_not_found.message)
            return
        
        order_data = db.get_order_number_delivery_price_created_at(order_id)
        order_number = order_data["order_number"]
        delivery_price = order_data["delivery_price"]
        created_at = order_data["created_at"]
        
        products = db.get_order_products(order_id)
        products_text, total = get_products_text_and_total_price(products, content_cfg, logger)
        
        admin_phone = db.get_admin_phone()
        
        status = content_cfg.order.status.for_payment.text
        success = db.update_order_status(order_id, status)
        if not success:
            bot.send_message(admin_chat_id, content_cfg.order.status.update_error.message)
            return
        
        total_with_delivery = total + delivery_price
        for_payment_text = content_cfg.get_order_user_send_for_payment_text(
            order_number, 
            format_local_datetime(created_at, timezone),
            status,
            products_text, 
            delivery_price, 
            total_with_delivery, 
            admin_phone
        )
        
        if file_type == "document":
            bot.send_document(
                tg_user_id,
                invoice_file,
                caption=for_payment_text,
                parse_mode="Markdown",
                reply_markup=order_user_cancel_keyboard(content_cfg, order_id)
            )
        else:
            bot.send_photo(
                tg_user_id,
                invoice_file,
                caption=for_payment_text,
                parse_mode="Markdown",
                reply_markup=order_user_cancel_keyboard(content_cfg, order_id)
            )
        bot.send_message(admin_chat_id, content_cfg.get_order_admin_new_send_for_payment_success_message(order_number))
        bot.delete_message(admin_chat_id, message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("send_receipt_"))
    @err_handler
    def send_receipt(call):    
        logger.debug("send_receipt CALL")
        
        order_id = (call.data.split("_")[2])
        
        prompt = content_cfg.order.admin.new.send.receipt.file.text
        message = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_receipt,
            order_id
        )    
        
    def process_receipt(message, order_id: str):
        logger.debug("process_receipt CALL")
        
        admin_chat_id = message.chat.id
        
        receipt_file =  None
        if message.document:
            receipt_file = message.document.file_id
            file_type = "document"
        elif message.photo:
            receipt_file = message.photo[-1].file_id
            file_type = "photo"
        else:
            bot.send_message(admin_chat_id, content_cfg.order.admin.new.send.incorrect_file_format.message)
            return
        
        prompt = content_cfg.order.admin.new.send.receipt.delivery_info.text
        message = bot.send_message(message.chat.id, prompt)
        bot.register_next_step_handler(
            message,
            process_delivery_data,
            order_id,
            receipt_file,
            file_type
        )   
        
    def process_delivery_data(message, order_id: str, receipt_file: Any, file_type: str):
        logger.debug("process_delivery_data CALL")
            
        admin_chat_id = message.chat.id
        
        delivery_info = message.text.strip()
        if not delivery_info:
            bot.send_message(
                admin_chat_id, 
                content_cfg.order.admin.new.send.receipt.delivery_info.is_empty.message
            )
            return
        
        success = db.set_delivery_info(order_id, delivery_info)
        if not success:
            bot.send_message(
                admin_chat_id, 
                content_cfg.order.admin.new.send.receipt.delivery_info.failed_to_set.message
            )
            return
        
        tg_user_id, timezone = db.get_tg_user_id_and_timezone(order_id)
        if not tg_user_id:
            bot.send_message(admin_chat_id, content_cfg.order.admin.new.user_not_found.message)
            return
        
        order_data = db.get_order_number_delivery_price_created_at(order_id)
        order_number = order_data["order_number"]
        delivery_price = order_data["delivery_price"]
        created_at = order_data["created_at"]
        
        products = db.get_order_products(order_id)
        products_text, total = get_products_text_and_total_price(products, content_cfg, logger)
        
        status = content_cfg.order.status.completed.text
        success = db.update_order_status(order_id, status)
        if not success:
            bot.send_message(admin_chat_id, content_cfg.order.status.update_error.message)
            return
        
        total_with_delivery = total + delivery_price
        
        receipt_text = content_cfg.get_order_user_send_receipt_text(
            order_number,
            format_local_datetime(created_at, timezone),
            status,
            products_text,
            delivery_price,
            total_with_delivery,
            delivery_info
        )
        
        if file_type == "document":
            bot.send_document(
                tg_user_id,
                receipt_file,
                caption=receipt_text,
                parse_mode="Markdown"
            )
        else:
            bot.send_photo(
                tg_user_id,
                receipt_file,
                caption=receipt_text,
                parse_mode="Markdown"
            )
        bot.send_message(admin_chat_id, content_cfg.get_order_admin_new_send_receipt_success_message(order_number))
        bot.delete_message(admin_chat_id, message.message_id)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.order.user.message)
    @err_handler
    def show_user_orders(message):
        logger.debug("show_user_orders CALL")

        tg_user_id = message.from_user.id
        orders = db.get_user_orders(tg_user_id)
        
        if not orders:
            bot.send_message(message.chat.id, content_cfg.order.user.all.is_empty.message)
            return
        
        user_order_show_set_session(tg_user_id, orders)
        
        order_control_show_text = content_cfg.get_order_user_all_control_show_text(len(orders))
        
        bot.send_message(
            message.chat.id,
            order_control_show_text,
            parse_mode="Markdown",
            reply_markup=order_user_control_show_mode_keyboard(content_cfg)
        )
        
        send_next_orders(message.chat.id, tg_user_id, count=1)
        
    def send_all_orders_displayed_message(chat_id: int, user_id: int):
        logger.debug("send_all_orders_displayed CALL")
        
        bot.send_message(chat_id, content_cfg.order.user.all.displayed.message)
        bot.send_message(
            chat_id, 
            content_cfg.order.user.main_menu.message, 
            reply_markup=main_menu_keyboard(content_cfg)
        )
        user_order_show_delete_session(user_id)
        
    def send_next_orders(chat_id: int, user_id: int, count: int):
        logger.debug("send_next_orders CALL")
        
        session = user_order_show_get_session(user_id)
        if not session:
            bot.send_message(chat_id, content_cfg.order.user.all.control_show.session_not_found.message)
            return
        
        orders = session["orders"]
        sent = session["sent"]
        total = session["total"]
        
        if sent >= total:
            send_all_orders_displayed_message(chat_id, user_id)
            return
        
        to_send = min(count, total-sent)
        for i in range(to_send):
            idx = sent + i
            order = orders[idx]
            
            order_id = order["order_id"]
            order_number = order["order_number"]
            products_text, total = get_products_text_and_total_price(order["products"], content_cfg, logger)    
            delivery_price = order["delivery_price"]
            total_with_delivery = total + float(delivery_price)
            delivery_company = order["delivery_company"]
            delivery_point_address = order["delivery_point_address"]
            delivery_info = order["delivery_info"]
            created_at = order["created_at"]
            timezone = order["timezone"]
            status = order["status"]
            
            order_text = content_cfg.get_order_user_all_control_show_current_text(
                order_number,
                format_local_datetime(created_at, timezone),
                status,
                products_text,
                delivery_price,
                total_with_delivery,
                delivery_company,
                delivery_point_address,
                delivery_info
            )   
            
            if status == content_cfg.order.status.review.message:
                keyboard = order_user_show_current_review_status_keyboard(content_cfg, order_id)
            else:
                keyboard = order_user_show_current_not_review_status_keyboard(content_cfg, order_id)
            
            bot.send_message(
                chat_id,
                text=order_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        
        session["sent"] = sent + to_send
        if session["sent"] >= total:
            send_all_orders_displayed_message(chat_id, user_id)
            
    def send_orders(message, count):
        logger.debug("send_orders CALL")
        
        user_id = message.from_user.id
        session = user_order_show_get_session(user_id)
        if not session:
            bot.send_message(message.chat.id, content_cfg.order.user.all.control_show.session_not_found.message)
            return
        
        send_next_orders(message.chat.id, user_id, count)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.order.user.all.control_show.next.message)
    @err_handler
    def send_next_one_order(message):
        logger.debug("send_next_one CALL")
        
        send_orders(message, 1)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.order.user.all.control_show.next5.message)
    @err_handler
    def send_next_five_orders(message):
        logger.debug("send_next_five_orders CALL")
        
        send_orders(message, 5)
        
    @bot.message_handler(func=lambda message: message.text == content_cfg.order.user.all.control_show.go_back_to_main_menu.message)
    @err_handler
    def go_back_to_main_menu(message):
        logger.debug("go_back_to_main_menu CALL")
        
        user_id = message.from_user.id
        user_order_show_delete_session(user_id)
        bot.send_message(
            message.chat.id,
            content_cfg.order.user.main_menu.message,
            reply_markup=main_menu_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("user_cancel_order_"))
    @err_handler
    def user_cancel_order(call):
        logger.debug("user_cancel_order CALL")
        
        order_id = (call.data.split("_")[3])
        
        order = db.get_order(order_id)
        
        success = db.cancel_order(order_id)
        if success:   
            bot.answer_callback_query(
                call.id, 
                content_cfg.get_order_user_cancel_success_message(order["order_number"])
            )
        
            admin_user_id = db.get_admin_user_id()
            if admin_user_id:
                products_details = get_order_products_details(order["products"])
                products_text = "\n\n".join(products_details)

                cancel_order_text = content_cfg.get_order_admin_new_cancel_user_text(
                    order["order_number"],
                    format_local_datetime(order["created_at"], order["timezone"]),
                    order["tg_username"],
                    order["tg_full_name"],
                    order["full_name"],
                    order["phone"],
                    order["delivery_company"],
                    order["delivery_point_address"],
                    products_text,
                    order["order_price"] + order["delivery_price"],
                    order["delivery_price"],
                    order["delivery_info"]
                )
                
                bot.send_message(
                    admin_user_id,
                    cancel_order_text,
                    parse_mode="Markdown"
                )
        else:
            bot.answer_callback_query(
                call.id, 
                content_cfg.get_order_user_cancel_error_message(order["order_number"])
            )
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("show_user_cancel_order_"))
    @err_handler
    def show_user_cancel_order(call):
        logger.debug("show_user_cancel_order CALL")
        
        order_id = (call.data.split("_")[4])
        
        order = db.get_order(order_id)
        order_number = order["order_number"]
        
        success = db.cancel_order(order_id)
        if success:   
            bot.answer_callback_query(
                call.id, 
                content_cfg.get_order_user_cancel_success_message(order_number)
            )
            
            current_order_products_text, total = get_products_text_and_total_price(order["products"], content_cfg, logger)    
            delivery_price = order["delivery_price"]
            total_with_delivery = total + float(delivery_price)
            delivery_company = order["delivery_company"]
            delivery_point_address = order["delivery_point_address"]
            delivery_info = order["delivery_info"]
            created_at = order["created_at"]
            timezone = order["timezone"]
            status = content_cfg.order.status.canceled.text
            
            formatted_created_at = format_local_datetime(created_at, timezone)
            
            order_text = content_cfg.get_order_user_all_control_show_current_text(
                order_number,
                formatted_created_at,
                status,
                current_order_products_text,
                delivery_price,
                total_with_delivery,
                delivery_company,
                delivery_point_address,
                delivery_info
            )   
            
            if status == content_cfg.order.status.review.message:
                keyboard = order_user_show_current_review_status_keyboard(content_cfg, order_id)
            else:
                keyboard = order_user_show_current_not_review_status_keyboard(content_cfg, order_id)
            
            bot.edit_message_text(
                order_text,
                call.message.chat.id,
                call.message.id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
            admin_user_id = db.get_admin_user_id()
            if admin_user_id:
                products_details = get_order_products_details(order["products"])
                products_text = "\n\n".join(products_details)

                cancel_order_text = content_cfg.get_order_admin_new_cancel_user_text(
                    order_number,
                    formatted_created_at,
                    order["tg_username"],
                    order["tg_full_name"],
                    order["full_name"],
                    order["phone"],
                    delivery_company,
                    delivery_point_address,
                    products_text,
                    total_with_delivery,
                    delivery_price,
                    delivery_info
                )
                
                bot.send_message(
                    admin_user_id,
                    cancel_order_text,
                    parse_mode="Markdown"
                )
        else:
            bot.answer_callback_query(
                call.id, 
                content_cfg.get_order_user_cancel_error_message(order_number)
            )
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("copy_to_cart_"))
    @err_handler
    def copy_to_cart(call):
        logger.debug("copy_to_cart CALL")
        
        order_id = (call.data.split("_")[3])
        tg_user_id = call.from_user.id
        
        result = db.copy_order_to_cart(tg_user_id, order_id)
        
        if result['error']:
            bot.answer_callback_query(
                call.id,
                content_cfg.order.user.all.control_show.current.copy_to_cart.error.message,
                show_alert=False
            )
            return
        
        added = result["added"]
        skipped = result["skipped"]
        
        response = []
        if added:
            response.append(content_cfg.order_user_all_control_show_current_copy_to_cart_added_message(added))
        if skipped:
            response.append(content_cfg.order_user_all_control_show_current_copy_to_cart_skipped_message(skipped))
            
        if not response:
            response.append(content_cfg.order.user.all.control_show.current.copy_to_cart.no_products)
            
        bot.answer_callback_query(
            call.id, 
            "\n".join(response),
            show_alert=False
        )
        