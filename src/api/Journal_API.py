###
### MAIN FILE FOR INTERACTING WITH JOURNAL API
###

import requests
import json

API_HOST = "msapi.top-academy.ru"
CONFIG_FILE = "src/api/creds.json"

class API:
    def __init__(self, USER: str, PASS: str):
        ### Проверка на наличие JWT токена в конфиг файле
        with open(CONFIG_FILE, "r") as file:
            json_config = json.loads(file.read())

        if json_config["have_JWT"]:
            JWT_TOKEN = json_config["JWT_token"]
        else:
            JWT_TOKEN = None

        self.USER = USER
        self.PASS = PASS

        headers_start = {
        "Host": API_HOST,
        "Referer": "https://journal.top-academy.ru/"
        }
    
        self.headers_with_JWT = headers_start
        
        if JWT_TOKEN == None:
            JWT_TOKEN = self.get_JWT_token(self.USER, self.PASS, headers_start)
            json_config["JWT_token"] = JWT_TOKEN
            with open(CONFIG_FILE, "w") as file:
                json_to_write = json.dumps()
                file.write(json_to_write)

        self.headers_with_JWT["Authorization"] = "Bearer " + JWT_TOKEN

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
            exit()


    def update_JWT_headers(self):
        JWT_TOKEN = self.get_JWT_token(self.USER, self.PASS, self.headers_with_JWT)
        self.headers_with_JWT["Authorization"] = "Bearer " + JWT_TOKEN

        with open(CONFIG_FILE, "r") as file:
            json_config = json.loads(file.read())

        json_config["JWT_token"] = JWT_TOKEN

        with open(CONFIG_FILE, "w") as file:
            json_to_write = json.dumps(json_config)
            file.write(json_to_write)


    def get_schedule_by_date(self, iso_date: str) -> dict:
        url = "https://" + API_HOST + "/api/v2/schedule/operations/get-by-date?date_filter=" + iso_date
        
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