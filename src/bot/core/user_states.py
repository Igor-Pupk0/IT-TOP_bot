###
### Просто для удобства, чтобы хранить не словарь, а класс
###
class User:
    def __init__(self):
        # У auth_status есть 4 состояния:
        # 1) "No_auth" - без авторизации
        # 2) "Auth_on_username" - проходит авторизация, бот ждет логина
        # 3) "Auth_on_password" - проходит авторизация, бот ждет пароль
        # 4) "Auth" - авторизован
        self.auth_status = "No_auth"

        # main
        # main/profile
        # main/homeworks
        # main/homeworks/some_hw
        # main/schedule
        self.active_menu = "main"

    