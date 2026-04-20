###
### Функция генерации страниц с оценками из JSON ответа
### Возвращает ссылку на страницу c размещенными оценками
###

import requests
import jinja2

STORAGE_SERVICE_URL = "http://127.0.0.1:8000/upload"
AUTH_TOKEN = "broodskoye"

def upload_html_page(file_content: str):
    files = {"file": ("mne.html", file_content.encode("utf-8"), "text/html")}
    
    headers = {
        "User-Agent": "IT-TOP_bot/1.0",
        "X-Auth-Token": AUTH_TOKEN
    }
    
    try:
        response = requests.post(
            STORAGE_SERVICE_URL, 
            files=files, 
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.text.strip('"')
        elif response.status_code == 429:
            return "Error: Too many requests (Rate limit)"
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"

def generate_marks_page(marks_list: list) -> str:

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("src/templates"))
    marks_template = env.get_template("marks.html")

    marks_html_content = marks_template.render(
        marks_list=marks_list
    )

    return upload_html_page(marks_html_content)


