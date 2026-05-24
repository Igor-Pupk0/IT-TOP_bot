###
### Функция генерации страниц с оценками из JSON ответа
### Возвращает ссылку на страницу c размещенными оценками
###

import httpx
import jinja2
from ...core.logs import logger

STORAGE_SERVICE_URL = "http://127.0.0.1:8000/upload"
AUTH_TOKEN = "broodskoye"

async def upload_html_page(file_content: str):
    files = {"file": ("mne.html", file_content.encode("utf-8"), "text/html")}
    
    headers = {
        "User-Agent": "IT-TOP_bot/1.0",
        "X-Auth-Token": AUTH_TOKEN
    }
    
    try:
        async with httpx.AsyncClient() as client:

            response = await client.post(
                STORAGE_SERVICE_URL, 
                files=files, 
                headers=headers,
                timeout=5
                )
        if response.status_code == 200:
            return response.text.strip('"')
        elif response.status_code == 429:
            logger.error("Error: Too many requests (Rate limit)")
            return False
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

async def generate_marks_page(marks_list: list) -> str:

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("src/templates"))
    marks_template = env.get_template("marks.html")

    marks_html_content = marks_template.render(
        marks_list=marks_list
    )

    return await upload_html_page(marks_html_content)


