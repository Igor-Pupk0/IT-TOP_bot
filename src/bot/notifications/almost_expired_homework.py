###
### Он проверяет и отправляет сообщение, если до того
### как домашка просрочилась осталось: полтора дня, 17 часов (в 7 утра)
### и 6 часов (18 вечера)
###


from ...storage import db_obj, settings_db_obj, failed_403_counts
from ..core.states import get_user_status
from ..auth.auth_funcs import load_user
from ..core.logs import logger
import aiogram
import datetime
import asyncio
import random
import apscheduler.triggers.cron
from ...storage import notification_scheduler
from aiogram import exceptions

notification_prefix = """❗️Уведомление❗️\n\n"""

AUTH_ERROR_CODES = (401, 403, 422)
KICK_THRESHOLD = 3


async def _handle_auth_error(bot: aiogram.Bot, user_id: int) -> bool:
    cnt = failed_403_counts.get(user_id, 0) + 1
    failed_403_counts[user_id] = cnt
    if cnt >= KICK_THRESHOLD:
        logger.warning(f"Кикаю пользователя {user_id} после {cnt}× 401/403/422 подряд")
        try:
            await db_obj.delete_user_by_telegram_id(user_id)
        except Exception as e:
            logger.error(f"Ошибка удаления юзера {user_id}: {e}")
        try:
            await settings_db_obj.delete_settings_by_telegram_id(user_id)
        except Exception as e:
            logger.error(f"Ошибка удаления настроек {user_id}: {e}")
        failed_403_counts.pop(user_id, None)
        try:
            await bot.send_message(
                chat_id=user_id,
                text="❗️ Сессия истекла (3 ошибки авторизации подряд). Авторизуйся заново: /start",
            )
        except Exception:
            pass
        return True
    logger.info(f"Пользователь {user_id}: {cnt}/{KICK_THRESHOLD} ошибок авторизации")
    return False


@load_user
async def check_homework(bot: aiogram.Bot, user_id: int):
    resp = await settings_db_obj.get_all_settings_by_telegram_id(user_id)

    if resp == None:
        await settings_db_obj.init_user_settings(user_id)
        resp = await settings_db_obj.get_all_settings_by_telegram_id(user_id)

    if resp is None:
        failed_403_counts.pop(user_id, None)
        return

    if resp.get("get_almost_expired_hw_notifications") == False:
        return

    timezone = resp.get('timezone')
    user_states = get_user_status(user_id)
    homework_count = await (get_user_status(user_id).API.get_homework_count())

    if homework_count in AUTH_ERROR_CODES:
        await _handle_auth_error(bot, user_id)
        return

    if homework_count == 500 or homework_count == {} or homework_count is False:
        return

    failed_403_counts.pop(user_id, None)

    pages_count = homework_count["type_3"] // 7 + 2
    for page in range(1, pages_count):
        actual_homeworks = await user_states.API.get_homework(3, page)

        if actual_homeworks in AUTH_ERROR_CODES:
            await _handle_auth_error(bot, user_id)
            return
        if actual_homeworks == 500 or actual_homeworks == False:
            continue
        await send_homework_notification(bot, actual_homeworks, user_id, timezone)
        await asyncio.sleep(0.05)



async def send_homework_notification(bot: aiogram.Bot, actual_homeworks: list, user_id, timezone: str):
    for homework in actual_homeworks:
        deadline = homework.get("overdue_time")
        try:
            time_to_expire = datetime.datetime.fromisoformat(deadline) - datetime.datetime.today()
        except Exception:
            continue
        if timezone and len(timezone) == 2:
            operation, number = timezone[0], timezone[1]
            try:
                delta = datetime.timedelta(hours=int(number))
            except ValueError:
                delta = datetime.timedelta(0)
            if operation == '+':
                time_to_expire -= delta
            else:
                time_to_expire += delta

        hours = time_to_expire.seconds / 60 / 60
        days = time_to_expire.days

        if days in [0, 1]:
            try:
                if 16.5 < hours < 17.5 and days == 0:
                    await bot.send_message(
                        chat_id=user_id,
                        text=notification_prefix + f"До просрочки дз по <i>{homework.get('name_spec')}</i> осталось около <b>17 часов</b>",
                        parse_mode="HTML")
                elif 11.5 < hours < 12.5 and days == 1:
                    await bot.send_message(
                        chat_id=user_id,
                        text=notification_prefix + f"До просрочки дз по <i>{homework.get('name_spec')}</i> осталось <b>полтора дня</b>",
                        parse_mode="HTML")
                elif 5.5 < hours < 6.5 and days == 0:
                        await bot.send_message(
                            chat_id=user_id,
                            text=notification_prefix + f"До просрочки дз по <i>{homework.get('name_spec')}</i> осталось около <b>6 часов</b>, торопись!",
                            parse_mode="HTML")
                        
    
            except exceptions.TelegramForbiddenError:
                logger.warning(f"Пользователь {user_id} ограничил доступ к боту.")
                await settings_db_obj.delete_settings_by_telegram_id(user_id)

            except exceptions.TelegramBadRequest as e:
                logger.warning(f"Ошибка запроса для {user_id}: {e}")

            except Exception as e:
                logger.error(f"Непредвиденная ошибка при рассылке пользователю {user_id}: {e}", exc_info=True)                    



async def check_homework_start(bot: aiogram.Bot):
    logger.info("Начинаю рассылку уведомлении о скорой просрочке дз")
    jitter = random.randint(0, 90)
    if jitter:
        await asyncio.sleep(jitter)
    users_ids = await db_obj.get_all_telegram_ids()
    if not users_ids:
        logger.info("Рассылка завершена — нет пользователей")
        return
    batch_size = 20
    for i in range(0, len(users_ids), batch_size):
        batch = users_ids[i:i + batch_size]
        await asyncio.gather(*(check_homework(bot, uid[0]) for uid in batch))
        if i + batch_size < len(users_ids):
            await asyncio.sleep(2)
    logger.info("Рассылка уведомлении о скорой просрочке дз завершена")
        


async def init_almost_expired_homework_notification(bot):
    
    notification_scheduler.add_job(
        check_homework_start,
        trigger=apscheduler.triggers.cron.CronTrigger(hour='*', minute=0),
        id='almost_exp_notification',
        args=[bot]
    )
