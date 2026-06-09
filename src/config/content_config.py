from typing import List

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
                "  Цена: {price} ₽ x {quantity} = {product_total} ₽"
            ),
            "added": {
                "message": "✅ Товар добавлен в корзину! Теперь в корзине: {quantity} шт."
            },
        },
        "total": {
            "text": "\n\n💰 *Итого:* {total} ₽"
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
                "Всего видов товаров: {number_products}\n"
                "Используйте кнопки внизу для навигации."
            ),
            "next": {"message": "➡️ Следующий товар"},
            "next5": {"message": "5️⃣ Следующие 5 товаров"},
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
            "profile": {
                "text": (
                    "👤 *Личные данные*\n\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📱 *Телефон:* {phone}\n"
                    "🌐 *Часовой пояс:* {timezone}\n"
                    "🚚 *Служба доставки:* {delivery_company}\n"
                    "📍 *Адрес пункта выдачи:* {delivery_point_address}" 
                ),
                "eng2ru_field_map": {
                    "full_name": "ФИО",
                    "phone": "Телефон",
                    "delivery_company": "Служба доставки",
                    "delivery_point_address": "Адрес пункта выдачи"
                },
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
                        },
                        "wrong_format": {
                            "message": "❌ Неверный формат телефона. Введите номер например в таком формате +7.........."
                        },
                    },
                    "timezone": {
                        "message": "✏️ Изменить часовой пояс",
                        "text": "Введите ваш часовой пояс в формате ±число, где число – смещение от UTC (целое число, например, +3, -5, 0):",
                        "update": {
                            "message": "✅ Часовой пояс был успешно обновлён."
                        },
                        "wrong_format": {
                            "message": "❌ Неверный формат. Введите, например: +3, или 2, или -5"
                        },
                        "offset_exceed": {
                            "message": "❌ Смещение не может превышать ±12 часов."
                        }
                    },
                    "delivery_company": {
                        "message": "✏️ Изменить службу доставки",
                        "text": "Введите название службы доставки (например, Яндекс Доставка):",
                        "update": {
                            "message": "✅ Служба доставки была успешно обновлена."
                        },
                        "question": {
                            "message": (
                                "У вас уже указана служба доставки: {delivery_company}\n"
                                "Вы хотели бы изменить её?"
                            ),
                        }
                    },
                    "delivery_point_address": {
                        "message": "✏️ Изменить адрес пункта выдачи",
                        "text": "Введите адрес пункта выдачи (например, г. Москва, Долгоруковская улица, 40):",
                        "update": {
                            "message": "✅ Адрес пункта выдачи был успешно обновлён."
                        },
                        "question": {
                            "message": (
                                "У вас уже указан адрес пункта выдачи: {delivery_point_address}\n"
                                "Вы хотели бы изменить его?"
                            ),
                        }
                    },
                    "yes": {
                        "message": "Да"
                    },
                    "no": {
                        "message": "Нет"
                    },
                    "empty_value": {
                        "message": "❌ Значение не может быть пустым."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления. Попробуйте позже."
                    }
                }
            }
        },
        "welcome": {
            "message": "Привет, {full_name}!\n\nВыбери действие из меню ниже:"
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
            "final": {
                "header_text": "📦 *Ваш заказ:*\n\n",
                "message": "💳 Оформить"
            },
            "empty_fields": {
                "message": (
                    "У вас не заполнены обязательные поля: {fields_string}.\n"
                    "Пожалуйста начните оформление заказа заново."
                )
            },
            "error": {
                "message": "❌ Ошибка при создании заказа. Попробуйте позже."
            },
            "transfer_to_admin": {
                "message": "✅ Заказ №{order_number} оформлен и передан Nadine. Ожидайте подтверждения."
            }
        },
        "limit_per_day": 50,
        "exceed_limit": {
            "message": "⚠️ Вы превысили лимит заказов (3 в день)."
        },
        "start": {
            "message": "Начинаем оформление заказа. На сегодня заказов доступно: {remaining}"
        },
        "session_not_found": {
            "message": "⚠️ Сессия не найдена. Начните заново оформлять заказ"
        },
        "admin": {
            "product": {
                "details": {
                    "text": (
                        "🔖 *{name}*\n"
                        "✨ *Nd_{article_number:05d}*\n"
                        "💰 *Цена:* {price} ₽ x {quantity} = {product_total} ₽\n"
                        "⛓️ *Материалы:* {materials}\n"
                        "🏷️ *Категория:* {category}\n"
                        "🕒 *Время изготовления:* {production_time} {production_time_units}"
                    )
                }
            },
            "new": {
                "text": (
                    "🆕 *НОВЫЙ ЗАКАЗ №{order_number}*\n\n"
                    "📅 *Дата и время оформления заказа:* {created_at}\n\n"
                    "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                    "📛 *Имя в Telegram:* {tg_full_name}\n"
                    "👤 *ФИО:* {full_name}\n"
                    "📱 *Телефон*: [{phone}](tel:{phone})\n"
                    "🚚 *Служба доставки:* {delivery_company}\n"
                    "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                    "📦 *Состав заказа:*\n\n{products_text}\n\n"
                    "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                    "💰 *Общая сумма:* {total_price} ₽\n"
                ),
                "set_delivery_price": {
                    "message": "💰 Ввести стоимость доставки",
                    "text": "Введите стоимость доставки:",
                    "incorrect_value": {
                        "message": "❌ Заданное значение некорректно."
                    },
                    "success": {
                        "message": "✅ Стоимость доставки была успешно обновлена."
                    },
                    "error": {
                        "message": "❌ Ошибка при установке стоимости доставки. Попробуйте позже."
                    }
                },
                "delivery_info": {
                    "text": "🚛 *Информация по доставке:\n*{delivery_info}"
                },
                "cancel": {
                    "message": "❌ Отменить заказ",
                    "success": {
                        "message": "✅ Заказ №{order_number} отменён."
                    },
                    "reason": {
                        "text": "Введите причину отмены заказа для пользователя:",
                        "message": (
                            "⚠️ К сожалению ваш заказ №{order_number} был отменён Nadine.\n\n"
                            "📅 *Дата и время оформления заказа:* {created_at}\n\n"
                            "Причина: {cancel_reason}\n\n"
                            "{order_text}\n"
                        )
                    },
                    "error": {
                        "message": "❌ Не удалось отменить заказ №{order_number}"
                    },
                    "user": {
                        "text": (
                            "⚠️ *ОТМЕНЁН ЗАКАЗ №{order_number}*\n\n"
                            "📅 *Дата и время оформления заказа:* {created_at}\n\n"
                            "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                            "📛 *Имя в Telegram:* {tg_full_name}\n"
                            "👤 *ФИО:* {full_name}\n"
                            "📱 *Телефон*: [{phone}](tel:{phone})\n"
                            "🚚 *Служба доставки:* {delivery_company}\n"
                            "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                            "📦 *Состав заказа:*\n\n{products_text}\n\n"
                            "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                            "{delivery_info_text}\n"
                            "💰 *Общая сумма:* {total_price} ₽\n"
                        )
                    }
                },
                "send": {
                    "for_payment": {
                        "message": "💳 Отправить на оплату",
                        "text": "Отправьте файл счёта на оплату (документ или изображение):",
                        "success": {
                            "message": "✅ Инвойс для заказа №{order_number} отправлен пользователю."
                        }
                    },
                    "receipt": {
                        "message": "🧾 Отправить чек",
                        "file": {
                            "text": "Отправьте файл чека (документ или изображение):",
                        },
                        "delivery_info": {
                            "text": "Введите данные о доставке:",
                            "is_empty": {
                                "message": "❌ Вы не ввели данные о доставке."
                            },
                            "failed_to_set": {
                                "message": "❌ Не удалось сохранить данные о доставке. Попробуйте позже."
                            }
                        },
                        "success": {
                            "message": "✅ Чек для заказа №{order_number} отправлен пользователю."
                        }
                    },
                    "incorrect_file_format": {
                        "message": "❌ Неверный формат файла."
                    }
                },
                "user_not_found": {
                    "message": "❌ Пользователь не найден."
                }
            }
        },
        "user": {
            "message": "📦 Мои заказы",
            "cancel": {
                "message": "❌ Отменить заказ",
                "success": {
                    "message": "✅ Заказ №{order_number} отменён."
                },
                "error": {
                    "message": "❌ Не удалось отменить заказ №{order_number}"
                }
            },
            "send": {
                "for_payment": {
                    "text": (
                        "✅ *Благодарю вас за оформление заказа №{order_number}*\n\n"
                        "📅 *Дата и время оформления заказа:* {created_at}\n"
                        "📌 *Статус заказа:* {status}\n\n"
                        "📦 *Ваш заказ:*\n{products_text}\n\n"
                        "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                        "💰 *Общая сумма:* {total_with_delivery} ₽\n\n"
                        "💳 Пожалуйста, произведите оплату по номеру телефона: [{admin_phone}](tel:{admin_phone})\n"
                        "После оплаты ожидайте подтверждения Nadine. Как только чек будет проверен, вы получите уведомление и данные о доставке.\n\n"
                        "🙏 Спасибо за заказ!"
                    )
                },
                "receipt": {
                    "text": (
                        "🧾 *Чек и информация по доставке для заказа №{order_number}*\n\n"
                        "📅 *Дата и время оформления заказа:* {created_at}\n"
                        "📌 *Статус заказа:* {status}\n\n"
                        "📦 *Ваш заказ:*\n{products_text}\n\n"
                        "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                        "💰 *Общая сумма:* {total_with_delivery} ₽\n\n"
                        "🚛 *Информация по доставке:\n*{delivery_info}\n"
                    )
                }
            },
            "all": {
                "is_empty": {
                    "message": "У вас нет заказов"
                },
                "control_show": {
                    "text": (
                        "Всего заказов: {number_orders}\n"
                        "Используйте кнопки внизу для навигации."
                    ),
                    "next": {"message": "➡️ Следующий заказ"},
                    "next5": {"message": "5️⃣ Следующие 5 заказов"},
                    "go_back_to_main_menu": {"message": "◀️ Перейти в главное меню"},
                    "session_not_found": {
                        "message": "⚠️ Сессия не найдена. Нажмите '📦 Мои заказы'"
                    },
                    "current": {
                        "text": (
                            "✅ *Заказ №{order_number}*\n\n"
                            "📅 *Дата и время оформления заказа:* {created_at}\n"
                            "📌 *Статус заказа:* {status}\n\n"
                            "📦 *Ваш заказ:*\n{products_text}\n\n"
                            "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                            "💰 *Общая сумма:* {total_with_delivery} ₽\n\n"
                            "🚚 *Служба доставки:* {delivery_company}\n"
                            "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                            "🚛 *Информация по доставке:\n*{delivery_info}\n"
                        ),
                        "cancel": {
                            "message": "❌ Отменить заказ"
                        },
                        "copy_to_cart": {
                            "message": "🗂️ Скопировать товары в корзину"
                        }
                    }
                },
                "displayed": {
                    "message": "✅ Все заказы уже показаны"
                }
            },
            "main_menu": {
                "message": "Главное меню:"
            }
        },
        "status": {
            "review": {
                "message": "на рассмотрении"
            },
            "for_payment": {
                "text": "отправлен на оплату"
            },
            "completed": {
                "text": "выполнен и отправлен"
            },
            "update_error": {
                "message": "❌ Не удалось обновить статус заказа."
            }
        }
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
        product_total: float
    ):
        return cls.cart.product.text.format(
            name=name.capitalize(),
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            product_total=round(product_total, 2)
        )
    
    @classmethod
    def get_cart_total_text(cls, total: float):
        return cls.cart.total.text.format(total=round(total, 2))
    
    @classmethod
    def get_cart_product_added_message(cls, quantity: int):
        return cls.cart.product.added.message.format(quantity=quantity)
    
    @classmethod
    def get_cart_edit_product_quantity_message(cls, quantity: int):
        return cls.cart.edit.product.quantity.message.format(quantity=quantity)
    
    # catalog
    
    @classmethod
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
    def get_common_welcome_message(cls, full_name: str) -> str:
        return cls.common.welcome.message.format(full_name=full_name)
    
    @classmethod
    def get_common_admin_contacts_text(cls, tg_username: str, phone: str):
        return cls.common.admin.contacts.text.format(tg_username=tg_username, phone=phone)
    
    @classmethod
    def get_common_user_profile_text(
        cls, 
        full_name: str, 
        phone: str,
        timezone: str,
        delivery_company: str,
        delivery_point_address
    ):
        return cls.common.user.profile.text.format(
            full_name=full_name if full_name else "-",
            phone=phone if phone else "-",
            timezone=timezone if timezone else "-",
            delivery_company=delivery_company if delivery_company else "-",
            delivery_point_address=delivery_point_address if delivery_point_address else "-"
        )
    
    @classmethod 
    def get_common_user_profile_edit_delivery_company_question_message(cls, delivery_company: str):
        return cls.common.user.profile.edit.delivery_company.question.message.format(delivery_company=delivery_company)
    
    @classmethod
    def get_common_user_profile_edit_delivery_point_address_question_message(cls, delivery_point_address: str):
        return cls.common.user.profile.edit.delivery_point_address.question.message.format(delivery_point_address=delivery_point_address)
    
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
    
    @classmethod
    def get_order_start_message(cls, remaining: int):
        return cls.order.start.message.format(remaining=remaining)

    @classmethod
    def get_order_place_empty_fields_message(cls, fields: List[str]):
        translated_fields = []
        for field in fields:
            translated_field = cls.common.user.profile.eng2ru_field_map.get(field)
            translated_fields.append(translated_field)
        fields_string = ", ".join(translated_fields)
        return cls.order.place.empty_fields.message.format(fields_string=fields_string)
    
    @classmethod
    def get_order_place_transfer_to_admin_message(cls, order_number: int):
        return cls.order.place.transfer_to_admin.message.format(order_number=order_number)
    
    @classmethod
    def get_order_admin_product_details_text(
        cls,
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
        return cls.order.admin.product.details.text.format(
            name=name.capitalize(),
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            product_total=round(float(product_total), 2),
            materials=materials,
            category=category,
            production_time=f"{production_time.lower}-{production_time.upper}",
            production_time_units=production_time_units
        )
        
    @classmethod
    def get_order_admin_new_text(
        cls,
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
        return cls.order.admin.new.text.format(
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
    
    @classmethod
    def get_order_admin_new_cancel_success_message(cls, order_number: str):
        return cls.order.admin.new.cancel.success.message.format(order_number=order_number)
    
    @classmethod
    def get_order_admin_new_cancel_reason_message(
        cls, 
        order_number: int,
        created_at: str,
        cancel_reason: str,
        order_text: str
    ):
        return cls.order.admin.new.cancel.reason.message.format(
            order_number=order_number,
            created_at=created_at,
            cancel_reason=cancel_reason,
            order_text=order_text
        )
    
    @classmethod
    def get_order_admin_new_cancel_error_message(cls, order_number: str):
        return cls.order.admin.new.cancel.error.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_cancel_success_message(cls, order_number: str):
        return cls.order.user.cancel.success.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_cancel_error_message(cls, order_number: str):
        return cls.order.user.cancel.error.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_send_for_payment_text(
        cls,
        order_number: int,
        created_at: str,
        status: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        admin_phone: str
    ):
        return cls.order.user.send.for_payment.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            admin_phone=admin_phone
        )
        
    @classmethod
    def get_order_admin_new_send_for_payment_success_message(cls, order_number: int):
        return cls.order.admin.new.send.for_payment.success.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_send_receipt_text(
        cls,
        order_number: int,
        created_at: str,
        status: str,
        products_text: str,
        delivery_price: float,
        total_with_delivery: float,
        delivery_info: str
    ):
        return cls.order.user.send.receipt.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            delivery_info=delivery_info
        )
        
    @classmethod
    def get_order_admin_new_send_receipt_success_message(cls, order_number: int):
        return cls.order.admin.new.send.receipt.success.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_all_control_show_text(cls, number_orders: int):
        return cls.order.user.all.control_show.text.format(number_orders=number_orders)
    
    @classmethod
    def get_order_user_all_control_show_current_text(
        cls,
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
        return cls.order.user.all.control_show.current.text.format(
            order_number=order_number,
            created_at=created_at,
            status=status,
            products_text=products_text,
            delivery_price=round(float(delivery_price), 2),
            total_with_delivery=round(float(total_with_delivery), 2),
            delivery_company=delivery_company,
            delivery_point_address=delivery_point_address,
            delivery_info=delivery_info
        )
    
    @classmethod
    def get_order_admin_new_cancel_user_text(
        cls,
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
            delivery_info_text = cls.order.admin.new.delivery_info.text.format(delivery_info=delivery_info)
            
        return cls.order.admin.new.cancel.user.text.format(
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
    
    @classmethod
    def get_order_user_cancel_success_message(cls, order_number: int):
        return cls.order.user.cancel.success.message.format(order_number=order_number)
    
    @classmethod
    def get_order_user_cancel_error_message(cls, order_number: int):
        return cls.order.user.cancel.error.message.format(order_number=order_number)