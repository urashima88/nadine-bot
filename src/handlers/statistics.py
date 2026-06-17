from logging import Logger
from datetime import datetime
from io import BytesIO
from typing import List

from telebot import TeleBot, types
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from src.storage import Storage
from src.config.config import Config
from src.config.content_config import ContentConfig
from src.utils.wrappers import error_handler
from src.keyboards import statistics_keyboard


def register_statistics_handlers(bot: TeleBot, db: Storage, cfg: Config, content_cfg: ContentConfig,  logger: Logger):
    err_handler = error_handler(bot, content_cfg, logger)
    
    @bot.message_handler(func=lambda message: message.text == content_cfg.statistics.admin.message)
    @err_handler
    def show_statistics(message: types.Message):
        logger.debug("show_statistics CALL")
        
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        completed_orders = db.get_monthly_completed_orders()
        revenue = db.get_monthly_revenue()
        new_users = db.get_monthly_new_users()
        active_users = db.get_monthly_active_users()
        top_products = db.get_top_selling_products(3)
        
        def filter_current_month(data):
            current_ym = current_month.strftime('%Y-%m')
            return next((item for item in data if item['month'].strftime('%Y-%m') == current_ym), None)
        
        cur_completed = filter_current_month(completed_orders)
        cur_revenue = filter_current_month(revenue)
        cur_new_users = filter_current_month(new_users)
        cur_active_users = filter_current_month(active_users)
        
        if not any([cur_completed, cur_revenue, cur_new_users, cur_active_users, top_products]):
            bot.send_message(message.chat.id, content_cfg.statistics.admin.month.no_data.message, parse_mode="Markdown")
        
        orders_count = total_revenue = new_users_count = active_users_count = 0
        if cur_completed:
            orders_count = cur_completed['orders_count']
        if cur_revenue:
            total_revenue = cur_revenue['total_revenue']
        if cur_new_users:
            new_users_count = cur_new_users['new_users_count']
        if cur_active_users:
            active_users_count = cur_active_users['active_users_count']
                
        top_products_text = ""
        if top_products:
            for i, product in enumerate(top_products, start=1):
                top_products_text += content_cfg.get_statistics_admin_top_product_text(
                    place=i,
                    name=product["name"],
                    article_number=product["article_number"],
                    total_quantity=product["total_quantity"]
                )
        
        month_name = content_cfg.common.eng2ru_month_map[current_month.strftime('%B')]
        year = current_month.year
        
        statistics_text = content_cfg.get_statistics_admin_text(
            month_name,
            year,
            orders_count,
            total_revenue,
            new_users_count,
            active_users_count,
            top_products_text
        )
        
        bot.send_message(
            message.chat.id,
            statistics_text,
            parse_mode="Markdown",
            reply_markup=statistics_keyboard(content_cfg)
        )
        
    @bot.callback_query_handler(func=lambda call: call.data == "plot_completed_orders_year")
    @err_handler
    def plot_completed_orders_year(call):
        logger.debug("plot_completed_orders_year CALL")
        
        bot.answer_callback_query(call.id)
        
        year = datetime.now().year
        data = db.get_monthly_completed_orders_for_year(year)
        
        if not data or all(item['orders_count'] == 0 for item in data):
            bot.send_message(call.message.chat.id, content_cfg.statistics.admin.histogram.completed_orders.year.no_data.message)
            return
        
        counts = [item['orders_count'] for item in data]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(get_month_short_names(), counts, color='skyblue', edgecolor='navy', linewidth=1.2)

        ax.set_title(content_cfg.get_statistics_admin_histogram_completed_orders_year_header_text(year), fontsize=16, pad=20)
        ax.set_xlabel(content_cfg.statistics.admin.histogram.month.text, fontsize=12)
        ax.set_ylabel(content_cfg.statistics.admin.histogram.completed_orders.count.text, fontsize=12)
        
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(count), ha='center', va='bottom', fontsize=10)
                
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        bot.send_photo(call.message.chat.id, buf)
    
    @bot.callback_query_handler(func=lambda call: call.data == "plot_revenue_year")
    @err_handler
    def plot_revenue_year(call):
        logger.debug("plot_revenue_year CALL")
        
        bot.answer_callback_query(call.id)
        
        year = datetime.now().year
        data = db.get_monthly_revenue_for_year(year)
        
        if not data or all(item['total_revenue'] == 0 for item in data):
            bot.send_message(call.message.chat.id, content_cfg.statistics.admin.histogram.revenue.year.no_data.message)
            return
        
        revenues = [item['total_revenue'] for item in data]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(get_month_short_names(), revenues, color='lightgreen', edgecolor='darkgreen', linewidth=1.2)
        
        ax.set_title(content_cfg.get_statistics_admin_histogram_revenue_year_header_text(year), fontsize=16, pad=20)
        ax.set_xlabel(content_cfg.statistics.admin.histogram.month.text, fontsize=12)
        ax.set_ylabel(content_cfg.statistics.admin.histogram.revenue.total.text, fontsize=12)
        
        for bar, value in zip(bars, revenues):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(value) + ' ₽', ha='center', va='bottom', fontsize=9)
                
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        bot.send_photo(call.message.chat.id, buf)

    @bot.callback_query_handler(func=lambda call: call.data == "plot_new_users_year")
    @err_handler
    def plot_new_users_year(call):
        logger.debug("plot_new_users_year CALL")
        
        bot.answer_callback_query(call.id)

        year = datetime.now().year
        data = db.get_monthly_new_users_for_year(year)

        if not data or all(item['new_users_count'] == 0 for item in data):
            bot.send_message(call.message.chat.id, content_cfg.statistics.admin.histogram.new_users.year.no_data.message)
            return

        counts = [item['new_users_count'] for item in data]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(get_month_short_names(), counts, color='lightsalmon', edgecolor='darkred', linewidth=1.2)

        ax.set_title(content_cfg.get_statistics_admin_histogram_new_users_year_header_text(year), fontsize=16, pad=20)
        ax.set_xlabel(content_cfg.statistics.admin.histogram.month.text, fontsize=12)
        ax.set_ylabel(content_cfg.statistics.admin.histogram.new_users.count.text, fontsize=12)
        
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(count), ha='center', va='bottom', fontsize=10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)

        bot.send_photo(call.message.chat.id, buf)
        
    def get_month_short_names() -> List[str]:
        month_short_names = []
        for ru_month in content_cfg.common.eng2ru_month_map.values():
            month_short_names.append(ru_month[:3])
        return month_short_names