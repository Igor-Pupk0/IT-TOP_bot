import aiogram
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from src.bot.core.logs import logger

start_router = aiogram.Router()

@start_router.message(Command("start"))
async def start(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) ввел команду /start")

    text, keyboard = generate_start_message()

    await message.answer(
        text=text, 
        reply_markup=keyboard,
        parse_mode="HTML"
    )


def generate_start_message() -> str:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        aiogram.types.KeyboardButton(text="📅 Раписание"),
        aiogram.types.KeyboardButton(text="🕵🏿‍♂️ Профиль"),
        aiogram.types.KeyboardButton(text="📔 ДЗ"),
        aiogram.types.KeyboardButton(text="5️⃣ Оценки"),
        aiogram.types.KeyboardButton(text="🐥 Разное"),
        aiogram.types.KeyboardButton(text="🌐 О боте")
    )
    keyboard.adjust(3, 3)
    text = f"Привет! Это бот журнал, здесь ты можешь посмотреть почти все, что связано с учебой."
    return (text, keyboard.as_markup(resize_keyboard=True))