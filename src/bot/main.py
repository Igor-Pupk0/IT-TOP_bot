import telebot
from src.bot.core.storage import TOKEN

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