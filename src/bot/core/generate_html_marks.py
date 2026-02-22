###
### Функция генерации страниц с оценками из JSON ответа
### Возвращает ссылку на страницу c размещенными оценками
###

import requests
import jinja2

# STORAGE_SERVICE_URL_2 = "https://envs.sh"
STORAGE_SERVICE_URL_2 = "https://0.vern.cc/"

user_agent_headers = {"User-Agent": "IT-TOP_bot/1.0"}

def upload_html_page(file_content: str):

    file_post_data = {"file": ("mne.html", file_content.encode("utf-8"), "text/html")}
    post_data = {"secret": "zov",
                 "expires": 3}
    
    response = requests.post(STORAGE_SERVICE_URL_2, files=file_post_data, data=post_data, headers=user_agent_headers)
    return response.text[:-1]

def generate_marks_page(marks_list: list) -> str:

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("src/templates"))
    marks_template = env.get_template("marks.html")

    marks_html_content = marks_template.render(
        marks_list=marks_list
    )

    return upload_html_page(marks_html_content)


