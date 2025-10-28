import telebot
from .core.storage import TOKEN

from .modules.menu_returns import setup_returns_module
from .modules.profile import setup_profile_module
from .modules.schedule import setup_schedule_module
from .modules.homework.get_homework import setup_get_homework_module
from .modules.start import setup_start_module
from .modules.pages_callbacks import setup_pages_cb_module
from .modules.authorization import setup_auth_module
from .modules.admin_funcs import setup_admin_module
from .modules.homework.send_homework import setup_send_homework_module
from .modules.homework.delete_homework import setup_delete_homework_module
from .modules.marks import setup_marks_module
from .modules.some_funcs.menu import setup_some_module
from .modules.some_funcs.rate_all_lessons import setup_rate_lessons_module
from .modules.some_funcs.feedbacks import setup_get_feedbacks_module
from .notifications.notifications_main import init_notifications


bot = telebot.TeleBot(TOKEN)

setup_start_module(bot)
setup_auth_module(bot)
setup_returns_module(bot)
setup_profile_module(bot)
setup_get_homework_module(bot)
setup_schedule_module(bot)
setup_pages_cb_module(bot)
setup_admin_module(bot)
setup_send_homework_module(bot)
setup_delete_homework_module(bot)
setup_marks_module(bot)
setup_some_module(bot)
setup_rate_lessons_module(bot)
setup_get_feedbacks_module(bot)

init_notifications(bot)
