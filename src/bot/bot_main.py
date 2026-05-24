import aiogram
from ..storage import dp

### Импорт НЕОБХОДИМОГО функционала, без него бот просто не будет нормально работать
from .core.returns import return_router
from .core.start import start_router
from .core.pages_callbacks import page_callback_router
from .auth.authorization_callbacks import auth_router

### Тут уже основной функционал
from .main_functions.profile.profile import profile_router
from .main_functions.schedule import schedule_router
from .main_functions.homework.get_homework import homework_router
from .main_functions.marks.marks import marks_router

from .admin.admin import admin_router
from .some_funcs.menu import some_menu_router

core_routers = [
    auth_router,
    start_router,
    return_router,
    page_callback_router
]

main_routers = [
    schedule_router,
    profile_router,
    homework_router,
    marks_router
]

dp.include_routers(
    *core_routers,
    *main_routers,
    some_menu_router,
    admin_router
)
# setup_returns_module(bot)
# setup_profile_module(bot)
# setup_get_homework_module(bot)
# setup_schedule_module(bot)
# setup_pages_cb_module(bot)
# setup_admin_module(bot)
# setup_send_homework_module(bot)
# setup_delete_homework_module(bot)
# setup_marks_module(bot)
# setup_some_module(bot)
# setup_rate_lessons_module(bot)
# setup_get_feedbacks_module(bot)
# setup_market_module(bot)
# setup_stats_module(bot)
# setup_settings_module(bot)
# setup_leaderboards_module(bot)
# setup_activity_module(bot)
# setup_exams_module(bot)

# init_notifications(bot)
