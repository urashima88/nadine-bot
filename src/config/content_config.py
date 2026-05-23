
class ContentConfig:
    catalog_text: str = "🎁 *Каталог товаров*\n\nВыберите категорию:"
    all_product_text: str = "📋 *Все товары:*\n\n"
    user_cart_text: str = "🛒 *Ваша корзина:*\n\n"
    cart_item_text: str = (
        "• Nd\\_{article_number}\n"
        "  Цена: {price} ₽ x {quantity} = {item_total} ₽\n\n"
    )
    cart_total_text: str = "💰 *Итого: {total} ₽*"
    product_text: str = (
        "✨ *Nd_{article_number}*\n\n"
        "💰 *Цена:* {price} ₽\n"
    )
    product_details_text: str = (
        "✨ *Nd_{article_number}*\n\n"
        "📝 *Описание:*\n{description}\n"
        "💰 *Цена:* {price} ₽\n"
        "⛓️ *Материалы:* {materials}\n"
        "🏷️ *Категория:* {category}\n\n"
        "Выберите действие:"
    )
    
    catalog_message: str = '🛍️ Каталог товаров'
    cart_message: str = '🛒 Корзина'
    contact_with_message: str = '📞 Связаться с Nadine'
    about_message: str = 'ℹ️ О Nadine'
    add_to_cart_message: str = '🛒 Добавить в корзину'
    more_detailed_message: str = '📋 Подробнее'
    back_to_catalog_message: str = '⬅️ Назад к каталогу'
    empty_cart_message: str = '🔄 Очистить корзину'
    place_order_message: str = '💳 Оформить заказ'
    back_message: str = '⬅️ Назад'
    cart_is_empty_message: str = "Ваша корзина пуста"
    catalog_is_empty_message: str = "Каталог пуст"
    product_not_found_message: str = "Товар не найден"
    product_added_to_cart_message: str = "✅ Товар добавлен в корзину!"
    welcome_message: str = "Привет, {name}!\n\nВыбери действие из меню ниже:"
    
    catalog_menu_all_products_text: str = 'Все товары'   
    catalog_menu_bracelets_category: str = 'Браслеты'
    catalog_menu_earrings_category: str = 'Серьги'
    catalog_menu_necklaces_category: str = 'Ожерелья'
    catalog_menu_brooches_category: str = 'Броши'
    catalog_menu_back: str = 'Назад'
    
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
            price=round(price, 2),
            quantity=quantity,
            item_total=round(item_total, 2)
        )
    
    @classmethod
    def get_cart_total_text(cls, total: float):
        return cls.cart_total_text.format(total=round(total, 2))
    
    @classmethod
    def get_product_text(cls, article_number: int, price: float):
        return cls.product_text.format(article_number=article_number, price=round(price, 2))
    
    @classmethod
    def get_product_details_text(
        cls,
        article_number: int,
        description: str,
        price: float,
        materials: str,
        category: str
    ):
        return cls.product_details_text.format(
            article_number=article_number,
            description=description,
            price=round(price, 2),
            materials=materials,
            category=category
        )
        
    