import datetime
import json
from api.Journal_API import API

with open("src/api/creds.json", "r") as file:
  json_config = json.loads(file.read())

USER = json_config["username"]
PASS = json_config["password"]

User = API(USER, PASS)

def print_today_schedule():
  today_in_iso = datetime.datetime.today().isoformat()[:10]
  today_schedule = User.get_schedule_by_date(today_in_iso)

  for lesson_json in today_schedule:
      lesson_number = lesson_json["lesson"]
      start_time = lesson_json["started_at"]
      end_time = lesson_json["finished_at"]
      teacher = lesson_json["teacher_name"]
      subject = lesson_json["subject_name"]
      where = lesson_json["room_name"]

      print(f"""Пара {lesson_number} ({subject}):
              Начнется в: {start_time}
              Закончится в: {end_time}
              Ведет: {teacher}
              В кабинете: {where}
            
            """)
      

if __name__ == "__main__":
  print_today_schedule()
