import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import logging

API_TOKEN = "BOT_ID"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


EBBINGHAUS_INTERVALS = [
    5 * 60,       # 5 минут
    30 * 60,      # 30 минут
    12 * 60 * 60, # 12 часов
    24 * 60 * 60, # 1 день
    2 * 24 * 60 * 60, # 2 дня
    7 * 24 * 60 * 60  # 7 дней
]


user_tasks = {}

async def send_reminders(user_id: int, title: str):
    for interval in EBBINGHAUS_INTERVALS:
        await asyncio.sleep(interval)
        try:
            await bot.send_message(user_id, f"⏰ Напоминание: {title}")
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления: {e}")
            break


@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я бот для запоминания по кривой Эббингауза.\n"
        "Используй команды:\n"
        "`/set <название>` – запустить напоминания\n"
        "`/stop` – остановить напоминания\n",
        parse_mode="Markdown"
    )


@dp.message(Command("set"))
async def set_reminder(message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажи название напоминания. Пример: `/set Английский`")
        return

    title = args[1]


    if user_id in user_tasks:
        user_tasks[user_id]["task"].cancel()

    task = asyncio.create_task(send_reminders(user_id, title))
    user_tasks[user_id] = {"task": task, "title": title}

    await message.answer(f"✅ Запустил напоминания по теме: {title}")


@dp.message(Command("stop"))
async def stop_reminder(message: Message):
    user_id = message.from_user.id
    if user_id in user_tasks:
        user_tasks[user_id]["task"].cancel()
        del user_tasks[user_id]
        await message.answer("❌ Напоминания остановлены")
    else:
        await message.answer("У тебя нет активных напоминаний.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
