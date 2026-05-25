import aiogram
from aiogram import F
from .core.logs import logger
from .core.keyboards import make_return_keyboard
from ..storage import SUPPORT_USERNAME

about_router = aiogram.Router()

@about_router.message(F.text == "🌐 О боте")
async def handle_message(message: aiogram.types.Message):
    logger.info(f"Пользователь ({message.from_user.username}:{message.from_user.id}) выбрал '{message.text}'")

    await message.answer(
        text=f"""\
Этот бот создан для того, чтобы сделать взаимодействие с функциями журнала более простым и быстрым, ну или расширить их. \
Моя задача была сделать бота, который мог бы предоставить весь основной функционал журнала, который может понадобится в эту минуту без \
долгого входа в сам журнал. Также благодаря изучению API журнала мне удалось расширить некоторый функционал ну или добавить новый, которого нету на сайте. 
Например: 
  - Автооценка пар
  - Напоминалка о сдаче дз
  - Просмотр фото в лидербордах
  - Расширенное поле для текстового ответа в дз

Сюда мне можно закинуть респект (Кириллу из КБ 25/1), написать про баги или идеи для функционала: <a href='t.me/{SUPPORT_USERNAME}'>Кликабельно</a>
Его исходный код доступен по этой ссылке: https://github.com/Igor-Pupk0/IT-TOP_bot
""", 
                    reply_markup=make_return_keyboard(),
                    parse_mode="HTML")
