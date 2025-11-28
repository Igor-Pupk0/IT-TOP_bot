###
### Он проверяет и отправляет сообщение, если до того
### как домашка просрочилась осталось: 24 часа, 12 часов
### 6, 1 час
###


from ..core.storage import ALMOST_EXPIRED_HOMEWORK_NOTIFICATION_TIMEOUT_SEC, db_obj, settings_db_obj
from ..core.states import get_user_status
from ..modules.authorization import load_user
from ..core.logs import logger
import threading
import telebot
import time
import datetime

notification_prefix = """❗️Уведомление❗️

"""

@load_user
def check_homework(bot: telebot.TeleBot, user_id: int):
    user_states = get_user_status(user_id)

    homework_count = get_user_status(user_id).API.get_homework_count()
    
    if homework_count == 500 or homework_count == {}:
        return
    
    pages_count = homework_count["type_3"] // 6 + 2
    for page in range(1, pages_count):
        actual_homeworks = user_states.API.get_homework(3, page)

        if actual_homeworks == 500:
            continue

        resp = settings_db_obj.get_all_settings_by_telegram_id(user_id)

        if resp.get("get_almost_expired_hw_notifictions") == 0:
            continue

        for homework in actual_homeworks:
            deadline = homework.get("overdue_time")
            time_to_expire = datetime.datetime.fromisoformat(deadline) - datetime.datetime.today()
            if time_to_expire.days in [0, 1] or time_to_expire.days == None:
                hours = time_to_expire.seconds / 60 / 60
                days = time_to_expire.days
                try:
                    if hours < 16.5 and hours > 17.5 and (days == 0 or days == None):
                        bot.send_message(user_id,
                                            notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>17 часов</b>",
                                            parse_mode="HTML")
                    elif hours < 12.5 and hours > 11.5 and days == 1:
                        bot.send_message(user_id,
                                            notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось <b>полтора дня</b>",
                                            parse_mode="HTML")
                    elif hours < 6.5 and hours > 5.5 and (days == 0 or days == None):
                            bot.send_message(user_id,
                                                notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>6 часов</b>, бедыч!",
                                                parse_mode="HTML")
                        
                except Exception as e:
                    if "chat not found" in str(e):
                        logger.warning(f"При рассылке уведомлении о скорой просрочке дз, чат с id {user_id} не был найден")
                        continue
                    elif "user is deactivated" in str(e):
                        logger.warning(f"При рассылке уведомлении о скорой просрочке дз, аккаунт с id {user_id} был деактивирован")
                        continue
                    elif "bot was blocked by the user" in str(e):
                        logger.warning(f"При рассылке уведомлении о скорой просрочке дз, аккаунт с id {user_id} заблокировал бота")
                        continue

                    logger.critical(f"Ошибка при рассылке уведомлении о скорой просрочке дз: ", e)
                    continue


def check_homework_cycle(bot: telebot.TeleBot):
    while True:
        time.sleep(ALMOST_EXPIRED_HOMEWORK_NOTIFICATION_TIMEOUT_SEC)
        logger.info("Начинаю рассылку уведомлении о скорой просрочке дз")
        users_ids = db_obj.get_all_telegram_ids()

        for user_id in users_ids:
            check_homework(bot, user_id[0])
            time.sleep(1)
        logger.info("Рассылка уведомлении о скорой просрочке дз завершена")
        

def init_almost_expired_homework_notification(bot):
    threading.Thread(target=check_homework_cycle, args=[bot], daemon=True).start()