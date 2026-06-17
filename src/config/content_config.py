from typing import List
import json
from pathlib import Path
from logging import Logger

from psycopg2.extras import NumericRange
from easydict import EasyDict as edict

class ContentConfig:
    def __init__(self, config_path: str, logger: Logger):
        self.config_path = Path(config_path)
        self.logger = logger
        self._data = None
        self._load()
        
    def _load(self):
        if not self.config_path.exists():
            self.logger.error(f"Content config file not found at path: {self.config_path.name}")
            return
        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        self._data = self._process_dict(raw_data)
        
    def _process_dict(self, obj):
        if isinstance(obj, dict):
            processed = {}
            for k, v in obj.items():
                processed[k] = self._process_dict(v)
            return edict(processed)
        elif isinstance(obj, list):
            if all(isinstance(item, str) for item in obj):
                return "".join(obj)
            else:
                return [self._process_dict(item) for item in obj]
        else:
            return obj
        
    def reload(self):
        self._load()
        
    def __getattr__(self, name):
        if name.startswith('_'):
            return super().__getattr__(name)
        return getattr(self._data, name)
    
    # cart
    
    def get_cart_product_text(
        self,
        name: str,
        article_number: int,
        price: float,
        quantity: int,
        product_total: float
    ):
        return self.cart.product.text.format(
            name=name.capitalize(),
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            product_total=round(product_total, 2)
        )
    
    
    def get_cart_total_text(self, total: float):
        return self.cart.total.text.format(total=round(total, 2))
    
    
    def get_cart_product_added_message(self, quantity: int):
        return self.cart.product.added.message.format(quantity=quantity)
    
    
    def get_cart_edit_product_quantity_message(self, quantity: int):
        return self.cart.edit.product.quantity.message.format(quantity=quantity)
    
    # catalog
    
    
    def get_catalog_control_show_text(
        self,
        category: str,
        number_products: int
    ):
        return self.catalog.control_show.text.format(
            category_text=self.catalog.category2text_map.get(category),
            number_products=number_products
        )
        
    
    def get_catalog_admin_edit_images_current_message(self, image_number: int):
        return self.catalog.admin.edit.images.current.message.format(image_number=image_number)
    
    
    def get_catalog_admin_edit_images_current_delete_message(self, image_number: int):
        return self.catalog.admin.edit.images.current.delete.message.format(image_number=image_number)
    
    
    def get_catalog_admin_edit_images_current_success_message(self, image_number: int):
        return self.catalog.admin.edit.images.current.success.message.format(image_number=image_number)
        
    # common
    
    
    def get_common_welcome_message(self, full_name: str) -> str:
        return self.common.welcome.message.format(full_name=full_name)
    
    
    def get_common_admin_contacts_text(
        self, 
        tg_username: str,
        tg_full_name: str,
        full_name: str, 
        phone: str,
        timezone: str
    ):
        return self.common.admin.contacts.text.format(
            tg_username=tg_username, 
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            timezone=timezone
        )
    
    
    def get_common_user_profile_text(
        self, 
        full_name: str, 
        phone: str,
        timezone: str,
        delivery_company: str,
        delivery_point_address
    ):
        return self.common.user.profile.text.format(
            full_name=full_name if full_name else "-",
            phone=phone if phone else "-",
            timezone=timezone if timezone else "-",
            delivery_company=delivery_company if delivery_company else "-",
            delivery_point_address=delivery_point_address if delivery_point_address else "-"
        )
        
    
    def get_common_admin_profile_text(
        self,
        full_name: str,
        phone: str,
        timezone: str
    ):
        return self.common.admin.profile.text.format(
            full_name=full_name,
            phone=phone,
            timezone=timezone
        )
    
     
    def get_common_profile_edit_delivery_company_question_message(self, delivery_company: str):
        return self.common.profile.edit.delivery_company.question.message.format(delivery_company=delivery_company)
    
    
    def get_common_profile_edit_delivery_point_address_question_message(self, delivery_point_address: str):
        return self.common.profile.edit.delivery_point_address.question.message.format(delivery_point_address=delivery_point_address)
    
    
    def get_common_admin_user_data_all_control_show_text(self, number_users: int):
        return self.common.admin.user_data.all.control_show.text.format(number_users=number_users)
    
    
    def get_common_admin_user_data_all_control_show_current_text(
        self,
        tg_username: str,
        tg_full_name: str,
        full_name: str,
        phone: str,
        timezone: str,
        delivery_company: str,
        delivery_point_address: str,
        created_at: str
    ):
        return self.common.admin.user_data.all.control_show.current.text.format(
            tg_username=tg_username,
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            timezone=timezone,
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            created_at=created_at
        )
    
    # product
    
    
    def get_product_text(self, name: str, article_number: int, price: float):
        return self.product.text.format(name=name.capitalize(), article_number=article_number, price=round(float(price), 2))
    
    
    def get_product_details_text(
        self,
        name: str,
        article_number: int,
        description: str,
        price: float,
        materials: str,
        category: str,
        production_time: NumericRange,
        prod_limit: int,
        production_time_units: str
    ):
        production_time_text = ""
        if production_time:
            if production_time.upper-1 - production_time.lower == 0:
                production_time_text = f"{production_time.upper-1}"
            else:
                production_time_text = f"{production_time.lower}-{production_time.upper-1}"
        
        return self.product.details.text.format(
            name=name.capitalize(),
            article_number=article_number,
            description=description,
            price=round(float(price), 2),
            materials=materials,
            category=category if category else "",
            production_time_text=production_time_text,
            prod_limit=prod_limit,
            production_time_units=production_time_units
        )
        
    # order
    
    
    def get_order_start_message(self, remaining: int):
        return self.order.start.message.format(remaining=remaining)

    
    def get_order_place_empty_fields_message(self, fields: List[str]):
        translated_fields = []
        for field in fields:
            translated_field = self.common.profile.eng2ru_field_map.get(field)
            translated_fields.append(translated_field)
        fields_string = ", ".join(translated_fields)
        return self.order.place.empty_fields.message.format(fields_string=fields_string)
    
    
    def get_order_place_transfer_to_admin_message(self, order_number: int):
        return self.order.place.transfer_to_admin.message.format(order_number=order_number)
    
    
    def get_order_admin_product_details_text(
        self,
        name: str,
        article_number: int,
        price: float,
        quantity: int,
        product_total: float,
        category: str,
        materials: str,
        production_time: NumericRange,
        production_time_units: str
    ):
        if production_time.upper-1 - production_time.lower == 0:
            production_time_text = f"{production_time.upper-1}"
        else:
            production_time_text = f"{production_time.lower}-{production_time.upper-1}"
        
        return self.order.admin.product.details.text.format(
            name=name.capitalize(),
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            product_total=round(float(product_total), 2),
            materials=materials,
            category=category,
            production_time_text=production_time_text,
            production_time_units=production_time_units
        )
        
    
    def get_order_admin_new_text(
        self,
        order_number: int,
        created_at: str,
        tg_username: str,
        tg_full_name: str,
        full_name: str,
        phone: str,
        delivery_company: str,
        delivery_point_address: str,
        products_text: str,
        total_price: float,
        delivery_price: float
    ):
        return self.order.admin.new.text.format(
            order_number=order_number,
            created_at=created_at,
            tg_username=tg_username,
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            products_text=products_text,
            total_price=round(float(total_price), 2),
            delivery_price=round(float(delivery_price), 2)
        )
    
    
    def get_order_admin_new_cancel_success_message(self, order_number: str):
        return self.order.admin.new.cancel.success.message.format(order_number=order_number)
    
    
    def get_order_admin_new_cancel_reason_message(
        self, 
        order_number: int,
        created_at: str,
        cancel_reason: str,
        order_text: str
    ):
        return self.order.admin.new.cancel.reason.message.format(
            order_number=order_number,
            created_at=created_at,
            cancel_reason=cancel_reason,
            order_text=order_text
        )
    
    
    def get_order_admin_new_cancel_error_message(self, order_number: str):
        return self.order.admin.new.cancel.error.message.format(order_number=order_number)
    
    
    def get_order_user_cancel_success_message(self, order_number: str):
        return self.order.user.cancel.success.message.format(order_number=order_number)
    
    
    def get_order_user_cancel_error_message(self, order_number: str):
        return self.order.user.cancel.error.message.format(order_number=order_number)
    
    
    def get_order_user_send_for_payment_text(
        self,
        order_number: int,
        created_at: str,
        status: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        admin_phone: str
    ):
        return self.order.user.send.for_payment.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            admin_phone=admin_phone
        )
        
    
    def get_order_admin_new_send_for_payment_success_message(self, order_number: int):
        return self.order.admin.new.send.for_payment.success.message.format(order_number=order_number)
    
    
    def get_order_user_send_receipt_text(
        self,
        order_number: int,
        created_at: str,
        status: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        delivery_info: str
    ):
        return self.order.user.send.receipt.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            delivery_info=delivery_info
        )
        
    
    def get_order_admin_new_send_receipt_success_message(self, order_number: int):
        return self.order.admin.new.send.receipt.success.message.format(order_number=order_number)
    
    
    def get_order_user_all_control_show_text(self, number_orders: int):
        return self.order.user.all.control_show.text.format(number_orders=number_orders)
    
    
    def get_order_user_all_control_show_current_text(
        self,
        order_number: int,
        created_at: str,
        status: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        delivery_company: str,
        delivery_point_address: str,
        delivery_info: str
    ):
        delivery_info_text = ""
        if delivery_info is not None:
            delivery_info_text = self.order.user.all.control_show.current.delivery_info.text.format(delivery_info=delivery_info)
        
        return self.order.user.all.control_show.current.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            delivery_info_text=delivery_info_text
        )
    
    
    def get_order_admin_new_cancel_user_text(
        self,
        order_number: int,
        created_at: str,
        tg_username: str,
        tg_full_name: str,
        full_name: str,
        phone: str,
        delivery_company: str,
        delivery_point_address: str,
        products_text: str,
        total_price: float,
        delivery_price: float,
        delivery_info: str = None
    ):
        delivery_info_text = ""
        if delivery_info is not None:
            delivery_info_text = self.order.admin.new.delivery_info.text.format(delivery_info=delivery_info)
            
        return self.order.admin.new.cancel.user.text.format(
            order_number=order_number,
            created_at=created_at,
            tg_username=tg_username,
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            products_text=products_text,
            total_price=round(float(total_price), 2),
            delivery_price=round(float(delivery_price), 2),
            delivery_info_text=delivery_info_text
        )
    
    
    def get_order_user_cancel_success_message(self, order_number: int):
        return self.order.user.cancel.success.message.format(order_number=order_number)
    
    
    def get_order_user_cancel_error_message(self, order_number: int):
        return self.order.user.cancel.error.message.format(order_number=order_number)
    
    
    def get_order_user_all_control_show_current_copy_to_cart_added_message(self, added: List[str]):
        added_text = ', '.join(map(str, added))
        return self.order.user.all.control_show.current.copy_to_cart.added.message.format(added_text=added_text)
    
    
    def get_order_user_all_control_show_current_copy_to_cart_skipped_message(self, skipped: List[str]):
        skipped_text = ', '.join(map(str, skipped))
        return self.order.user.all.control_show.current.copy_to_cart.skipped.message.format(skipped_text=skipped_text)
    
    
    def get_order_admin_all_control_show_text(self, number_orders: int):
        return self.order.admin.all.control_show.text.format(number_orders=number_orders)
    
    
    def get_order_admin_all_control_show_current_text(
        self,
        order_number: int,
        created_at: str,
        status: str,
        tg_username: str,
        tg_full_name: str,
        full_name: str,
        phone: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        delivery_company: str,
        delivery_point_address: str,
        delivery_info: str
    ):
        delivery_info_text = ""
        if delivery_info is not None:
            delivery_info_text = self.order.admin.all.control_show.current.delivery_info.text.format(delivery_info=delivery_info)
        
        return self.order.admin.all.control_show.current.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            tg_username=tg_username,
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            delivery_info_text=delivery_info_text
        )
    
    # statistics
    
    
    def get_statistics_admin_top_product_text(
        self,
        place: int,
        name: str,
        article_number: int,
        total_quantity: int
    ):
        return self.statistics.admin.top_product.text.format(
            place=place,
            name=name.capitalize(),
            article_number=article_number,
            total_quantity=total_quantity
        )
            
    
    def get_statistics_admin_text(
        self,
        month_name: str,
        year: str,
        order_count: int,
        total_revenue: float,
        new_users_count: int,
        active_users_count: int,
        top_products_text: str
    ):
        return self.statistics.admin.text.format(
            month_name=month_name,
            year=year,
            order_count=order_count,
            total_revenue=round(float(total_revenue), 2),
            new_users_count=new_users_count,
            active_users_count=active_users_count,
            top_products_text=top_products_text
        )
          
      
    def get_statistics_admin_histogram_completed_orders_year_header_text(self, year: str):
        return self.statistics.admin.histogram.completed_orders.year.header.text.format(year=year)
    
    
    def get_statistics_admin_histogram_revenue_year_header_text(self, year: str):
        return self.statistics.admin.histogram.revenue.year.header.text.format(year=year)
    
    
    def get_statistics_admin_histogram_new_users_year_header_text(self, year: str):
        return self.statistics.admin.histogram.new_users.year.header.text.format(year=year)
    
    # settings 
    
    def get_settings_admin_content_config_parsing_error_message(self, e: json.JSONDecodeError):
        return self.settings.admin.content.config.parsing_error.message.format(e=e)