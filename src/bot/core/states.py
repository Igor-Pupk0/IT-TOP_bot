from src.bot.core.user_states import User
from .storage import users_states

def get_user_status(telegram_id):
    user_states = users_states.get(telegram_id)
    if user_states is not None:
        return user_states
    user_states = User()
    users_states[telegram_id] = user_states
    return user_states