"""
Telegram бот для Ozon статистики - с работающим меню
"""
import asyncio
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv

# Настройки
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user

    # Основное приветственное сообщение
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я бот для мониторинга статистики заказов Ozon.\n\n"
        f"📊 Используйте команды меню ниже 👇\n"
        f"🌐 Веб-панель: http://localhost:8000"
    )

    # СОЗДАЕМ REPLY KEYBOARD (постоянное меню внизу)
    keyboard = [
        [KeyboardButton("📊 Текущая статистика")],
        [KeyboardButton("📈 Отчет за день"), KeyboardButton("📋 Список товаров")],
        [KeyboardButton("✅ Подписаться"), KeyboardButton("❌ Отписаться")],
        [KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👇 Выберите действие в меню:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "🤖 *Ozon Stats Bot*\n\n"
        "📊 *Основные функции:*\n"
        "• 📊 Текущая статистика\n"
        "• 📈 Отчет за день\n"
        "• 📋 Список товаров\n"
        "• ✅/❌ Подписка на отчеты\n\n"
        "🕐 *Расписание:*\n"
        "• Часовые отчеты: каждый час\n"
        "• Веб-панель: http://localhost:8000\n\n"
        "📞 *Команды:*\n"
        "/start - обновить меню\n"
        "/stats - статистика\n"
        "/report - отчет\n"
        "/subscribe - подписка",
        parse_mode=ParseMode.MARKDOWN
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    stats = (
        "📊 *Текущая статистика*\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        "📈 *Заказы за сегодня:*\n"
        "• Всего: 15\n"
        "• За час: 3\n"
        "• Средний чек: 12,456₽\n\n"
        "🏆 *Топ товары:*\n"
        "1. Смартфон Xiaomi - 5 заказов\n"
        "2. Наушники JBL - 3 заказа\n"
        "3. Ноутбук ASUS - 2 заказа\n\n"
        "🌐 *Веб-панель:* http://localhost:8000"
    )
    await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /report"""
    report = (
        "📊 *Отчет Ozon*\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        "📈 *Статистика:*\n"
        "• Заказов: 127\n"
        "• Выручка: 1,583,245₽\n"
        "• Средний чек: 12,466₽\n\n"
        "🏆 *Топ-3:*\n"
        "1. 📱 Смартфон (28 заказов)\n"
        "2. 🎧 Наушники (15 заказов)\n"
        "3. 💻 Ноутбук (12 заказов)\n\n"
        "🌐 *Детальная статистика:*\n"
        "http://localhost:8000"
    )
    await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /subscribe"""
    await update.message.reply_text(
        "✅ *Подписка оформлена!*\n\n"
        "Вы будете получать:\n"
        "• Часовые отчеты\n"
        "• Ежедневные итоги\n"
        "• Важные уведомления\n\n"
        "Для отписки нажмите ❌ Отписаться в меню",
        parse_mode=ParseMode.MARKDOWN
    )


async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /products"""
    await update.message.reply_text(
        "🛒 *Список отслеживаемых товаров:*\n\n"
        "1. `123456` - Смартфон Xiaomi Redmi Note 12\n"
        "2. `789012` - Наушники JBL Tune 510BT\n"
        "3. `345678` - Ноутбук ASUS VivoBook 15\n"
        "4. `901234` - Часы Apple Watch Series 9\n"
        "5. `567890` - Планшет Samsung Galaxy Tab S9\n\n"
        "📊 *Всего:* 10 товаров",
        parse_mode=ParseMode.MARKDOWN
    )


# ========== ОБРАБОТКА СООБЩЕНИЙ (КНОПОК) ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (нажатий на кнопки Reply Keyboard)"""
    text = update.message.text

    if text == "📊 Текущая статистика":
        await stats_command(update, context)
    elif text == "📈 Отчет за день":
        await report_command(update, context)
    elif text == "📋 Список товаров":
        await products_command(update, context)
    elif text == "✅ Подписаться":
        await subscribe_command(update, context)
    elif text == "❌ Отписаться":
        await update.message.reply_text(
            "❌ *Вы отписались от отчетов.*\n\n"
            "Вы больше не будете получать автоматические отчеты.\n"
            "Для подписки нажмите ✅ Подписаться",
            parse_mode=ParseMode.MARKDOWN
        )
    elif text == "❓ Помощь":
        await help_command(update, context)
    else:
        # Если текст не распознан, предлагаем меню
        await update.message.reply_text(
            "ℹ️ Используйте меню ниже или команды:\n"
            "/start - обновить меню\n"
            "/stats - статистика\n"
            "/help - помощь"
        )


# ========== ЗАПУСК БОТА ==========
def main():
    """Основная функция запуска"""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN не найден в .env!")
        print("Добавьте в .env: TELEGRAM_TOKEN=ваш_токен")
        return

    # Создаем новый event loop для Windows
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("products", products_command))

    # Обработчик текстовых сообщений (кнопок меню)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Бот запущен...")
    print("✅ Telegram бот запущен с рабочим меню!")
    print("📱 Откройте: @ozon_stats_analytics_bot")
    print("🌐 Веб-панель: http://localhost:8000")

    try:
        # Запускаем бота
        app.run_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
