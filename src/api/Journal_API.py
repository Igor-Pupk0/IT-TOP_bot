###
### MAIN FILE FOR INTERACTING WITH JOURNAL API
### Тут находиться класс для взаимодействия с API
###

from src.db.Journal_database import Creds_db
import requests
import json

API_HOST = "msapi.top-academy.ru"

class API:
    def __init__(self, USER: str, PASS: str, JWT_token = False):
        self.succesful_auth = False
        self.USER = USER
        self.PASS = PASS

        headers_start = {
        "Host": API_HOST,
        "Referer": "https://journal.top-academy.ru/"
        }
    
        self.headers_with_JWT = headers_start

        if JWT_token == False or JWT_token == 'None':
            self.JWT_TOKEN = self.get_JWT_token(self.USER, self.PASS, headers_start)
        else:
            self.JWT_TOKEN = JWT_token

        if self.JWT_TOKEN == False:
            return

        self.headers_with_JWT["Authorization"] = "Bearer " + self.JWT_TOKEN
        self.succesful_auth = True

    def get_JWT_token(self, username: str, password: str, headers_start: dict) -> str:
        url = "https://" + API_HOST + "/api/v2/auth/login"
        json_data = {
            "application_key":"6a56a5df2667e65aab73ce76d1dd737f7d1faef9c52e8b8c55ac75f565d8e8a6",
            "id_city":None,
            "password":password,
            "username":username
        }
        
        try:
            response = requests.post(url, headers=headers_start, json=json_data)

            if response.status_code != 200:
                if response.status_code == 422:
                    raise Exception("Invalid creds")
                raise Exception("Non 200 HTTP code on auth:", response.status_code, response.text)
            
            json_responce_obj = json.loads(response.text)
            return json_responce_obj["access_token"]
        except Exception as e:
            print(e)
            if str(e) == "Invalid creds":
                return False
            exit()


    def update_JWT_headers(self):
        self.JWT_TOKEN = self.get_JWT_token(self.USER, self.PASS, self.headers_with_JWT)
        self.headers_with_JWT["Authorization"] = "Bearer " + self.JWT_TOKEN

        db_obj = Creds_db()
        db_obj.update_user_JWT_token(self.USER, self.JWT_TOKEN)


    def get_schedule_by_date(self, iso_date: str) -> dict:
        url = f"https://{API_HOST}/api/v2/schedule/operations/get-by-date?date_filter={iso_date}"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                if response.status_code != 200:
                    if response.status_code == 401:
                        raise Exception("Unauthorized")
                    raise Exception("Non 200 HTTP code on auth:", response.status_code, response.text)
                break
            
            except Exception as e:
                print("Error in 'get_schedule_by_date' func:", e)
                if str(e) == "Unauthorized":
                    self.update_JWT_headers()
                    continue
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        return json_responce_obj
    
    # Получение ДЗ по типу:
    #  - 0 - ? (возможно просроченное)
    #  - 1 - Сданное и оцененное ДЗ
    #  - 2 - Сданное ДЗ, ожидающее проверки
    #  - 3 - Актуальное
    def get_homework(self, homework_status: int, page: int) -> dict:
        url = f"https://{API_HOST}/api/v2/homework/operations/list?page={page}&status={homework_status}&type=0&group_id=84"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                if response.status_code != 200:
                    if response.status_code == 401:
                        raise Exception("Unauthorized")
                    raise Exception("Non 200 HTTP code on auth:", response.status_code, response.text)
                break

            except Exception as e:
                print("Error in 'get_homework' func:", e)
                if str(e) == "Unauthorized":
                    self.update_JWT_headers()
                    continue
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        return json_responce_obj