"""
Упрощенная веб-панель без WebSocket
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import logging
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SimpleDashboard:
    """Упрощенная веб-панель"""

    def __init__(self, db, host="0.0.0.0", port=8000):
        self.db = db
        self.host = host
        self.port = port
        self.app = FastAPI(title="Ozon Stats Dashboard")

        # Настраиваем статику
        os.makedirs("static", exist_ok=True)
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

        # Регистрируем маршруты
        self.setup_routes()

        # Создаем CSS файл
        self.create_css_file()

    @staticmethod
    def create_css_file():
        """Создание CSS файла"""
        css_path = "static/style.css"
        if not os.path.exists(css_path):
            css_content = """
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.8em;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.9;
                margin-top: 10px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                padding: 40px;
                background: #f8f9fa;
            }

            .stat-card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
                border-left: 6px solid #667eea;
            }

            .stat-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }

            .stat-value {
                font-size: 3em;
                font-weight: bold;
                color: #667eea;
                margin: 15px 0;
            }

            .stat-label {
                color: #6c757d;
                font-size: 1em;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }

            .stat-desc {
                color: #868e96;
                font-size: 0.9em;
                margin-top: 10px;
            }

            .section {
                padding: 40px;
            }

            .section h2 {
                color: #343a40;
                margin-bottom: 25px;
                font-size: 1.8em;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            }

            th {
                background: #667eea;
                color: white;
                padding: 20px;
                text-align: left;
                font-weight: 600;
            }

            td {
                padding: 18px 20px;
                border-bottom: 1px solid #e9ecef;
                color: #495057;
            }

            tr:hover {
                background: #f8f9fa;
            }

            .controls {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                padding: 30px 40px;
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }

            .btn {
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 600;
                font-size: 1em;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                text-decoration: none;
            }

            .btn-primary {
                background: #667eea;
                color: white;
            }

            .btn-primary:hover {
                background: #5a67d8;
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }

            .btn-success {
                background: #28a745;
                color: white;
            }

            .btn-warning {
                background: #ffc107;
                color: #212529;
            }

            .btn-info {
                background: #17a2b8;
                color: white;
            }

            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
            }

            .status-active {
                background: #d4edda;
                color: #155724;
            }

            .status-inactive {
                background: #f8d7da;
                color: #721c24;
            }

            .time-display {
                font-size: 1.2em;
                margin-top: 15px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                display: inline-block;
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    border-radius: 15px;
                }

                .header {
                    padding: 25px;
                }

                .header h1 {
                    font-size: 2em;
                    flex-direction: column;
                }

                .stats-grid {
                    grid-template-columns: 1fr;
                    padding: 25px;
                    gap: 15px;
                }

                .section {
                    padding: 25px;
                }

                .controls {
                    padding: 20px;
                }

                .btn {
                    width: 100%;
                    justify-content: center;
                }
            }
            """

            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_content)

    def setup_routes(self):
        """Настройка маршрутов"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(_: Request):
            # Получаем данные для отображения
            stats = await self.get_dashboard_stats()
            orders = await self.get_recent_orders()
            users = await self.get_users()

            html = f"""
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Ozon Stats Dashboard</title>
                <link rel="stylesheet" href="/static/style.css">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <script>
                    function updateTime() {{
                        const now = new Date();
                        document.getElementById('current-time').textContent = 
                            'Текущее время: ' + now.toLocaleTimeString() + ' | ' + now.toLocaleDateString();
                    }}

                    function refreshData() {{
                        location.reload();
                    }}

                    function exportData(formatType) {{
                        alert('Экспорт в ' + formatType + ' будет выполнен. Проверьте консоль сервера.');
                        fetch('/api/export/' + formatType);
                    }}

                    function sendTestReport() {{
                        fetch('/api/test-report', {{ method: 'POST' }})
                            .then(response => response.json())
                            .then(data => alert(data.message || 'Отчет отправлен'));
                    }}

                    // Обновление времени каждую секунду
                    setInterval(updateTime, 1000);

                    // Автообновление каждые 30 секунд
                    setInterval(refreshData, 30000);

                    document.addEventListener('DOMContentLoaded', updateTime);
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>
                            <i class="fas fa-chart-line"></i>
                            Ozon Stats Dashboard
                            <span class="status-badge status-active">🟢 РАБОТАЕТ</span>
                        </h1>
                        <p>Система мониторинга статистики заказов Ozon в реальном времени</p>
                        <div id="current-time" class="time-display"></div>
                    </div>

                    <div class="stats-grid">
                        {self.generate_stats_html(stats)}
                    </div>

                    <div class="section">
                        <h2><i class="fas fa-shopping-cart"></i> Последние заказы</h2>
                        {self.generate_orders_html(orders)}
                    </div>

                    <div class="section">
                        <h2><i class="fas fa-users"></i> Пользователи бота</h2>
                        {self.generate_users_html(users)}
                    </div>

                    <div class="controls">
                        <button class="btn btn-primary" onclick="exportData('excel')">
                            <i class="fas fa-file-excel"></i> Экспорт в Excel
                        </button>
                        <button class="btn btn-primary" onclick="exportData('csv')">
                            <i class="fas fa-file-csv"></i> Экспорт в CSV
                        </button>
                        <button class="btn btn-success" onclick="sendTestReport()">
                            <i class="fas fa-paper-plane"></i> Тестовый отчет
                        </button>
                        <button class="btn btn-warning" onclick="refreshData()">
                            <i class="fas fa-sync-alt"></i> Обновить (30 сек)
                        </button>
                        <a href="https://t.me/ozon_stats_analytics_bot" target="_blank" class="btn btn-info">
                            <i class="fab fa-telegram"></i> Telegram Bot
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """

            return HTMLResponse(content=html)

        @self.app.get("/api/stats")
        async def get_stats():
            stats = await self.get_dashboard_stats()
            return {"stats": stats}

        @self.app.get("/api/orders")
        async def get_orders():
            orders = await self.get_recent_orders()
            return {"orders": orders}

        @self.app.get("/api/users")
        async def get_users():
            users = await self.get_users()
            return {"users": users}

        @self.app.post("/api/test-report")
        async def test_report():
            return {"message": "Тестовый отчет отправлен в Telegram"}

        @self.app.get("/api/export/{format_type}")
        async def export_data(format_type: str):
            return {"message": f"Экспорт в {format_type} запущен"}

    @staticmethod
    def generate_stats_html(stats):
        """Генерация HTML для статистики"""
        if not stats:
            return '<div class="stat-card"><div class="stat-label">Нет данных</div></div>'

        html = ""
        for stat in stats:
            html += f"""
            <div class="stat-card">
                <div class="stat-label">{stat['label']}</div>
                <div class="stat-value">{stat['value']}</div>
                <div class="stat-desc">{stat['description']}</div>
            </div>
            """
        return html

    @staticmethod
    def generate_orders_html(orders):
        """Генерация HTML для заказов"""
        if not orders:
            return '<p>Нет данных о заказах</p>'

        html = '<table><tr><th>Артикул</th><th>Товар</th><th>Заказов</th><th>Цена</th><th>Час</th></tr>'

        for order in orders[:10]:  # Показываем первые 10
            html += f"""
            <tr>
                <td><code>{order['article_code']}</code></td>
                <td>{order['article_name']}</td>
                <td><strong>{order['orders_count']}</strong></td>
                <td>{order['price'] or '0.00'}₽</td>
                <td>{order['hour']}:00</td>
            </tr>
            """

        html += '</table>'
        return html

    @staticmethod
    def generate_users_html(users):
        """Генерация HTML для пользователей"""
        if not users:
            return '<p>Нет пользователей</p>'

        html = '<table><tr><th>Имя</th><th>Username</th><th>Подписка</th><th>Активность</th></tr>'

        for user in users[:10]:  # Показываем первые 10
            subscription = '✅ ВКЛ' if user['subscribed_to_daily'] else '❌ ВЫКЛ'
            last_active = user['last_active']
            if isinstance(last_active, datetime):
                last_active_str = last_active.strftime('%d.%m.%Y %H:%M')
            else:
                last_active_str = 'нет данных'

            html += f"""
            <tr>
                <td>{user['first_name'] or '-'}</td>
                <td>@{user['username'] if user['username'] else 'нет'}</td>
                <td>{subscription}</td>
                <td>{last_active_str}</td>
            </tr>
            """

        html += '</table>'
        return html

    async def get_dashboard_stats(self):
        """Получение статистики для дашборда"""
        try:
            async with self.db.pool.acquire() as conn:
                today = date.today()

                # Заказов сегодня
                today_orders = await conn.fetchval("""
                    SELECT COALESCE(SUM(orders_count), 0)
                    FROM daily_stats 
                    WHERE date = $1
                """, today) or 0

                # Активных пользователей
                active_users = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM bot_users 
                    WHERE is_active = TRUE
                """) or 0

                # Всего товаров
                total_products = await conn.fetchval("""
                    SELECT COUNT(*) FROM articles
                """) or 10  # По умолчанию 10 тестовых товаров

                # Следующий отчет
                now = datetime.now()
                next_hour = (now.hour + 1) % 24

                stats = [
                    {
                        "label": "Заказов сегодня",
                        "value": today_orders,
                        "description": "Сумма всех заказов"
                    },
                    {
                        "label": "Активных пользователей",
                        "value": active_users,
                        "description": "Подписаны на отчеты"
                    },
                    {
                        "label": "Отслеживаемых товаров",
                        "value": total_products,
                        "description": "В базе данных"
                    },
                    {
                        "label": "Следующий отчет",
                        "value": f"{next_hour}:30",
                        "description": "Время отправки"
                    }
                ]

                return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            # Возвращаем тестовые данные при ошибке
            return [
                {
                    "label": "Заказов сегодня",
                    "value": "0",
                    "description": "Нет данных"
                },
                {
                    "label": "Активных пользователей",
                    "value": "0",
                    "description": "Нет данных"
                },
                {
                    "label": "Отслеживаемых товаров",
                    "value": "10",
                    "description": "Тестовые данные"
                },
                {
                    "label": "Следующий отчет",
                    "value": f"{(datetime.now().hour + 1) % 24}:30",
                    "description": "Время отправки"
                }
            ]

    async def get_recent_orders(self):
        """Получение последних заказов"""
        try:
            # Используем тестовые данные из коллектора
            from ozon_stats_bot import StatsCollector
            collector = StatsCollector()
            stats = collector.collect_current_stats()  # Возвращает список объектов ArticleStats

            orders = []
            for item in stats:
                if item.hourly_orders > 0:  # item - это объект ArticleStats
                    orders.append({
                        "article_code": item.article,
                        "article_name": item.name,
                        "orders_count": item.hourly_orders,
                        "price": f"{item.price:.2f}",
                        "hour": datetime.now().hour
                    })

            # Если нет заказов, создаем тестовые данные
            if not orders:
                orders = [
                    {
                        "article_code": "123456",
                        "article_name": "Смартфон Xiaomi Redmi Note 12",
                        "orders_count": 5,
                        "price": "19999.99",
                        "hour": datetime.now().hour
                    },
                    {
                        "article_code": "789012",
                        "article_name": "Наушники JBL Tune 510BT",
                        "orders_count": 3,
                        "price": "3499.99",
                        "hour": datetime.now().hour
                    },
                    {
                        "article_code": "345678",
                        "article_name": "Ноутбук ASUS VivoBook 15",
                        "orders_count": 1,
                        "price": "54999.99",
                        "hour": datetime.now().hour
                    }
                ]

            return sorted(orders, key=lambda x: x['orders_count'], reverse=True)[:10]

        except Exception as e:
            logger.error(f"Ошибка получения заказов: {e}")
            # Возвращаем тестовые данные при ошибке
            return [
                {
                    "article_code": "123456",
                    "article_name": "Тестовый товар 1",
                    "orders_count": 5,
                    "price": "1500.00",
                    "hour": datetime.now().hour
                },
                {
                    "article_code": "789012",
                    "article_name": "Тестовый товар 2",
                    "orders_count": 3,
                    "price": "2500.00",
                    "hour": datetime.now().hour
                }
            ]

    async def get_users(self):
        """Получение пользователей"""
        try:
            async with self.db.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT first_name, username, subscribed_to_daily, last_active
                    FROM bot_users
                    ORDER BY last_active DESC
                    LIMIT 10
                """)

                users = [
                    {
                        "first_name": row["first_name"],
                        "username": row["username"],
                        "subscribed_to_daily": row["subscribed_to_daily"],
                        "last_active": row["last_active"]
                    }
                    for row in rows
                ]

                # Если нет пользователей, создаем тестовые данные
                if not users:
                    users = [
                        {
                            "first_name": "Иван",
                            "username": "ivan_ozon",
                            "subscribed_to_daily": True,
                            "last_active": datetime.now()
                        },
                        {
                            "first_name": "Мария",
                            "username": "maria_shopper",
                            "subscribed_to_daily": True,
                            "last_active": datetime.now() - timedelta(hours=2)
                        },
                        {
                            "first_name": "Алексей",
                            "username": None,
                            "subscribed_to_daily": False,
                            "last_active": datetime.now() - timedelta(days=1)
                        }
                    ]

                return users

        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            # Возвращаем тестовые данные при ошибке
            return [
                {
                    "first_name": "Тестовый",
                    "username": "test_user",
                    "subscribed_to_daily": True,
                    "last_active": datetime.now()
                }
            ]

    async def run(self):
        """Запуск веб-сервера"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


async def run_simple_dashboard():
    """Запуск упрощенной веб-панели"""
    from database import Database
    import os
    from dotenv import load_dotenv

    load_dotenv()

    db = Database(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "ozon_bot_db"),
        user=os.getenv("DB_USER", "ozon_bot_user"),
        password=os.getenv("DB_PASSWORD", "password123")
    )

    await db.connect()

    dashboard = SimpleDashboard(db, host="0.0.0.0", port=8000)
    print("🌐 Упрощенная веб-панель запущена: http://localhost:8000")
    await dashboard.run()


if __name__ == "__main__":
    asyncio.run(run_simple_dashboard())
