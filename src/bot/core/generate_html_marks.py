###
### Функция генерации страниц с оценками из JSON ответа
### Возвращает ссылку на страницу c размещенными оценками
###

import requests
import jinja2

# STORAGE_SERVICE_URL_2 = "https://envs.sh"
STORAGE_SERVICE_URL_2 = "https://0x0.st"

user_agent_headers = {"User-Agent": "IT-TOP_bot/1.0"}

def upload_html_page(file_content: str):

    file_post_data = {"file": ("mne.html", file_content.encode("utf-8"), "text/html")}
    post_data = {"secret": "zov",
                 "expires": 3}
    
    response = requests.post(STORAGE_SERVICE_URL_2, files=file_post_data, data=post_data, headers=user_agent_headers)
    print(response.text)
    return response.text[:-1]

def generate_marks_page(marks_list: list) -> str:

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("src/templates"))
    marks_template = env.get_template("marks.html")

    marks_html_content = marks_template.render(
        marks_list=marks_list
    )

    # lesson_data = marks_list.get("date_visit")
    # lesson_number = marks_list.get("lesson_number")
    # student_was_on_lesson = marks_list.get("status_was")
    # teacher_name = marks_list.get("teacher_name")
    # lesson_name = marks_list.get("spec_name")
    # lesson_theme = marks_list.get("lesson_theme")

    # # Оценки
    # control_work_mark = marks_list.get("control_work_mark")
    # home_work_mark = marks_list.get("home_work_mark")
    # lab_work_mark = marks_list.get("lab_work_mark")
    # class_work_mark = marks_list.get("class_work_mark")
    # practical_work_mark = marks_list.get("practical_work_mark")

    return upload_html_page(marks_html_content)


