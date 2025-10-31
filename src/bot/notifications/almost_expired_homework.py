###
### Он проверяет и отправляет сообщение, если до того
### как домашка просрочилась осталось: 24 часа, 12 часов
### 6, 1 час
###


from ..core.storage import ALMOST_EXPIRED_HOMEWORK_NOTIFICATION_TIMEOUT_SEC, db_obj
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
    
    if homework_count == 500:
        return
    
    pages_count = homework_count["type_3"] // 6 + 2
    for page in range(1, pages_count):
        actual_homeworks = user_states.API.get_homework(3, page)

        if actual_homeworks == 500:
            continue

        for homework in actual_homeworks:
            deadline = homework.get("overdue_time")
            time_to_expire = datetime.datetime.fromisoformat(deadline) - datetime.datetime.today()
            if time_to_expire.days == 0 or time_to_expire.days == None:
                hours = time_to_expire.seconds / 60 / 60
                try:
                    if hours < 24 and hours > 23:
                        bot.send_message(user_id,
                                            notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>24 часов</b>",
                                            parse_mode="HTML")
                    elif hours < 12.5 and hours > 11.5:
                        bot.send_message(user_id,
                                            notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>12 часов</b>",
                                            parse_mode="HTML")
                    elif hours < 6.5 and hours > 5.5:
                            bot.send_message(user_id,
                                                notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>6 часов</b>, бедыч!",
                                                parse_mode="HTML")
                    elif hours < 1.5:
                            bot.send_message(user_id, 
                                                notification_prefix + f"До просрочки дз по <i>{homework.get("name_spec")}</i> осталось около <b>часа!</b>",
                                                parse_mode="HTML")
                        
                except Exception as e:
                    if "chat not found" in str(e):
                        logger.warning(f"При рассылке уведомлении о скорой просрочке дз, чат с id {id[0]} не был найден")
                        continue

                    logger.critical(f"Ошибка при рассылке уведомлении о скорой просрочке дз: ", e)


def check_homework_cycle(bot: telebot.TeleBot):
    while True:
        logger.info("Начинаю рассылку уведомлении о скорой просрочке дз")
        users_ids = db_obj.get_all_telegram_ids()

        for user_id in users_ids:
            check_homework(bot, user_id[0])
            time.sleep(1)
        logger.info("Рассылка уведомлении о скорой просрочке дз завершена")
        time.sleep(ALMOST_EXPIRED_HOMEWORK_NOTIFICATION_TIMEOUT_SEC)

def init_almost_expired_homework_notification(bot):
    threading.Thread(target=check_homework_cycle, args=[bot], daemon=True).start()