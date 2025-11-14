import telebot
from .authorization import check_auth
from ..core.logs import logger
from ..core.states import get_user_status, delete_user_status
from ..core.keyboards import make_return_button
from ..core.storage import db_obj


def setup_stats_module(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == 'show_statistic')
    @check_auth
    def handle_message(call: telebot.types.CallbackQuery):
        logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) выбрал посмотреть статистику")

        stats_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        stats_keyboard.add(make_return_button())

        user = get_user_status(call.from_user.id)
        user_info = user.API.get_user_info()
        user_leader_stats = user.API.get_leader_tables_stats()

        ### Дикое извлечение данных
        full_name = user_info["full_name"]
        name = full_name.split()[1]
        group_name = user_info["group_name"]
        photo_url = user_info["photo"]

        topcoins = user_info["gaming_points"][0]["points"]
        topgems = user_info["gaming_points"][1]["points"]

        leader_group_top = user_leader_stats.get("group")
        leader_strean_top = user_leader_stats.get("stream")

        user_homework = user.API.get_homework_count()

        homework_done_procent = round((user_homework["type_1"] / user_homework["type_4"]) * 100)
        visits_procent = user.API.get_student_visits_procent()

        bot.send_message(call.message.chat.id,
f"""\
Статистика:
Ку, <b>{full_name}</b>
Группа: {group_name}

Баланс:
  - <b>{topcoins}</b> Топкоинов 💸
  - <b>{topgems}</b> Топгемов  💎
  Всего: {topcoins + topgems}

Место в топах:
  - В группе: <b>{leader_group_top["studentPosition"]}</b> из {leader_group_top["totalCount"]}
  - В потоке: <b>{leader_strean_top["studentPosition"]}</b>

Сделано <b>{homework_done_procent}%</b> всех дз
Посещаемость: <b>{visits_procent}%</b>
Фотокарточка профиля: <a href='{photo_url}'>ТЫК</a>
""", 
                        reply_markup=stats_keyboard,
                        parse_mode="HTML")


def logout(telegram_id):
    logger.info(f"Пользователь (???:{telegram_id}) был кикнут из аккаунта")
    db_obj.delete_user_by_telegram_id(telegram_id)
    delete_user_status(telegram_id)