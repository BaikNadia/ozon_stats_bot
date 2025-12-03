"""
Модуль для работы с PostgreSQL
"""
import asyncpg
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Модель товара"""
    article_code: str
    article_name: str
    current_price: float
    created_at: datetime
    updated_at: datetime


@dataclass
class Order:
    """Модель заказа"""
    article_code: str
    order_time: datetime
    hour_of_day: int


@dataclass
class DailyStat:
    """Модель дневной статистики"""
    article_code: str
    stat_date: date
    hour: int
    orders_count: int


@dataclass
class BotUser:
    """Модель пользователя бота"""
    chat_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    subscribed_to_daily: bool
    subscribed_to_alerts: bool
    created_at: datetime
    last_active: datetime


class Database:
    """Класс для работы с базой данных"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Подключение к базе данных"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10
            )
            logger.info(f"Подключено к базе данных {self.database}")

            # Проверяем соединение
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")

            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    async def close(self):
        """Закрытие соединения"""
        if self.pool:
            await self.pool.close()
            logger.info("Соединение с БД закрыто")

    # Методы для работы с товарами
    async def save_article(self, article_code: str, article_name: str, price: float) -> bool:
        """Сохранение товара в БД"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO articles (article_code, article_name, current_price)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (article_code) 
                    DO UPDATE SET 
                        article_name = EXCLUDED.article_name,
                        current_price = EXCLUDED.current_price,
                        updated_at = CURRENT_TIMESTAMP
                """, article_code, article_name, price)
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения товара: {e}")
            return False

    async def get_all_articles(self) -> List[Article]:
        """Получение всех товаров"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT article_code, article_name, current_price, 
                           created_at, updated_at 
                    FROM articles 
                    ORDER BY article_code
                """)

                return [
                    Article(
                        article_code=row['article_code'],
                        article_name=row['article_name'],
                        current_price=row['current_price'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ) for row in rows
                ]
        except Exception as e:
            logger.error(f"Ошибка получения товаров: {e}")
            return []

    # Методы для работы с заказами
    async def save_order(self, article_code: str, order_time: datetime) -> bool:
        """Сохранение заказа"""
        try:
            async with self.pool.acquire() as conn:
                hour_of_day = order_time.hour

                await conn.execute("""
                    INSERT INTO orders (article_code, order_time, hour_of_day)
                    VALUES ($1, $2, $3)
                """, article_code, order_time, hour_of_day)

                # Обновляем дневную статистику
                await self.update_daily_stats(
                    article_code=article_code,
                    stat_date=order_time.date(),
                    hour=hour_of_day
                )

                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения заказа: {e}")
            return False

    async def update_daily_stats(self, article_code: str, stat_date: date, hour: int):
        """Обновление дневной статистики"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO daily_stats (article_code, date, hour, orders_count)
                    VALUES ($1, $2, $3, 1)
                    ON CONFLICT (article_code, date, hour) 
                    DO UPDATE SET 
                        orders_count = daily_stats.orders_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                """, article_code, stat_date, hour)
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")

    async def get_hourly_stats(self, target_date: date, target_hour: int) -> List[DailyStat]:
        """Получение статистики за конкретный час"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT ds.article_code, ds.date, ds.hour, ds.orders_count,
                           a.article_name, a.current_price
                    FROM daily_stats ds
                    JOIN articles a ON ds.article_code = a.article_code
                    WHERE ds.date = $1 AND ds.hour = $2
                    ORDER BY ds.orders_count DESC
                """, target_date, target_hour)

                return [
                    DailyStat(
                        article_code=row['article_code'],
                        stat_date=row['date'],
                        hour=row['hour'],
                        orders_count=row['orders_count']
                    ) for row in rows
                ]
        except Exception as e:
            logger.error(f"Ошибка получения часовой статистики: {e}")
            return []

    async def get_daily_total(self, target_date: date) -> Dict[str, int]:
        """Получение общей статистики за день"""
        try:
            async with self.pool.acquire() as conn:
                # Общее количество за день
                rows = await conn.fetch("""
                    SELECT article_code, SUM(orders_count) as total_orders
                    FROM daily_stats
                    WHERE date = $1
                    GROUP BY article_code
                    ORDER BY total_orders DESC
                """, target_date)

                return {row['article_code']: row['total_orders'] for row in rows}
        except Exception as e:
            logger.error(f"Ошибка получения дневной статистики: {e}")
            return {}

    # Методы для работы с пользователями
    async def save_user(self, chat_id: int, username: Optional[str] = None,
                        first_name: Optional[str] = None, last_name: Optional[str] = None) -> bool:
        """Сохранение/обновление пользователя"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bot_users (chat_id, username, first_name, last_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (chat_id) 
                    DO UPDATE SET 
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        last_active = CURRENT_TIMESTAMP,
                        is_active = TRUE
                """, chat_id, username, first_name, last_name)
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователя: {e}")
            return False

    async def get_active_users(self) -> List[BotUser]:
        """Получение активных пользователей"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT chat_id, username, first_name, last_name,
                           is_active, subscribed_to_daily, subscribed_to_alerts,
                           created_at, last_active
                    FROM bot_users
                    WHERE is_active = TRUE AND subscribed_to_daily = TRUE
                    ORDER BY chat_id
                """)

                return [
                    BotUser(
                        chat_id=row['chat_id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        is_active=row['is_active'],
                        subscribed_to_daily=row['subscribed_to_daily'],
                        subscribed_to_alerts=row['subscribed_to_alerts'],
                        created_at=row['created_at'],
                        last_active=row['last_active']
                    ) for row in rows
                ]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []

    async def update_user_subscription(self, chat_id: int, subscription_type: str, value: bool) -> bool:
        """Обновление подписки пользователя"""
        try:
            async with self.pool.acquire() as conn:
                if subscription_type == 'daily':
                    await conn.execute("""
                        UPDATE bot_users 
                        SET subscribed_to_daily = $2,
                            last_active = CURRENT_TIMESTAMP
                        WHERE chat_id = $1
                    """, chat_id, value)
                elif subscription_type == 'alerts':
                    await conn.execute("""
                        UPDATE bot_users 
                        SET subscribed_to_alerts = $2,
                            last_active = CURRENT_TIMESTAMP
                        WHERE chat_id = $1
                    """, chat_id, value)

                return True
        except Exception as e:
            logger.error(f"Ошибка обновления подписки: {e}")
            return False

    async def save_sent_report(self, chat_id: int, report_type: str, report_content: str):
        """Сохранение отправленного отчета"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO sent_reports (chat_id, report_type, report_content)
                    VALUES ($1, $2, $3)
                """, chat_id, report_type, report_content)
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")
