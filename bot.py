import asyncio
import csv
import os
import threading

from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана")

CHANNEL_ID = "@serdechnyy_marketolog"
GIFT_LINK = "https://chatgpt.com/g/g-69af1c4e51f0819195f77b3237fe1ca1-tredmen"

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def save_user(user):
    file_name = "users.csv"
    file_exists = os.path.exists(file_name)

    with open(file_name, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["user_id", "username", "first_name"])

        writer.writerow([
            user.id,
            user.username if user.username else "",
            user.first_name if user.first_name else ""
        ])


@dp.message(CommandStart())
async def start(message: Message):
    save_user(message.from_user)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton(text="Готово", callback_data="check_sub")]
        ]
    )

    await message.answer(
        "Привет! 👋\n\n"
        "Хочешь писать посты в Threads быстрее и получать больше вовлечения? 🔥\n\n"
        "Я сделала бота, который:\n"
        "— даёт сильные идеи под твою тему\n"
        "— собирает цепляющую структуру\n"
        "— оформляет текст так, чтобы его не пролистывали\n\n"
        "👇 Забирай доступ:\n\n"
        "1. Подпишись на канал\n"
        "2. Нажми «Готово»",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                "🔥 Супер! Вот твой подарок:\n\n"
                f"👉 {GIFT_LINK}"
            )
            await callback.answer()
        else:
            await callback.answer("Сначала подпишись на канал ❗", show_alert=True)

    except Exception as e:
        await callback.answer("Не удалось проверить подписку. Проверь настройки канала.", show_alert=True)
        print(f"Ошибка проверки подписки: {e}")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    asyncio.run(main())
