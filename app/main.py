from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.config.config_loader import main_config
from database.db_session_maker import close_db_connection, initialize_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.channel import channel_router
from services.daily_post_handler import DailyPostHandler
from services.telethon_client import client_instance

# Инициализация расписания
scheduler = AsyncIOScheduler()


async def daily_task():
    print("Daily task!!!")


async def startup_event():
    # Подключаем Telethon клиент
    await client_instance.connect()
    await initialize_database()

    # Запускаем расписание задач
    daily_post_handler = DailyPostHandler(client_instance, days_to_keep=main_config.daily_post_handler.days_to_keep)
    # scheduler.add_job(daily_post_handler.run_daily_tasks, "cron", minute="*/1")
    scheduler.add_job(daily_post_handler.run_daily_tasks, "cron", hour=0, minute=0)
    scheduler.start()

    print("Scheduler started and daily tasks scheduled")


async def shutdown_event():
    # Отключаем Telethon клиент
    await client_instance.disconnect()
    await close_db_connection()
    # Останавливаем расписание
    scheduler.shutdown()


tags_metadata = [
    # {"name": "users", "description": "Operations with users. Create and update users."},
]


app = FastAPI(
    title="Essence Bot Parser",
    on_startup=[startup_event],
    on_shutdown=[shutdown_event],
    tags_metadata=tags_metadata,
)
app.include_router(channel_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization"],
)
