import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.states import get_user_status
from ..core.keyboards import make_return_button, make_turn_pages_buttons
from ..core.pages import Pages, messages_pages
from ..core.journal_500 import get_500_message

activity_router = aiogram.Router()

@activity_router.callback_query(F.data == "show_activity")
@check_auth
async def handle_get_activity(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит активность")
    
    user = get_user_status(call.from_user.id)
    user_activites = await user.API.get_activity()
    if user_activites == 500:
        await call.message.answer(text=get_500_message(call))
        return

    page_obj = Pages()
    message = ''
    for num, activity in enumerate(user_activites):
        if num == 0:
            message = f'Страница: №{page_obj.page_count + 1} из {len(user_activites) // 10}\n'

        activity_date = activity["date"]
        points_rewarded = activity["current_point"]
        reward_points_icon = "??"
        match activity["point_types_name"]:
            case "COIN":
                reward_points_icon = "💎"
            case "DIAMOND":
                reward_points_icon = "🪙"

        

        if activity["achievements_type"] == 1:
            activity_desc = match_user_activity_achievements_name(activity["achievements_name"])
        else:
            activity_desc = "Ачивка"

        if activity["action"] == 1:
            activity_act = "+"
        else:
            activity_act = "-"

        message += f"    {activity_act}{points_rewarded} {reward_points_icon}: {activity_desc} ({activity_date}) \n"
        
        if num % 10 == 0 and num != 0:
            page_obj.add_page(message)
            message = f'Страница: №{page_obj.page_count + 1} из {len(user_activites) // 10}\n'

    keyboard = InlineKeyboardBuilder()
    turn_left_button, turn_right_button = make_turn_pages_buttons()
    keyboard.add(turn_left_button, turn_right_button, make_return_button())
    keyboard.adjust(2, 1)

    await call.answer()
    sended_message = await call.message.answer(
        text=page_obj.get_page(), 
        parse_mode="HTML", 
        reply_markup=keyboard.as_markup(), 
        disable_web_page_preview=True)
    
    messages_pages[call.from_user.id].update({sended_message.message_id: page_obj})
    

def match_user_activity_achievements_name(ach_name: str):
    match ach_name:
        case "ASSESMENT":
            return "Оценка"
        case "PAIR_VISIT":
            return "Посещение пары"
        case "HOMETASK_INTIME":
            return "Выполнение дз вовремя"
        case "REDO_HOMETASK":
            return "Пересдача дз"
        case "WORK_IN_CLASS":
            return "От препода"
        case "EVALUATION_LESSON_MARK":
            return "Оценка занятия"
        case "UNCONFIRMED_ATTRIBUTE":
            return "Не заполнены данные в лк"
        
    
    return "??"