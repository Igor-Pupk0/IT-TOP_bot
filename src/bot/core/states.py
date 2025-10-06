from .user import User
from .storage import users_states, user_auths

def get_user_status(telegram_id):
    user_states: User = users_states.get(telegram_id)
    if user_states is not None:
        print(1)
        if user_states.API == None and user_auths.get(telegram_id) != None:
            print(2)
            user_list = user_auths.get(telegram_id)
            print(user_states.auth_status)
            user_obj = user_list.get('User_obj')
            if user_obj != None:
                user_states = User(user_obj)
        return user_states
    user_list = user_auths.get(telegram_id)
    if user_list == None:
        user_states = User()
    else:
        user_states = User(user_list['User_obj'])
    users_states[telegram_id] = user_states
    return user_states

