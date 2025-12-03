import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Dict, List
import random
from dataclasses import dataclass


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ArticleStats:
    """Статистика по одному артикулу"""
    article: str
    name: str
    hourly_orders: int  # заказов за последний час
    daily_orders: int  # заказов за текущий день
    price: float

    def format_report(self) -> str:
        return f"{self.article} - {self.name}: {self.hourly_orders} / {self.daily_orders} (цена: {self.price}₽)"


class MockOzonAPI:
    """Мок-класс для имитации API Ozon"""

    def __init__(self):
        self.articles = {
            "123456": "Смартфон Xiaomi Redmi Note 12",
            "789012": "Наушники JBL Tune 510BT",
            "345678": "Ноутбук ASUS VivoBook 15",
            "901234": "Часы Apple Watch Series 9",
            "567890": "Планшет Samsung Galaxy Tab S9",
            "234567": "Фитнес-браслет Huawei Band 8",
            "890123": "Колонка Яндекс Станция Мини 2",
            "456789": "Монитор LG 24MP400-B",
            "012345": "Клавиатура Logitech MX Keys",
            "678901": "Мышь беспроводная Razer Viper"
        }

        # Начальные цены
        self.prices = {
            "123456": 19999.99,
            "789012": 3499.99,
            "345678": 54999.99,
            "901234": 42999.99,
            "567890": 72999.99,
            "234567": 2999.99,
            "890123": 8999.99,
            "456789": 12999.99,
            "012345": 11999.99,
            "678901": 6999.99
        }

        # История заказов за день (артикул -> список времен заказов)
        self.daily_orders_history: Dict[str, List[datetime]] = {}

    def generate_hourly_orders(self, article: str, current_hour: int) -> int:
        """
        Генерация реалистичных заказов за час
        Больше заказов в часы пик (11-13, 19-21)
        """
        base_orders = random.randint(0, 3)

        # Часы пик
        if 11 <= current_hour <= 13:
            base_orders += random.randint(2, 5)
        elif 19 <= current_hour <= 21:
            base_orders += random.randint(3, 7)
        elif current_hour < 8 or current_hour > 22:
            base_orders = random.randint(0, 1)

        # Случайные всплески
        if random.random() < 0.1:  # 10% шанс на всплеск
            base_orders *= random.randint(2, 4)

        return max(0, base_orders)

    def update_price(self, article: str) -> float:
        """Имитация изменения цены"""
        change_percent = random.uniform(-0.02, 0.02)  # ±2%
        self.prices[article] *= (1 + change_percent)
        self.prices[article] = round(self.prices[article], 2)
        return self.prices[article]

    def get_stats_for_hour(self, hour: int) -> List[ArticleStats]:
        """Получение статистики для указанного часа"""
        stats = []
        current_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)

        for article, name in self.articles.items():
            # Генерируем заказы за этот час
            hourly_orders = self.generate_hourly_orders(article, hour)

            # Обновляем историю заказов
            if article not in self.daily_orders_history:
                self.daily_orders_history[article] = []

            # Добавляем временные метки заказов
            for _ in range(hourly_orders):
                order_time = current_time + timedelta(minutes=random.randint(0, 59))
                self.daily_orders_history[article].append(order_time)

            # Считаем заказы за день (до текущего часа включительно)
            daily_orders = len([
                t for t in self.daily_orders_history.get(article, [])
                if t.hour <= hour
            ])

            # Обновляем цену
            price = self.update_price(article)

            stats.append(ArticleStats(
                article=article,
                name=name,
                hourly_orders=hourly_orders,
                daily_orders=daily_orders,
                price=price
            ))

        return stats


class StatsCollector:
    """Сборщик статистики"""

    def __init__(self):
        self.api = MockOzonAPI()
        self.current_hour = datetime.now().hour

    def collect_current_stats(self) -> List[ArticleStats]:
        """Сбор текущей статистики"""
        current_hour = datetime.now().hour
        return self.api.get_stats_for_hour(current_hour)

    def get_top_performers(self, stats: List[ArticleStats], limit: int = 3) -> List[ArticleStats]:
        """Получение топовых товаров по заказам за час"""
        return sorted(stats, key=lambda x: x.hourly_orders, reverse=True)[:limit]


