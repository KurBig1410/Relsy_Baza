from aiogram import BaseMiddleware
from datetime import datetime, time as dtime
import asyncio
from data.yc_service import fetch_and_store_yclients_data  # твоя основная функция

class YclientsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        asyncio.create_task(self.run_yc_updater())
        print("🚀 YclientsMiddleware запущен")

    async def __call__(self, handler, event, data):
        return await handler(event, data)

    async def run_yc_updater(self):
        """Периодически обновляет данные из YClients 2 раза в день."""
        while True:
            now = datetime.now().time()
            # Обновлять только утром и вечером
            if dtime(9, 0) <= now <= dtime(10, 0) or dtime(19, 0) <= now <= dtime(20, 0):
                try:
                    print("📊 Запуск обновления данных с YClients")
                    await fetch_and_store_yclients_data()
                    print("✅ Обновление завершено")
                except Exception as e:
                    print(f"❌ Ошибка при обновлении данных: {e}")
                await asyncio.sleep(3600)  # Ждём 1 час, чтобы не повторилось в том же окне
            else:
                await asyncio.sleep(300)  # Проверяем каждые 5 минут