###
### MAIN FILE FOR INTERACTING WITH JOURNAL API
### Тут находиться класс для взаимодействия с API
###

from src.db.Journal_database import Creds_db
from src.bot.core.logs import logger
from src.bot.core.states import delete_user_status
import requests
import json

API_HOST = "msapi.top-academy.ru"

class API:

    def status_code_checker(self, response: requests.Response):
            if response.status_code != 200:
                if response.status_code == 401:
                    raise Exception("Unauthorized")
                elif response.status_code == 500:
                    raise Exception("Server error")
                elif response.status_code == 201:
                    raise Exception("ALL OK!")
                elif response.status_code == 204:
                    raise Exception("No content")

                raise Exception("Non 200 HTTP code on auth:", response.status_code, response.text)

    def exception_handler(self, ex, response):
            print("Error in some func:", ex)
            if str(ex) == "Unauthorized" or str(ex) == "Invalid creds":
                res = self.update_JWT_headers()
                if res == "Account has wrong creds":
                    db_obj = Creds_db()
                    telegram_id = db_obj.get_telegram_id_by_user(self.USER)
                    if telegram_id == None:
                        return "Account has wrong creds"
                    logout(telegram_id[0])
            elif str(ex) == "Server error":
                return response.status_code
            elif str(ex) == "ALL OK!":
                return response.status_code
            elif str(ex) == "No content":
                return response.status_code

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
                elif response.status_code == 500:
                    raise Exception("Server error")
                
                raise Exception("Non 200 HTTP code on auth:", response.status_code, response.text)
            
            json_responce_obj = json.loads(response.text)
            return json_responce_obj["access_token"]
        except Exception as e:
            print(e)
            if str(e) == "Invalid creds":
                return False
            elif str(e) == "Server error":
                return response.status_code

    def update_JWT_headers(self):
        self.JWT_TOKEN = self.get_JWT_token(self.USER, self.PASS, self.headers_with_JWT)
        if type(self.JWT_TOKEN) != str:
            return "Account has wrong creds"
        
        self.headers_with_JWT["Authorization"] = "Bearer " + self.JWT_TOKEN
        db_obj = Creds_db()
        db_obj.update_user_JWT_token(self.USER, self.JWT_TOKEN)


    def get_schedule_by_date(self, iso_date: str) -> dict:
        url = f"https://{API_HOST}/api/v2/schedule/operations/get-by-date?date_filter={iso_date}"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)


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
        url = f"https://{API_HOST}/api/v2/homework/operations/list?page={page}&status={homework_status}&type=0"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)
                
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        return json_responce_obj

    def get_homework_count(self) -> dict:
        url = f"https://{API_HOST}/api/v2/count/homework?type=0"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)
                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)
                

        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        homework_count_dict = {}

        for i in json_responce_obj:
            if type(i) != dict:
                continue
            homework_count_dict[ f'type_{i["counter_type"]}' ] = i["counter"]

        return homework_count_dict
    
    def get_user_info(self) -> dict:
        url = f"https://{API_HOST}/api/v2/settings/user-info"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    def send_homework(self, homework_id: int, text_answer: str, homework_file_name:str = None, time_spent: str = "00:00", homework_file_bytes: bytes = None) -> dict:
        url = f"https://{API_HOST}/api/v2/homework/operations/create"

        time = time_spent.split(":")
        time_hrs, time_min = time


        post_data = {"id": homework_id,
                "answerText": text_answer,
                "spentTimeHour": time_hrs,
                "spentTimeMin": time_min}
        

        if homework_file_bytes == None:
            post_file = {}
        else:
            post_file = {"file": (homework_file_name, homework_file_bytes, "*/*")}
        
        for _ in range(1, 4):
            try:
                response = requests.post(url, headers=self.headers_with_JWT, data=post_data, files=post_file)

                self.status_code_checker(response)
                break
            except Exception as e:
                code = self.exception_handler(e, response)
                if code != None:
                    return code
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    def delete_homework(self, checkout_homework_id):
        url = f"https://{API_HOST}/api/v2/homework/operations/delete"

        post_data = {"id": checkout_homework_id}
        
        for _ in range(1, 4):
            try:
                response = requests.post(url, headers=self.headers_with_JWT, data=post_data)

                self.status_code_checker(response)
                break
            except Exception as e:
                code = self.exception_handler(e, response)
                if code != None:
                    return code
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    

    def get_marks(self) -> dict:
        url = f"https://{API_HOST}/api/v2/progress/operations/student-visits"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj


    def get_lessons_for_feedback(self) -> dict:
        url = f"https://{API_HOST}/api/v2/feedback/students/evaluate-lesson-list"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                self.exception_handler(e, response)
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    def send_lesson_feedback(self, lesson_key: str):
        url = f"https://{API_HOST}/api/v2/feedback/students/evaluate-lesson"

        post_data = {"mark_lesson":5,
                     "mark_teach":5,
                     "key": lesson_key,
                     "tags_lesson":[],
                     "tags_teach":[],
                     "comment_lesson":"",
                     "comment_teach":""}
        
        
        for _ in range(1, 4):
            try:
                response = requests.post(url, headers=self.headers_with_JWT, data=post_data)

                self.status_code_checker(response)
                break
            except Exception as e:
                code = self.exception_handler(e, response)
                if code != None:
                    return code
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    def get_student_feedbacks(self):
        url = f"https://{API_HOST}/api/v2/reviews/index/list"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                code = self.exception_handler(e, response)
                if code != None:
                    return code
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    def get_market_products(self):
        url = f"https://{API_HOST}/api/v2/market/customer/product/list?page=1&type=0"
        
        for _ in range(1, 4):
            try:
                response = requests.get(url, headers=self.headers_with_JWT)

                self.status_code_checker(response)
                break
            except Exception as e:
                code = self.exception_handler(e, response)
                if code != None:
                    return code
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    def get_leader_tables_stats(self):
        url_group = f"https://{API_HOST}/api/v2/dashboard/progress/leader-group-points"
        url_stream = f"https://{API_HOST}/api/v2/dashboard/progress/leader-stream-points"
        
        for _ in range(1, 4):
            try:
                response_group = requests.get(url_group, headers=self.headers_with_JWT)

                self.status_code_checker(response_group)
                break
            except Exception as e:
                code = self.exception_handler(e, response_group)
                if code != None:
                    return code
                
        for _ in range(1, 4):
            try:
                response_stream = requests.get(url_stream, headers=self.headers_with_JWT)

                self.status_code_checker(response_stream)
                break
            except Exception as e:
                code = self.exception_handler(e, response_stream)
                if code != None:
                    return code
                
        json_responce_obj_stream = json.loads(response_stream.text)
        json_responce_obj_group = json.loads(response_group.text)
        
        return {"stream": json_responce_obj_stream, "group": json_responce_obj_group}

    def get_student_visits_procent(self):
        responce = self.get_marks()

        lessons_dont_was = 0

        for i in responce:
            if i.get("status_was") != 1:
                lessons_dont_was += 1
        
        return round(100 - (lessons_dont_was / len(responce)) * 100, 1)
                

def logout(telegram_id):
    logger.info(f"Пользователь (???:{telegram_id}) был кикнут из аккаунта")
    db_obj = Creds_db()
    db_obj.delete_user_by_telegram_id(telegram_id)
    delete_user_status(telegram_id)