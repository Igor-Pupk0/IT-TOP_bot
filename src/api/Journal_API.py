###
### MAIN FILE FOR INTERACTING WITH JOURNAL API
### Тут находится класс для взаимодействия с API
###

from ..storage import db_obj
from src.bot.core.logs import logger
from ..bot.auth.delete import delete_user
import httpx
import json

API_HOST = "msapi.top-academy.ru"

class API:
    def __status_code_checker(self, response: httpx.Response):
            if response.status_code - 200 >= 100:
                logger.info(f"Non 200 HTTP code on auth: {response.status_code}, {response.text}")
                raise Exception(response.status_code)


    async def __exception_handler(self, ex: Exception, response: httpx.Response):
            if response.status_code in [403, 422, 401]:
                if response.status_code == 422:
                    telegram_id = await db_obj.get_telegram_id_by_user(self.USER)
                    if telegram_id == None:
                        return 422
                if response.status_code == 401:
                    if await self.update_JWT_headers() == 422:
                        telegram_id = await db_obj.get_telegram_id_by_user(self.USER)
                        await delete_user(telegram_id)
                        return

            else:
                logger.error(f"Error in some func: {ex}")
                return response.status_code

    def __init__(self, USER: str, PASS: str, JWT_token = False):
        self.succesful_auth = False
        self.USER = USER
        self.PASS = PASS
    
        self.headers = {
        "Host": API_HOST,
        "Referer": "https://journal.top-academy.ru/"
        }

        self.headers_with_JWT = {
        "Host": API_HOST,
        "Referer": "https://journal.top-academy.ru/"
        }

        self.JWT_TOKEN = JWT_token

    async def init_user(self):
        if await self.update_JWT_headers() == 422:
            return False
        self.succesful_auth = True


    async def get_JWT_token(self) -> str:
        url = "https://" + API_HOST + "/api/v2/auth/login"
        json_data = {
            "application_key":"6a56a5df2667e65aab73ce76d1dd737f7d1faef9c52e8b8c55ac75f565d8e8a6",
            "id_city":None,
            "password":self.PASS,
            "username":self.USER
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=json_data)

            self.__status_code_checker(response)
            
            json_responce_obj = json.loads(response.text)
            return json_responce_obj["access_token"]
        except Exception as e:
            await self.__exception_handler(e, response)

    async def update_JWT_headers(self):
        self.JWT_TOKEN = await self.get_JWT_token()
        if type(self.JWT_TOKEN) != str:
            return 422
        
        self.headers_with_JWT["Authorization"] = "Bearer " + self.JWT_TOKEN
        await db_obj.update_user_JWT_token(self.USER, self.JWT_TOKEN)

    async def __send_get_request(self, url: str) -> httpx.Response:        
        for _ in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers_with_JWT)
                self.__status_code_checker(response)
                break
            except Exception as e:
                code = await self.__exception_handler(e, response)
                if code != None:
                    return code
        return response

    
    async def __send_post_request(self, url: str, data: dict = {}, file: dict = {}) -> httpx.Response:        
        for _ in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=self.headers_with_JWT, data=data, files=file)

                self.__status_code_checker(response)
                break
            except Exception as e:
                code = await self.__exception_handler(e, response)

        return response

    async def get_schedule_by_date(self, iso_date: str) -> dict:
        url = f"https://{API_HOST}/api/v2/schedule/operations/get-by-date?date_filter={iso_date}"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj 
    
    # Получение ДЗ по типу:
    #  - 0 - Просроченное
    #  - 1 - Сданное и оцененное ДЗ
    #  - 2 - Сданное ДЗ, ожидающее проверки преподом
    #  - 3 - Актуальное
    # Параметр type отвечает за показ лаб, тоесть:
    #  - 0 - обычное дз
    #  - 1 - лабораторные работы
    async def get_homework(self, homework_status: int, page: int) -> dict:
        url = f"https://{API_HOST}/api/v2/homework/operations/list?page={page}&status={homework_status}&type=0"
        
        response = await self.__send_get_request(url)
                
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        return json_responce_obj

    async def get_homework_count(self) -> dict:
        url = f"https://{API_HOST}/api/v2/count/homework?type=0"
        
        response = await self.__send_get_request(url)

        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
        
        homework_count_dict = {}

        for i in json_responce_obj:
            if type(i) != dict:
                continue
            homework_count_dict[ f'type_{i["counter_type"]}' ] = i["counter"]

        return homework_count_dict
    
    async def get_user_info(self) -> dict:
        url = f"https://{API_HOST}/api/v2/settings/user-info"
        
        response = await self.__send_get_request(url)
                
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    async def send_homework(self, homework_id: int, text_answer: str, homework_file_name:str = None, time_spent: str = "00:00", homework_file_bytes: bytes = None) -> dict:
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
        
        response = await self.__send_post_request(url, data=post_data, file=post_file)
        
        if response.status_code == 201:
            return True
        else:
            return False
    
    async def delete_homework(self, checkout_homework_id) -> bool:
        url = f"https://{API_HOST}/api/v2/homework/operations/delete"

        post_data = {"id": checkout_homework_id}
        
        response = await self.__send_post_request(url, data=post_data)
        
        if response.status_code == 204:
            return True
        
        return False
    

    async def get_marks(self) -> dict:
        url = f"https://{API_HOST}/api/v2/progress/operations/student-visits"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    async def get_lessons_for_feedback(self) -> dict:
        url = f"https://{API_HOST}/api/v2/feedback/students/evaluate-lesson-list"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return []
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    async def send_lesson_feedback(self, lesson_key: str):
        url = f"https://{API_HOST}/api/v2/feedback/students/evaluate-lesson"

        post_data = {"mark_lesson":5,       # Оценка урока
                     "mark_teach":5,        # Оценка препода
                     "key": lesson_key,     # ID урока
                     "tags_lesson":[],      # Теги урока, тип "все понятно" или "ниче не понятно"
                     "tags_teach":[],       # Теги препода
                     "comment_lesson":"",   # Комментарий по уроку
                     "comment_teach":""}    # Комментарий по преподу
        
        
        response = await self.__send_post_request(url, data=post_data)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    async def get_student_feedbacks(self):
        url = f"https://{API_HOST}/api/v2/reviews/index/list"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj
    
    async def get_market_products(self):
        url = f"https://{API_HOST}/api/v2/market/customer/product/list?page=1&type=0"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    async def get_leader_tables_stats(self):
        url_group = f"https://{API_HOST}/api/v2/dashboard/progress/leader-group-points"
        url_stream = f"https://{API_HOST}/api/v2/dashboard/progress/leader-stream-points"
        
        response_group = await self.__send_get_request(url_group)
        response_stream = await self.__send_get_request(url_stream)

        json_responce_obj_stream = json.loads(response_stream.text)
        json_responce_obj_group = json.loads(response_group.text)
        
        return {"stream": json_responce_obj_stream, "group": json_responce_obj_group}

    async def get_student_visits_procent(self): # Считает АБСОЛЮТНО всю посещаемость за все время, не за месяц
        response = await self.get_marks()

        skipped_lessons = 0
        all_lessons = len(response)

        for lesson in response:
            if lesson.get("status_was") != 1: # Тоесть типа не было
                skipped_lessons += 1
        
        return round(100 - (skipped_lessons / all_lessons) * 100, 1)

    async def get_leaderboard_group(self):
        url = f"https://{API_HOST}/api/v2/dashboard/progress/leader-group"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    async def get_leaderboard_stream(self):
        url = f"https://{API_HOST}/api/v2/dashboard/progress/leader-stream"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj 

    async def get_activity(self):
        url = f"https://{API_HOST}/api/v2/dashboard/progress/activity"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj

    async def get_future_exams(self):
        url = f"https://{API_HOST}/api/v2/dashboard/info/future-exams"
        
        response = await self.__send_get_request(url)
        
        json_responce_obj = json.loads(response.text)
        if json_responce_obj == None or json_responce_obj == []:
            return False
                
        json_responce_obj = json.loads(response.text)
        
        return json_responce_obj 
