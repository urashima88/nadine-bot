from typing import List, Dict

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
        },
        "admin": {
            "category_menu": {
                "header_text": "🎁 *Каталог артикулов*\n\nВыберите категорию:",
            },
            "message": "🛍️ Каталог артикулов",
            "control_show": {
                "next": {"message": "➡️ Следующий артикул"},
                "next5": {"message": "5️⃣ Следующие 5 артикулов"},
                "stop": {"message": "⏹ Прекратить показ"},
                "go_back_to_main_menu": {"message": "◀️ Выйти главное меню"}
            },
            "edit": {
                "message": "✏️ Изменить артикул",
                "name": {
                    "message": "Изменить название",
                    "text": "Введите название артикула:",
                    "success": {
                        "message": "✅ Название артикула было успешно обновлено."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления названия артикула. Попробуйте позже."
                    }
                },
                "description": {
                    "message": "Изменить описание",
                    "text": "Введите описание артикула:",
                    "success": {
                        "message": "✅ Описание артикула было успешно обновлено."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления описания артикула. Попробуйте позже."
                    }
                },
                "price": {
                    "message": "Изменить цену",
                    "text": "Введите цену артикула:",
                    "success": {
                        "message": "✅ Цена артикула была успешно обновлена."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления цены артикула. Попробуйте позже."
                    },
                    "not_number": {
                        "message": "❌ Значение должно быть целым числом или числом с плавающей точкой."
                    },
                    "negative": {
                        "message": "❌ Значение цены aртикула не может быть отрицательным."
                    }
                },
                "category": {
                    "message": "Изменить категорию",
                    "text": "Выберите категорию из списка ниже:",
                    "success": {
                        "message": "✅ Категория артикула была успешно обновлена."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления категории артикула. Попробуйте позже."
                    }
                },
                "production_time": {
                    "message": "Изменить время изготовления",
                    "text": (
                        "Введите время изготовления артикула в формате 'минимум дней - максимум дней' (например, '1 - 2', также допустимо '1-2') или просто в формате 'максимум дней' (например, 3):"
                    ),
                    "success": {
                        "message": "✅ Время изготовления артикула было успешно обновлено."
                    },
                    "update_error": {
                        "message": "Ошибка обновления времени изготовления артикула. Попробуйте позже."
                    },
                    "lower": {
                        "not_number": {
                            "message": "❌ Значение нижней границы времени изготовления артикула должно быть целым числом."
                        },
                        "negative": {
                            "message": "❌ Значение нижней границы времени изготовления артикула не может быть отрицательным."
                        }
                    },
                    "upper": {
                        "not_number": {
                            "message": "❌ Значение верхней границы времени изготовления артикула должно быть целым числом."
                        },
                        "negative": {
                            "message": "❌ Значение верхней границы времени изготовления артикула не может быть отрицательным."
                        }
                    }
                },
                "prod_limit": {
                    "message": "Изменить максимум в одном заказе",
                    "text": "Введите максимально допустимое число товаров данного типа в одном заказе:",
                    "success": {
                        "message": "✅ Максимум в одном заказе был успешно обновлён."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления максимально допустимого числа товаров данного типа в одном заказе. Попробуйте позже."
                    },
                    "not_number": {
                        "message": "❌ Значение максимума в одном заказе должно быть целым числом."
                    },
                    "negative": {
                        "message": "❌ Значение максимума в одном заказе не может быть отрицательным."
                    }
                },
                "materials": {
                    "message": "Изменить материалы",
                    "text": "Введите названия материалов через ',':",
                    "success": {
                        "message": "✅ Материалы были успешно обновлены."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления материалов. Попробуйте позже."
                    }
                },
                "images": {
                    "message": "Изменить изображения",
                    "text": "Выберите действие из меню ниже:",
                    "add": {
                        "message": "Добавить изображение",
                        "text": "Загрузите изображение:",
                        "incorrect_file_format": {
                            "message": "❌ Неверный формат файла."
                        },
                        "exceed_limit": {
                            "message": "⚠️ Вы превысили лимит изображений на артикул (максимум 10 изображений)."
                        },
                        "failed_to_load": {
                            "message": "❌ Не удалось загрузить изображение. Попробуйте позже."
                        },
                        "success": {
                            "message": "✅ Изображение было успешно загружено."
                        },
                    },
                    "current": {
                        "message": "Изменить изображение №{image_number}",
                        "text": "Загрузите изображение:",
                        "incorrect_file_format": {
                            "message": "❌ Неверный формат файла."
                        },
                        "failed_to_load": {
                            "message": "❌ Не удалось загрузить изображение. Попробуйте позже."
                        },
                        "success": {
                            "message": "✅ Изображение №{image_number} было успешно заменено на новое."
                        },
                        "delete": {
                            "message": "Удалить изображение №{image_number}",
                            "success": {
                                "message": "✅ Изображение было успешно удалено."
                            },
                            "error": {
                                "message": "❌ Не удалось удалить файл."
                            }
                        }
                    }
                },
                "empty_value": {
                    "message": "❌ Значение не может быть пустым."
                },
                "not_found": {
                    "message": "❌ Товар не найден"
                },
            }
        }
    })
    
    common: edict = edict({
        "admin": {
            "contacts": {
                "text": (
                    "📞 *Контакты Nadine:*\n\n"
                    "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                    "📇 *Имя в Telegram:* {tg_full_name}\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📱 *Телефон:* [{phone}](tel:{phone})\n"
                    "🌐 *Часовой пояс:* {timezone}\n"
                ),
                "message": "📞 Связаться с Nadine"
            },
            "about": {
                "text": (
                    "👤 *О Nadine:*\n\n"
                    "..."
                ),
                "message": "ℹ️ О Nadine"
            },
            "user_data": {
                "all": {
                    "message": "🧑‍💻 Данные пользователей",
                    "is_empty": {
                        "message": "Нет пользователей"
                    },
                    "control_show": {
                        "text": (
                            "Всего пользователей: {number_users}\n"
                            "Используйте кнопки внизу для навигации."
                        ),
                        "next": {"message": "➡️ Следующий пользователь"},
                        "next5": {"message": "5️⃣ Следующие 5 пользователей"},
                        "go_back_to_main_menu": {"message": "◀️ Возврат в главное меню"},
                        "session_not_found": {
                            "message": "⚠️ Сессия не найдена. Нажмите '🧑‍💻 Данные пользователей'"
                        },
                        "current": {
                            "text": (
                                "👤 *Личные данные*\n\n"
                                "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                                "📇 *Имя в Telegram:* {tg_full_name}\n"
                                "📛 *ФИО:* {full_name}\n"
                                "📱 *Телефон:* {phone}\n"
                                "🌐 *Часовой пояс:* {timezone}\n"
                                "🚚 *Служба доставки:* {delivery_company}\n"
                                "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                                "📅 *Дата регистрации:* {created_at}\n"
                            )
                        }
                    },
                    "displayed": {
                        "message": "✅ Все пользователи уже показаны"
                    }
                },
                "main_menu": {
                    "message": "Главное меню:"
                }
            },
            "personal_data": {
                "message": "👤 Личные данные Nadine",
            },
            "profile": {
                "text": (
                    "👤 *Личные данные:*\n\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📱 *Телефон:* {phone}\n"
                    "🌐 *Часовой пояс:* {timezone}\n"
                )
            }
        },
        "user": {
            "personal_data": {
                "message": "👤 Личные данные"
            },
            "profile": {
                "text": (
                    "👤 *Личные данные:*\n\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📱 *Телефон:* {phone}\n"
                    "🌐 *Часовой пояс:* {timezone}\n"
                    "🚚 *Служба доставки:* {delivery_company}\n"
                    "📍 *Адрес пункта выдачи:* {delivery_point_address}" 
                )
            }
        },
        "profile": {
            "eng2ru_field_map": {
                "full_name": "ФИО",
                "phone": "Телефон",
                "timezone": "Часовой пояс",
                "delivery_company": "Служба доставки",
                "delivery_point_address": "Адрес пункта выдачи"
            },
            "edit": {
                "full_name": {
                    "message": "Изменить ФИО",
                    "text": "Введите ФИО:",
                    "success": {
                        "message": "✅ ФИО было успешно обновлено."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления ФИО. Попробуйте позже."
                    }
                },
                "phone": {
                    "message": "Изменить телефон",
                    "text": "Введите номер телефона:",
                    "success": {
                        "message": "✅ Номер телефона был успешно обновлён."
                    },
                    "wrong_format": {
                        "message": "❌ Неверный формат телефона. Введите номер например в таком формате +7.........."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления телефона. Попробуйте позже."
                    }
                },
                "timezone": {
                    "message": "Изменить часовой пояс",
                    "text": "Введите ваш часовой пояс в формате ±число, где число – смещение от UTC (целое число, например, +3, -5, 0):",
                    "success": {
                        "message": "✅ Часовой пояс был успешно обновлён."
                    },
                    "wrong_format": {
                        "message": "❌ Неверный формат. Введите, например: +3, или 2, или -5"
                    },
                    "offset_exceed": {
                        "message": "❌ Смещение не может превышать ±12 часов."
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления часового пояса. Попробуйте позже."
                    }
                },
                "delivery_company": {
                    "message": "Изменить службу доставки",
                    "text": "Введите название службы доставки (например, Яндекс Доставка):",
                    "success": {
                        "message": "✅ Служба доставки была успешно обновлена."
                    },
                    "question": {
                        "message": (
                            "У вас уже указана служба доставки: {delivery_company}\n"
                            "Вы хотели бы изменить её?"
                        ),
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления службы доставки. Попробуйте позже."
                    }
                },
                "delivery_point_address": {
                    "message": "Изменить адрес пункта выдачи",
                    "text": "Введите адрес пункта выдачи (например, г. Москва, Долгоруковская улица, 40):",
                    "success": {
                        "message": "✅ Адрес пункта выдачи был успешно обновлён."
                    },
                    "question": {
                        "message": (
                            "У вас уже указан адрес пункта выдачи: {delivery_point_address}\n"
                            "Вы хотели бы изменить его?"
                        ),
                    },
                    "update_error": {
                        "message": "❌ Ошибка обновления адреса пункта выдачи. Попробуйте позже."
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
                }
            }
        },
        "welcome": {
            "message": "Привет, {full_name}!\n\nВыбери действие из меню ниже:"
        },
        "error": {
            "message": "⚠️ Непредвиденная ошибка. Повторите позже."
        },
        "main_menu": {
            "admin": {
                "message": "Главное меню:"
            },
            "user": {
                "message": "Главное меню:"
            }
        },
        "eng2ru_month_map": {
            'January': 'Январь',
            'February': 'Февраль',
            'March': 'Март',
            'April': 'Апрель',
            'May': 'Май',
            'June': 'Июнь',
            'July': 'Июль',
            'August': 'Август',
            'September': 'Сентябрь',
            'October': 'Октябрь',
            'November': 'Ноябрь',
            'December': 'Декабрь'
        }, 
        "months": ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
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
                "🕒 *Время изготовления:* {production_time_text} {production_time_units}\n"
                "📦 *Максимум товаров в одном заказе:* {prod_limit}\n"
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
        },
        "admin": {
            "create": {
                "message": "🆕 Добавить артикул",
                "session_not_found": {
                    "message": "⚠️ Сессия не найдена. Начните заново из каталога"
                },
                "empty_value": {
                    "message": "❌ Значение не может быть пустым."
                },
                "name": {
                    "message": "Добавить название",
                    "text": "Введите название артикула:",
                    "success": {
                        "message": "✅ Название артикула было успешно сохранено."
                    }
                },
                "description": {
                    "message": "Добавить описание",
                    "text": "Введите описание артикула:",
                    "success": {
                        "message": "✅ Описание артикула было успешно сохранено."
                    }
                },
                "price": {
                    "message": "Добавить цену",
                    "text": "Введите цену артикула:",
                    "success": {
                        "message": "✅ Цена артикула была успешно сохранена."
                    },
                    "not_number": {
                        "message": "❌ Значение должно быть целым числом или числом с плавающей точкой."
                    },
                    "negative": {
                        "message": "❌ Значение цены aртикула не может быть отрицательным."
                    }
                },
                "category": {
                    "message": "Добавить категорию",
                    "text": "Выберите категорию из списка ниже:",
                    "success": {
                        "message": "✅ Категория артикула была успешно сохранена."
                    }
                },
                "production_time": {
                    "message": "Добавить время изготовления",
                    "text": (
                        "Введите время изготовления артикула в формате 'минимум дней - максимум дней' (например, '1 - 2', также допустимо '1-2') или просто в формате 'максимум дней' (например, 3):"
                    ),
                    "success": {
                        "message": "✅ Время изготовления артикула было успешно сохранено."
                    },
                    "lower": {
                        "not_number": {
                            "message": "❌ Значение нижней границы времени изготовления артикула должно быть целым числом."
                        },
                        "negative": {
                            "message": "❌ Значение нижней границы времени изготовления артикула не может быть отрицательным."
                        }
                    },
                    "upper": {
                        "not_number": {
                            "message": "❌ Значение верхней границы времени изготовления артикула должно быть целым числом."
                        },
                        "negative": {
                            "message": "❌ Значение верхней границы времени изготовления артикула не может быть отрицательным."
                        }
                    }
                },
                "prod_limit": {
                    "message": "Добавить максимум в одном заказе",
                    "text": "Введите максимально допустимое число товаров данного типа в одном заказе:",
                    "success": {
                        "message": "✅ Максимум в одном заказе был успешно сохранён."
                    },
                    "not_number": {
                        "message": "❌ Значение максимума в одном заказе должно быть целым числом."
                    },
                    "negative": {
                        "message": "❌ Значение максимума в одном заказе не может быть отрицательным."
                    }
                },
                "materials": {
                    "message": "Добавить материалы",
                    "text": "Введите названия материалов через ',':",
                    "success": {
                        "message": "✅ Материалы были успешно сохранены."
                    }
                },
                "images": {
                    "add": {
                        "message": "Добавить изображение",
                        "text": "Загрузите изображение:",
                        "incorrect_file_format": {
                            "message": "❌ Неверный формат файла."
                        },
                        "exceed_limit": {
                            "message": "⚠️ Вы превысили лимит изображений на артикул (максимум 10 изображений)."
                        },
                        "failed_to_load": {
                            "message": "❌ Не удалось загрузить изображение. Попробуйте позже."
                        },
                        "success": {
                            "message": "✅ Изображение было успешно загружено."
                        }
                    }
                },
                "clear": {
                    "message": "🔄 Очистить данные артикула",
                    "success": {
                        "message": "✅ Данные артикула были успешно очищены."
                    },
                    "error": {
                        "message": "❌ Не удалось очистить данные артикула. Попробуйте позже."
                    }
                },
                "complete": {
                    "message": "🏁 Завершить создание артикула",
                    "success": {
                        "message": "✅ Новый артикул был успешно создан."
                    },
                    "error": {
                        "message": "❌ Не удалось создать новый артикул. Попробуйте позже."
                    }
                },
                "empty_value": {
                    "message": "❌ Значение не может быть пустым."
                }
            }
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
                        "🕒 *Время изготовления:* {production_time_text} {production_time_units}"
                    )
                }
            },
            "new": {
                "text": (
                    "🆕 *НОВЫЙ ЗАКАЗ №{order_number}*\n\n"
                    "📅 *Дата и время оформления заказа:* {created_at}\n\n"
                    "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                    "📇 *Имя в Telegram:* {tg_full_name}\n"
                    "📛 *ФИО:* {full_name}\n"
                    "📱 *Телефон*: [{phone}](tel:{phone})\n"
                    "🚚 *Служба доставки:* {delivery_company}\n"
                    "📍 *Адрес пункта выдачи:* {delivery_point_address}\n\n"
                    "📦 *Состав заказа:*\n\n{products_text}\n\n"
                    "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                    "💰 *Общая сумма:* {total_price} ₽\n"
                ),
                "set_delivery_price": {
                    "message": "💰 Ввести стоимость доставки",
                    "text": "Введите стоимость доставки:",
                    "empty_value": {
                        "message": "❌ Значение не может быть пустым."
                    },
                    "not_number": {
                        "message": "❌ Значение стоимости доставки должно быть целым числом или числом с плавающей точкой."
                    },
                    "negative": {
                        "message": "❌ Значение стоимости доставки не может быть отрицательным."
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
                            "*Причина:* {cancel_reason}\n\n"
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
                            "📇 *Имя в Telegram:* {tg_full_name}\n"
                            "📛 *ФИО:* {full_name}\n"
                            "📱 *Телефон*: [{phone}](tel:{phone})\n"
                            "🚚 *Служба доставки:* {delivery_company}\n"
                            "📍 *Адрес пункта выдачи:* {delivery_point_address}\n\n"
                            "📦 *Состав заказа:*\n\n{products_text}\n\n"
                            "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                            "{delivery_info_text}\n"
                            "💰 *Общая сумма:* {total_price} ₽\n"
                        )
                    },
                    "not_completed_yet": {
                        "other": {
                            "message": "⚠️ У вас ещё не завершён процесс отмены другого заказа"
                        },
                        "current": {
                            "message": "⚠️ Вы уже находитесь в процессе отмены данного заказа"
                        }
                    }
                },
                "send": {
                    "for_payment": {
                        "message": "💳 Отправить на оплату",
                        "text": "Загрузите файл счёта на оплату (документ или изображение):",
                        "success": {
                            "message": "✅ Инвойс для заказа №{order_number} отправлен пользователю."
                        }
                    },
                    "receipt": {
                        "message": "🧾 Отправить чек",
                        "file": {
                            "text": "Загрузите файл чека (документ или изображение):",
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
            },
            "all": {
                "message": "📦 Заказы",
                "is_empty": {
                    "message": "Нет заказов"
                },
                "control_show": {
                    "text": (
                        "Всего заказов: {number_orders}\n"
                        "Используйте кнопки внизу для навигации."
                    ),
                    "next": {"message": "➡️ Следующий заказ пользователя"},
                    "next5": {"message": "5️⃣ Следующие 5 заказов пользователей"},
                    "go_back_to_main_menu": {"message": "◀️ Назад в главное меню"},
                    "session_not_found": {
                        "message": "⚠️ Сессия не найдена. Нажмите '📦 Заказы'"
                    },
                    "current": {
                        "text": (
                            "🎁 *Заказ №{order_number}*\n\n"
                            "📅 *Дата и время оформления заказа:* {created_at}\n"
                            "📌 *Статус заказа:* {status}\n\n"
                            "🆔 *Имя пользователя:* [@{tg_username}](https://t.me/{tg_username})\n"
                            "📇 *Имя в Telegram:* {tg_full_name}\n"
                            "📛 *ФИО:* {full_name}\n"
                            "📱 *Телефон*: [{phone}](tel:{phone})\n\n"
                            "📦 *Состав заказа:*\n{products_text}\n\n"
                            "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                            "💰 *Общая сумма:* {total_with_delivery} ₽\n\n"
                            "🚚 *Служба доставки:* {delivery_company}\n"
                            "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                            "{delivery_info_text}\n"
                        ),
                        "delivery_info": {
                            "text": "🚛 *Информация по доставке:\n*{delivery_info}"
                        },
                        "cancel": {
                            "message": "❌ Отменить заказ"
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
                        "📦 *Состав заказа:*\n{products_text}\n\n"
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
                        "📦 *Состав заказа:*\n{products_text}\n\n"
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
                            "🎁 *Заказ №{order_number}*\n\n"
                            "📅 *Дата и время оформления заказа:* {created_at}\n"
                            "📌 *Статус заказа:* {status}\n\n"
                            "📦 *Состав заказа:*\n{products_text}\n\n"
                            "🛵 *Стоимость доставки:* {delivery_price} ₽\n"
                            "💰 *Общая сумма:* {total_with_delivery} ₽\n\n"
                            "🚚 *Служба доставки:* {delivery_company}\n"
                            "📍 *Адрес пункта выдачи:* {delivery_point_address}\n"
                            "{delivery_info_text}\n"
                        ),
                        "delivery_info": {
                            "text": "🚛 *Информация по доставке:\n*{delivery_info}"
                        },
                        "cancel": {
                            "message": "❌ Отменить заказ"
                        },
                        "copy_to_cart": {
                            "message": "🗂️ Скопировать товары в корзину",
                            "error": {
                                "message": "❌ Заказ не найден или не принадлежит вам"
                            },
                            "added": {
                                "message": "✅ Добавлены артикулы: {added_text}"
                            },
                            "skipped": {
                                "message": "⚠️ Не добавлены (превышен лимит): {skipped_text}"
                            },
                            "no_products": {
                                "message": "❌ Нет товаров для добавления."
                            }
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
            "canceled": {
                "text": "отменён"
            },
            "update_error": {
                "message": "❌ Не удалось обновить статус заказа."
            }
        }
    })
    
    statistics: edict = edict({
        "admin": {
            "message": "📊 Статистика",
            "month": {
                "no_data": {
                    "message": "📊 Нет данных за текущий месяц."
                }
            },
            "text": (
                "📊 *Статистика за {month_name} {year}*\n\n"
                "📦 *Выполненных заказов:* {order_count}\n"
                "💰 *Выручка:* {total_revenue} ₽\n"
                "👤 *Новых пользователей:* {new_users_count}\n"
                "🔥 *Активных пользователей:* {active_users_count}\n\n"
                "🏆 *Топ-3 товаров:*\n"
                "{top_products_text}"
            ),
            "top_product": {
                "text": "{place}. {name} (Nd\\_{article_number:05d}) — {total_quantity} шт.\n"
            },
            "histogram": {
                "completed_orders": {
                    "year": {
                        "message": "График 'Число выполненных заказов за текущий год'",
                        "no_data": {
                            "message": "📊 Нет выполненных заказов за текущий год."
                        },
                        "header": {
                            "text": "Количество выполненных заказов по месяцам ({year})"
                        }
                    },
                    "count": {
                        "text": "Количество заказов"
                    }
                },
                "revenue": {
                    "year": {
                        "message": "График 'Выручка за текущий год'",
                        "no_data": {
                            "message": "📊 Нет выручки за текущий год."
                        },
                        "header": {
                            "text": "Выручка по месяцам ({year})"
                        }
                    },
                    "total": {
                        "text": "Выручка (₽)"
                    }
                },
                "new_users": {
                    "year": {
                        "message": "График 'Число новых пользователей за текущий год'",
                        "no_data": {
                            "message": "📊 Нет новых пользователей за текущий год."
                        },
                        "header": {
                            "text": "Число новых пользователей по месяцам ({year})"
                        }
                    },
                    "count": {
                        "text": "Количество пользователей"
                    }
                },
                "month": {
                    "text": "Месяц"
                }
            }
        }
    })
    
    settings: edict = edict({
        "admin": {
            "message": "⚙️ Настройки"
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
        
    @classmethod
    def get_catalog_admin_edit_images_current_message(cls, image_number: int):
        return cls.catalog.admin.edit.images.current.message.format(image_number=image_number)
    
    @classmethod
    def get_catalog_admin_edit_images_current_delete_message(cls, image_number: int):
        return cls.catalog.admin.edit.images.current.delete.message.format(image_number=image_number)
    
    @classmethod
    def get_catalog_admin_edit_images_current_success_message(cls, image_number: int):
        return cls.catalog.admin.edit.images.current.success.message.format(image_number=image_number)
        
    # common
    
    @classmethod
    def get_common_welcome_message(cls, full_name: str) -> str:
        return cls.common.welcome.message.format(full_name=full_name)
    
    @classmethod
    def get_common_admin_contacts_text(
        cls, 
        tg_username: str,
        tg_full_name: str,
        full_name: str, 
        phone: str,
        timezone: str
    ):
        return cls.common.admin.contacts.text.format(
            tg_username=tg_username, 
            tg_full_name=tg_full_name,
            full_name=full_name,
            phone=phone,
            timezone=timezone
        )
    
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
    def get_common_admin_profile_text(
        cls,
        full_name: str,
        phone: str,
        timezone: str
    ):
        return cls.common.admin.profile.text.format(
            full_name=full_name,
            phone=phone,
            timezone=timezone
        )
    
    @classmethod 
    def get_common_profile_edit_delivery_company_question_message(cls, delivery_company: str):
        return cls.common.profile.edit.delivery_company.question.message.format(delivery_company=delivery_company)
    
    @classmethod
    def get_common_profile_edit_delivery_point_address_question_message(cls, delivery_point_address: str):
        return cls.common.profile.edit.delivery_point_address.question.message.format(delivery_point_address=delivery_point_address)
    
    @classmethod
    def get_common_admin_user_data_all_control_show_text(cls, number_users: int):
        return cls.common.admin.user_data.all.control_show.text.format(number_users=number_users)
    
    @classmethod
    def get_common_admin_user_data_all_control_show_current_text(
        cls,
        tg_username: str,
        tg_full_name: str,
        full_name: str,
        phone: str,
        timezone: str,
        delivery_company: str,
        delivery_point_address: str,
        created_at: str
    ):
        return cls.common.admin.user_data.all.control_show.current.text.format(
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
        production_time_text = ""
        if production_time:
            if production_time.upper-1 - production_time.lower == 0:
                production_time_text = f"{production_time.upper-1}"
            else:
                production_time_text = f"{production_time.lower}-{production_time.upper-1}"
        
        return cls.product.details.text.format(
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
    
    @classmethod
    def get_order_start_message(cls, remaining: int):
        return cls.order.start.message.format(remaining=remaining)

    @classmethod
    def get_order_place_empty_fields_message(cls, fields: List[str]):
        translated_fields = []
        for field in fields:
            translated_field = cls.common.profile.eng2ru_field_map.get(field)
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
        if production_time.upper-1 - production_time.lower == 0:
            production_time_text = f"{production_time.upper-1}"
        else:
            production_time_text = f"{production_time.lower}-{production_time.upper-1}"
        
        return cls.order.admin.product.details.text.format(
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
        delivery_info_text = ""
        if delivery_info is not None:
            delivery_info_text = cls.order.user.all.control_show.current.delivery_info.text.format(delivery_info=delivery_info)
        
        return cls.order.user.all.control_show.current.text.format(
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
    
    @classmethod
    def get_order_user_all_control_show_current_copy_to_cart_added_message(cls, added: List[str]):
        added_text = ', '.join(map(str, added))
        return cls.order.user.all.control_show.current.copy_to_cart.added.message.format(added_text=added_text)
    
    @classmethod
    def get_order_user_all_control_show_current_copy_to_cart_skipped_message(cls, skipped: List[str]):
        skipped_text = ', '.join(map(str, skipped))
        return cls.order.user.all.control_show.current.copy_to_cart.skipped.message.format(skipped_text=skipped_text)
    
    @classmethod
    def get_order_admin_all_control_show_text(cls, number_orders: int):
        return cls.order.admin.all.control_show.text.format(number_orders=number_orders)
    
    @classmethod
    def get_order_admin_all_control_show_current_text(
        cls,
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
            delivery_info_text = cls.order.admin.all.control_show.current.delivery_info.text.format(delivery_info=delivery_info)
        
        return cls.order.admin.all.control_show.current.text.format(
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
    
    @classmethod
    def get_statistics_admin_top_product_text(
        cls,
        place: int,
        name: str,
        article_number: int,
        total_quantity: int
    ):
        return cls.statistics.admin.top_product.text.format(
            place=place,
            name=name.capitalize(),
            article_number=article_number,
            total_quantity=total_quantity
        )
            
    @classmethod
    def get_statistics_admin_text(
        cls,
        month_name: str,
        year: str,
        order_count: int,
        total_revenue: float,
        new_users_count: int,
        active_users_count: int,
        top_products_text: str
    ):
        return cls.statistics.admin.text.format(
            month_name=month_name,
            year=year,
            order_count=order_count,
            total_revenue=round(float(total_revenue), 2),
            new_users_count=new_users_count,
            active_users_count=active_users_count,
            top_products_text=top_products_text
        )
          
    @classmethod  
    def get_statistics_admin_histogram_completed_orders_year_header_text(cls, year: str):
        return cls.statistics.admin.histogram.completed_orders.year.header.text.format(year=year)
    
    @classmethod
    def get_statistics_admin_histogram_revenue_year_header_text(cls, year: str):
        return cls.statistics.admin.histogram.revenue.year.header.text.format(year=year)
    
    @classmethod
    def get_statistics_admin_histogram_new_users_year_header_text(cls, year: str):
        return cls.statistics.admin.histogram.new_users.year.header.text.format(year=year)