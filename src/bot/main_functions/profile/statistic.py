import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...auth.authorization_callbacks import check_auth
from ...core.logs import logger
from ...core.states import get_user_status
from ...core.keyboards import make_return_button
from ...core.journal_500 import get_500_message

static_router = aiogram.Router()

@static_router.callback_query(F.data == 'show_statistic')
@check_auth
async def handle_message(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) выбрал посмотреть статистику")

    stats_keyboard = InlineKeyboardBuilder()
    stats_keyboard.add(make_return_button())

    user = get_user_status(call.from_user.id)
    user_info = await user.API.get_user_info()
    if user_info == 500:
      await call.message.answer(get_500_message(call.message))
      return
    user_leader_stats = await user.API.get_leader_tables_stats()

    ### Дикое извлечение данных
    full_name = user_info["full_name"]
    name = full_name.split()[1]
    group_name = user_info["group_name"]
    photo_url = user_info["photo"]

    topcoins = user_info["gaming_points"][0]["points"]
    topgems = user_info["gaming_points"][1]["points"]

    leader_group_top = user_leader_stats.get("group")
    leader_strean_top = user_leader_stats.get("stream")

    user_homework = await user.API.get_homework_count()

    homework_done_procent = round((user_homework["type_1"] / user_homework["type_4"]) * 100)
    visits_procent = await user.API.get_student_visits_procent()

    await call.answer()
    await call.message.answer(text=f"""\
Статистика:
Привет, <b>{full_name}</b>
Группа: {group_name}

Баланс:
- <b>{topcoins}</b> Топкоинов 💸
- <b>{topgems}</b> Топгемов  💎
Всего: {topcoins + topgems}

Место в топах:
- В группе: <b>{leader_group_top["studentPosition"]}</b> из {leader_group_top["totalCount"]}
- В потоке: <b>{leader_strean_top["studentPosition"]}</b>

Сделано <b>{homework_done_procent}%</b> всех дз
Посещаемость за все время: <b>{visits_procent}%</b>
Фотокарточка профиля: <a href='{photo_url}'>ТЫК</a>
""", 
                    reply_markup=stats_keyboard.as_markup(),
                    parse_mode="HTML")