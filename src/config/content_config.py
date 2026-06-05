from typing import Dict

from psycopg2.extras import NumericRange
from easydict import EasyDict as edict

class ContentConfig:
    
    cart: edict = edict({
        "user": {
            "header_text": "🛒 *Ваша корзина:*\n\n"
        },
        "product": {
            "text": (
                "• *{name}*\n"
                "  Nd\\_{article_number:05d}\n"
                "  Цена: {price} ₽ x {quantity} = {item_total} ₽\n\n"
            ),
            "added": {
                "message": "✅ Товар добавлен в корзину! Теперь в корзине: {quantity} шт."
            },
        },
        "total": {
            "text": "💰 *Итого: {total} ₽*"
        },
        "message": "🛒 Корзина",
        "edit": {
            "message": "✏️ Редактировать корзину",
            "text": (
                "✏️ Режим редактирования корзины\n"
                "Используйте кнопки внизу для навигации."
            ),
            "product": {
                "decrease": {
                    "message": ("➖")
                },
                "quantity": {
                    "message": ("{quantity}")
                },
                "increase": {
                    "message": ("➕")
                },
                "delete": {
                    "message": ("🗑 Удалить")
                },
                "not_found": {
                    "message": "❌ Товар не найден"
                },
                "error": {
                    "message": "⚠️ Возникла ошибка при редактировании товара"
                },
                "prod_limit_exceeded": {
                    "message": "⚠️ Превышен лимит данного товара. Для добавления большего числа обратитесь к Nadine."
                }
            }
        },
        "clear": {
            "message": "🔄 Очистить корзину"
        },
        "is_empty": {
            "message": "Ваша корзина пуста"
        }, 
        "add_error_user_not_found": {
            "message": "❌ Ошибка добавления. Пользователь не найден."
        },
        "session_not_found": {
            "message": "⚠️ Сессия не найдена. Начните заново из корзины"
        },
        "main_menu": {
            "message": "Главное меню:"
        },
        "completely_cleared": {
            "message": "✅ Корзина полностью очищена"
        },
        "is_empty_or_failed_to_clear": {
            "message": "❌ Корзина уже пуста или не удалось очистить корзину"
        },
        "control_edit": {
            "next": {"message": "➡️ Следующий товар в корзине"},
            "next5": {"message": "5️⃣ Следующие 5 товаров в корзине"},
            "stop": {"message": "⏹ Остановить редактирование"},
            "go_back_to_main_menu": {"message": "◀️ Вернуться в главное меню"},
            "no_other_products": {
                "message": "Нет других товаров в корзине"
            }
        }
    })
    
    catalog: edict = edict({
        "category_menu": {
            "header_text": "🎁 *Каталог товаров*\n\nВыберите категорию:",
        },
        "menu": {
            "categories": {
                "all_products": {"message": "Все товары"},
                "bracelets": {"message": "Браслеты"},
                "earrings": {"message": "Серьги"},
                "necklaces": {"message": "Ожерелья"},
                "brooches": {"message": "Броши"},
                "pendants": {"message": "Кулоны"},
                "chains": {"message": "Цепочки"},
                "rings": {"message": "Кольца"}
            }
        },
        "message": "🛍️ Каталог товаров",
        "is_empty": {
            "message": "Каталог пуст"
        },
        "session_not_found": {
            "message": "⚠️ Сессия не найдена. Начните заново из каталога"
        },
        "all_displayed": {
            "message": "✅ Все товары уже показаны"
        },
        "main_menu": {
            "message": "Главное меню:"
        },
        "control_show": {
            "text": (
                "{category_text}\n"
                "Всего товаров: {number_products}\n"
                "Используйте кнопки внизу для навигации."
            ),
            "next": {"message": "➡️ Следующий товар"},
            "next5": {"message": "5️⃣ Следующие 5"},
            "stop": {"message": "⏹ Остановить показ"},
            "go_back_to_main_menu": {"message": "◀️ В главное меню"}
        },
        "eng2ru_category_map": {
            "bracelets": "браслеты",
            "earrings": "серьги",
            "necklaces": "ожерелья",
            "brooches": "броши",
            "pendants": "кулоны",
            "chains": "цепочки",
            "rings": "кольца",
        },
        "category2text_map": {
            "all": "📋 *Все товары*",
            "bracelets": "📿 *Браслеты*",
            "earrings": "💎 *Серьги*",
            "necklaces": "💫 *Ожерелья*",
            "brooches": "🦋 *Броши*",
            "pendants": "🔮 *Кулоны*",
            "chains": "⛓️ *Цепочки*",
            "rings": "💍 *Кольца*"
        }
    })
    
    common: edict = edict({
        "admin": {
            "contacts": {
                "text": (
                    "📞 *Контакты Nadine:*\n\n"
                    "👤 Telegram: [@{tg_username}](https://t.me/{tg_username})\n"
                    "📱 Телефон: [{phone}](tel:{phone})"
                ),
                "message": "📞 Связаться с Nadine"
            },
            "about": {
                "text": (
                    "👤 *О Nadine:*\n\n"
                    "..."
                ),
                "message": "ℹ️ О Nadine"
            }
        },
        "user": {
            "personal_data": {
                "message": "👤 Личные данные"
            },
            "orders": {
                "message": "📦 Мои заказы"
            },
            "profile": {
                "text": (
                    "👤 *Личные данные*\n\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📞 *Телефон:* {phone}\n"
                    "🚚 *Служба доставки:* {delivery_company}\n"
                    "📍 *Адрес пункта выдачи:* {delivery_point_address}" 
                ),
                "edit": {
                    "full_name": {
                        "message": "✏️ Изменить ФИО",
                        "text": "Введите ФИО:",
                        "update": {
                            "message": "✅ ФИО было успешно обновлено."
                        }
                    },
                    "phone": {
                        "message": "✏️ Изменить телефон",
                        "text": "Введите номер телефона:",
                        "update": {
                            "message": "✅ Номер телефона был успешно обновлён."
                        }
                    },
                    "delivery_company": {
                        "message": "✏️ Изменить службу доставки",
                        "text": "Введите название службы доставки (например, Яндекс Доставка):",
                        "update": {
                            "message": "✅ Служба доставки была успешно обновлена."
                        }
                    },
                    "delivery_point_address": {
                        "message": "✏️ Изменить адрес пункта выдачи",
                        "text": "Введите адрес пункта выдачи (например, г. Москва, Долгоруковская улица, 40):",
                        "update": {
                            "message": "✅ Адрес пункта выдачи был успешно обновлён."
                        }
                    },
                    "empty_value": {
                        "message": "❌ Значение не может быть пустым."
                    },
                    "wrong_phone_format": {
                        "message": "❌ Неверный формат телефона. Введите номер например в таком формате +7.........."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления. Попробуйте позже."
                    }
                }
            }
        },
        "welcome": {
            "message": "Привет, {name}!\n\nВыбери действие из меню ниже:"
        },
        "error": {
            "message": "⚠️ Непредвиденная ошибка. Повторите позже."
        }
    })
    
    product: edict = edict({
        "text": (
            "🔖 *{name}*\n\n"
            "✨ *Nd_{article_number:05d}*\n\n"
            "💰 *Цена:* {price} ₽\n"
        ),
        "details": {
            "text": (
                "🔖 *{name}*\n\n"
                "✨ *Nd_{article_number:05d}*\n\n"
                "📝 *Описание:*\n{description}\n"
                "💰 *Цена:* {price} ₽\n"
                "⛓️ *Материалы:* {materials}\n"
                "🏷️ *Категория:* {category}\n"
                "🕒 *Время изготовления:* {production_time} {production_time_units}\n"
                "📦 *Максимум товаров в одном заказе:* {prod_limit}\n\n"
                "Выберите действие:"
            ),
            "message": "📋 Подробнее"
        },
        "add_to_cart": {
            "message": "🛒 Добавить в корзину"
        },
        "not_found": {
            "message": "❌ Товар не найден"
        },
        "production_time": {
            "unit_1": "день",
            "unit_234": "дня",
            "unit_other": "дней"
        }
    })
    
    order: edict = edict({
        "place": {
            "message": "💳 Оформить заказ",
            "session_not_found": {
                "message": "⚠️ Сессия не найдена. Начните новый заказ"
            }
        },
        "limit_per_day": 3,
        "exceed_limit": {
            "message": "⚠️ Вы превысили лимит заказов (3 в день)."
        },
        "start": {
            "message": "Начинаем оформление заказа. На сегодня заказов доступно: {remaining}"
        },
    })
    
    db: edict = edict({
        "error": {
            "message": "⚠️ Ошибка базы данных. Попробуйте позже."
        }
    })

    
    # cart
    @classmethod
    def get_cart_product_text(
        cls,
        name: str,
        article_number: int,
        price: float,
        quantity: int,
        item_total: float
    ):
        return cls.cart.product.text.format(
            name=name.capitalize(),
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            item_total=round(item_total, 2)
        )
    
    @classmethod
    def get_cart_total_text(cls, total: float):
        return cls.cart.total.text.format(total=round(total, 2))
    
    def get_cart_product_added_message(cls, quantity: int):
        return cls.cart.product.added.message.format(quantity=quantity)
    
    def get_cart_edit_product_quantity_message(cls, quantity: int):
        return cls.cart.edit.product.quantity.message.format(quantity=quantity)
    
    # catalog
    
    def get_catalog_control_show_text(
        cls,
        category: str,
        number_products: int
    ):
        return cls.catalog.control_show.text.format(
            category_text=cls.catalog.category2text_map.get(category),
            number_products=number_products
        )
    
    # common
    
    @classmethod
    def get_common_welcome_message(cls, name: str) -> str:
        return cls.common.welcome.message.format(name=name)
    
    def get_common_admin_contacts_text(cls, tg_username: str, phone: str):
        return cls.common.admin.contacts.text.format(tg_username=tg_username, phone=phone)
    
    def get_common_user_profile_text(
        cls, 
        full_name: str, 
        phone: str,
        delivery_company: str,
        delivery_point_address
    ):
        return cls.common.user.profile.text.format(
            full_name=full_name if full_name else "-",
            phone=phone if phone else "-",
            delivery_company=delivery_company if delivery_company else "-",
            delivery_point_address=delivery_point_address if delivery_point_address else "-"
        )
    
    # product
    
    @classmethod
    def get_product_text(cls, name: str, article_number: int, price: float):
        return cls.product.text.format(name=name.capitalize(), article_number=article_number, price=round(float(price), 2))
    
    @classmethod
    def get_product_details_text(
        cls,
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
        return cls.product.details.text.format(
            name=name.capitalize(),
            article_number=article_number,
            description=description,
            price=round(float(price), 2),
            materials=materials,
            category=category,
            production_time=f"{production_time.lower}-{production_time.upper}",
            prod_limit=prod_limit,
            production_time_units=production_time_units
        )
        
    # order
    
    def get_order_start_message(cls, remaining: int):
        return cls.order.start.message.format(remaining=remaining)