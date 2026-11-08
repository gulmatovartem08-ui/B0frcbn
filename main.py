import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Добавь переменную BOT_TOKEN в настройках сервера.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- ОБРАБОТЧИК /start ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    bot_username = (await bot.get_me()).username
    
    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я бот для автоматизации твоего профиля.\n"
        "Посмотри, как меня использовать, в моем ТГК: @Pas0n\n\n"
        "⚙️ <b>Доступные команды:</b>\n"
        "/spam [текст] [кол-во] — отправить сообщение много раз (до 1000)\n"
        "/del — удалить сообщение (ответь на него этой командой)\n\n"
        "👇 <i>Чтобы я начал работать, добавь меня в свой профиль!</i>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Инструкция в ТГК", url="https://t.me/pas0n")],
        [InlineKeyboardButton(text="➕ Добавить в профиль", url="tg://settings/edit")]
    ])

    await message.answer(text, reply_markup=keyboard)


# --- ОБРАБОТЧИК /spam ---
@dp.message(Command("spam"))
async def cmd_spam(message: Message):
    if message.chat.type != "private":
        return await message.answer("❌ Эта команда работает только в личных чатах!")

    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        return await message.answer("⚠️ <b>Использование:</b>\n<code>/spam [текст] [кол-во]</code>\nПример: <code>/spam Привет 100</code>")

    text_to_spam = args[1]
    try:
        count = int(args[2])
    except ValueError:
        return await message.answer("⚠️ Количество должно быть числом!")

    # Ставим жесткий лимит 1000, как ты просил
    if count > 1000:
        count = 1000
        await message.answer("⚠️ Установлен максимум 1000 сообщений.")
    
    if count < 1:
        return await message.answer("⚠️ Количество должно быть больше 0.")

    await message.answer(f"🚀 Начинаю спам: {count} раз...")

    # Отправляем сообщения
    for i in range(count):
        try:
            await message.answer(text_to_spam)
            # Пауза 0.05 сек. Если убрать совсем — Telegram выдаст 429 ошибку и бот крашнется
            await asyncio.sleep(0.05) 
        except Exception as e:
            logging.error(f"Ошибка при спаме (возможно, лимиты Telegram): {e}")
            # Если Telegram забанил запрос, прерываем цикл, чтобы бот не висел
            break 


# --- ОБРАБОТЧИК /del ---
@dp.message(Command("del"))
async def cmd_del(message: Message):
    if message.chat.type != "private":
        return await message.answer("❌ Эта команда работает только в личных чатах!")

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
            return
        except Exception:
            return await message.answer("❌ Не удалось удалить сообщение. Возможно, оно слишком старое или нет прав.")

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await message.delete()
    except Exception:
        await message.answer("❌ Не удалось удалить предыдущее сообщение.")


# --- ЗАПУСК ---
async def main():
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")