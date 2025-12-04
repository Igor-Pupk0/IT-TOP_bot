###
### Просто для удобства, чтобы хранить не словарь, а класс
###

class User:
    def __init__(self, user_obj = None):

        self.API = user_obj

        # У auth_status есть 4 состояния:
        # 1) "No_auth" - без авторизации
        # 2) "Auth_on_username" - проходит авторизация, бот ждет логина
        # 3) "Auth_on_password" - проходит авторизация, бот ждет пароль
        # 4) "Auth" - авторизован
        self.auth_status = "No_auth"

        self.broadcast_typing_status = False

        ### Параметры для сдачи ДЗ
        self.writing_time = False
        self.sending_text_answer = False
        self.sending_homework_file = False
    