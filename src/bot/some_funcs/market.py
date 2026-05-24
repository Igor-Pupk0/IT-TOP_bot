import aiogram
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..auth.authorization_callbacks import check_auth
from ..core.logs import logger
from ..core.states import get_user_status
from ..core.pages import Pages, messages_pages
from ..core.keyboards import make_return_button
from ..core.journal_500 import get_500_message
from ..core.keyboards import make_return_button, make_turn_pages_buttons

market_router = aiogram.Router()

@market_router.callback_query(F.data == "show_market")
@check_auth
async def handle_get_market(call: aiogram.types.CallbackQuery):
    logger.info(f"Пользователь ({call.from_user.username}:{call.from_user.id}) смотрит маркет")
    
    market_products: list = await (get_user_status(call.from_user.id).API.get_market_products())
    if market_products == 500:
        await call.message.answer(text=get_500_message(call.message))
        return
    
    keyboard = InlineKeyboardBuilder()
    turn_left_button, turn_right_button = make_turn_pages_buttons()
    keyboard.add(turn_left_button, turn_right_button, make_return_button())
    keyboard.adjust(2, 1)
    pages_obj = Pages()

    products_list = market_products["products_list"]
    total_count = len(products_list)

    for num, product in enumerate(products_list):
        product_name = product["title"]
        product_quantity = product["quantity"]
        product_desc = product["description"]
        product_price = {"top_coins": product["prices"][0]["points_sum"], "top_gems": product["prices"][1]["points_sum"]}

        pages_obj.add_page(f"""\
Вещь №{num+1} из {total_count}

Название: <b>{product_name}</b>
Кол-во: <i>{product_quantity}</i>
Цена: <b>{product_price['top_coins']}</b> топкойнов 💸 и <b>{product_price['top_gems']}</b> топгемов 💎

<i>{product_desc}</i>

""")

    await call.answer()
    sended_message: aiogram.types.Message = await call.message.answer(
        text=pages_obj.get_page(), 
        parse_mode="HTML", 
        reply_markup=keyboard.as_markup(), 
        disable_web_page_preview=True)
    
    messages_pages[call.from_user.id].update({sended_message.message_id: pages_obj})