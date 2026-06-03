from typing import Dict

from psycopg2.extras import NumericRange

class ContentConfig:
    catalog_text: str = "🎁 *Каталог товаров*\n\nВыберите категорию:"
    all_product_text: str = "📋 *Все товары:*\n\n"
    user_cart_text: str = "🛒 *Ваша корзина:*\n\n"
    cart_item_text: str = (
        "• Nd\\_{article_number:05d}\n"
        "  Цена: {price} ₽ x {quantity} = {item_total} ₽\n\n"
    )
    cart_total_text: str = "💰 *Итого: {total} ₽*"
    product_text: str = (
        "🔖 *{name}*\n\n"
        "✨ *Nd_{article_number:05d}*\n\n"
        "💰 *Цена:* {price} ₽\n"
    )
    product_details_text: str = (
        "🔖 *{name}*\n\n"
        "✨ *Nd_{article_number:05d}*\n\n"
        "📝 *Описание:*\n{description}\n"
        "💰 *Цена:* {price} ₽\n"
        "⛓️ *Материалы:* {materials}\n"
        "🏷️ *Категория:* {category}\n"
        "🕒 *Время изготовления:* {production_time} {production_time_units}\n"
        "📦 *Максимум товаров в одном заказе:* {prod_limit}\n\n"
        "Выберите действие:"
    )
    
    product_added_to_cart_message: str = "✅ Товар добавлен в корзину! Теперь в корзине: {quantity} шт."
    
    catalog_message: str = "🛍️ Каталог товаров"
    cart_message: str = "🛒 Корзина"
    contact_with_message: str = "📞 Связаться с Nadine"
    about_message: str = "ℹ️ О Nadine"
    add_to_cart_message: str = "🛒 Добавить в корзину"
    more_detailed_message: str = "📋 Подробнее"
    empty_cart_message: str = "🔄 Очистить корзину"
    place_order_message: str = "💳 Оформить заказ"
    cart_is_empty_message: str = "Ваша корзина пуста"
    catalog_is_empty_message: str = "Каталог пуст"
    product_not_found_message: str = "❌ Товар не найден"
    prod_limit_exceeded_message: str = "⚠️ Превышен лимит данного товара. Для добавления большего числа обратитесь к Nadine."
    add_error_user_not_found_message: str = "❌ Ошибка добавления. Пользователь не найден."
    welcome_message: str = "Привет, {name}!\n\nВыбери действие из меню ниже:"
    session_not_found_message: str = "⚠️ Сессия не найдена. Начните заново из каталога"
    all_products_displayed_message: str = "✅ Все товары уже показаны"
    main_menu_message: str = "Главное меню:"
    
    catalog_control_next_message: str = "➡️ Следующий товар"
    catalog_control_next5_message: str = "5️⃣ Следующие 5"
    catalog_control_stop_message: str = "⏹ Остановить показ"
    catalog_control_back_to_main_menu_message: str = "◀️ В главное меню"
    
    catalog_menu_all_products_text: str = "Все товары"   
    catalog_menu_bracelets_category: str = "Браслеты"
    catalog_menu_earrings_category: str = "Серьги"
    catalog_menu_necklaces_category: str = "Ожерелья"
    catalog_menu_brooches_category: str = "Броши"
    catalog_menu_pendants_category: str = "Кулоны"
    catalog_menu_chains_category: str = "Цепочки"
    catalog_menu_rings_category: str = "Кольца"
    
    eng2ru_category_map: Dict[str, str] = {
        "bracelets": "браслеты",
        "earrings": "серьги",
        "necklaces": "ожерелья",
        "brooches": "броши",
        "pendants": "кулоны",
        "chains": "цепочки",
        "rings": "кольца",
    }
    
    category2text_map: Dict[str, str] = {
        "all": "📋 *Все товары*",
        "bracelets": "📿 *Браслеты*",
        "earrings": "💎 *Серьги*",
        "necklaces": "💫 *Ожерелья*",
        "brooches": "🦋 *Броши*",
        "pendants": "🔮 *Кулоны*",
        "chains": "⛓️ *Цепочки*",
        "rings": "💍 *Кольца*"
    }
    
    catalog_category_text: str = (
        "{category_text}\n"
        "Всего товаров: {number_products}\n"
        "Используйте кнопки внизу для навигации."
    )
    
    production_time_unit_1: str = "день"
    production_time_unit_234: str = "дня"
    production_time_unit_other: str = "дней"
    
    @classmethod
    def get_welcome_message(cls, name: str) -> str:
        return cls.welcome_message.format(name=name)
    
    @classmethod
    def get_cart_item_text(
        cls,
        article_number: int,
        price: float,
        quantity: int,
        item_total: float
    ):
        return cls.cart_item_text.format(
            article_number=article_number,
            price=round(float(price), 2),
            quantity=quantity,
            item_total=round(item_total, 2)
        )
    
    @classmethod
    def get_cart_total_text(cls, total: float):
        return cls.cart_total_text.format(total=round(total, 2))
    
    @classmethod
    def get_product_text(cls, name: str, article_number: int, price: float):
        return cls.product_text.format(name=name.capitalize(), article_number=article_number, price=round(float(price), 2))
    
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
        return cls.product_details_text.format(
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
        
    
    def get_catalog_category_text(
        cls,
        category: str,
        number_products: int
    ):
        return cls.catalog_category_text.format(
            category_text=cls.category2text_map.get(category),
            number_products=number_products
        )
        
    def get_product_addded_to_cart_message(cls, quantity: int):
        return cls.product_added_to_cart_message.format(quantity=quantity)