class ReportGenerator:
    """Генератор отчетов"""

    @staticmethod
    def generate_hourly_report(stats: List[ArticleStats],
                               top_performers: List[ArticleStats]) -> str:
        """Генерация часового отчета"""
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        report = [
            f"📊 Отчет по заказам Ozon",
            f"🕐 Время отчета: {current_time}",
            f"📈 Общая статистика:",
            ""
        ]

        # Общая статистика
        total_hourly = sum(s.hourly_orders for s in stats)
        total_daily = sum(s.daily_orders for s in stats)

        report.append(f"Всего заказов за час: {total_hourly}")
        report.append(f"Всего заказов за день: {total_daily}")
        report.append("")

        # Топ товаров
        if top_performers:
            report.append("🏆 Топ товаров за час:")
            for i, item in enumerate(top_performers, 1):
                report.append(f"{i}. {item.format_report()}")
            report.append("")

        # Детальная статистика
        report.append("📋 Детальная статистика по артикулам:")
        for item in stats:
            report.append(f"• {item.format_report()}")

        return "\n".join(report)

    @staticmethod
    def generate_summary_report(stats: List[ArticleStats]) -> str:
        """Краткий отчет для уведомлений"""
        total_hourly = sum(s.hourly_orders for s in stats)
        total_daily = sum(s.daily_orders for s in stats)

        top_article = max(stats, key=lambda x: x.hourly_orders)

        return (
            f"🕐 {datetime.now().strftime('%H:%M')} | "
            f"За час: {total_hourly} | "
            f"За день: {total_daily} | "
            f"Топ: {top_article.article} ({top_article.hourly_orders})"
        )


class NotificationService:
    """Сервис уведомлений"""

    @staticmethod
    def send_to_console(report: str):
        """Отправка в консоль (для тестирования)"""
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60 + "\n")

    @staticmethod
    def save_to_file(report: str, filename: str = "ozon_reports.log"):
        """Сохранение в файл"""
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(report)
            f.write("\n" + "-" * 60 + "\n")
        logger.info(f"Отчет сохранен в {filename}")

    @staticmethod
    def simulate_telegram_send(report: str):
        """Имитация отправки в Telegram"""
        # Здесь можно добавить реальную интеграцию с Telegram Bot API
        short_report = report.split('\n')[0:5]
        print(f"[Telegram Bot] Отправка сообщения:")
        print("\n".join(short_report) + "\n...")

    @staticmethod
    def simulate_email_send(report: str, email: str = "admin@example.com"):
        """Имитация отправки email"""
        print(f"[Email] Отправка отчета на {email}")
        print(f"Тема: Ozon отчет за {datetime.now().strftime('%H:%M')}")
        print(f"Длина отчета: {len(report)} символов")


class OzonStatsBot:
    """Основной бот"""

    def __init__(self, notification_service: NotificationService):
        self.collector = StatsCollector()
        self.notifier = notification_service
        self.report_generator = ReportGenerator()
        self.is_running = False

    def should_run_now(self) -> bool:
        """Проверка, должно ли выполняться сейчас (8:30-23:30)"""
        now = datetime.now().time()
        start_time = time(8, 30)
        end_time = time(23, 30)
        return start_time <= now <= end_time

    async def collect_and_send_report(self, detailed: bool = True):
        """Сбор и отправка отчета"""
        if not self.should_run_now():
            logger.info("Вне рабочего времени (8:30-23:30)")
            return

        try:
            logger.info("Сбор статистики...")

            # Сбор данных
            stats = self.collector.collect_current_stats()
            top_performers = self.collector.get_top_performers(stats)

            # Генерация отчетов
            if detailed:
                report = self.report_generator.generate_hourly_report(stats, top_performers)
            else:
                report = self.report_generator.generate_summary_report(stats)

            # Отправка уведомлений
            self.notifier.send_to_console(report)
            self.notifier.save_to_file(report)
            self.notifier.simulate_telegram_send(report)

            # Каждый 3-й час отправляем email
            if datetime.now().hour % 3 == 0:
                self.notifier.simulate_email_send(report)

            logger.info("Отчет успешно отправлен")

        except Exception as e:
            logger.error(f"Ошибка при формировании отчета: {e}")

    async def run_scheduler(self):
        """Запуск планировщика"""
        self.is_running = True
        logger.info("Бот запущен. Ожидание 8:30 для начала работы...")

        while self.is_running:
            now = datetime.now()

            # Проверяем каждый час в :30
            if now.minute == 30 and self.should_run_now():
                await self.collect_and_send_report()
                # Ждем 61 минуту чтобы не выполнить дважды в одном часе
                await asyncio.sleep(61)
            else:
                # Каждую минуту проверяем время
                await asyncio.sleep(60)

    def stop(self):
        """Остановка бота"""
        self.is_running = False
        logger.info("Бот остановлен")


async def main():
    """Основная функция"""
    # Инициализация сервисов
    notifier = NotificationService()
    bot = OzonStatsBot(notifier)

    try:
        # Запускаем бота
        await bot.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        bot.stop()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        bot.stop()


if __name__ == "__main__":
    # Для тестирования можно запустить сразу один отчет
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Тестовый запуск одного отчета
        notifier = NotificationService()
        bot = OzonStatsBot(notifier)

        print("🚀 Тестовый запуск отчета...")
        asyncio.run(bot.collect_and_send_report())
    else:
        # Запуск бота в режиме планировщика
        asyncio.run(main())
