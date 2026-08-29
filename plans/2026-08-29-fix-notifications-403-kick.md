# 2026-08-29 fix notifications thunder herd + 403 kick

## Фазы
- [x] Фаза 1 — storage: failed_403_counts dict
- [x] Фаза 2 — Journal_API: явный return 401/403/422
- [x] Фаза 3 — almost_expired_homework: батчинг 20 + sleep 2 + jitter 0-90 + кик 3 цикла
- [x] Фаза 4 — верификация (syntax + логика кика + батчей)

## Что сделано
- `src/storage.py:20` — failed_403_counts RAM dict
- `src/api/Journal_API.py:20-112` — __exception_handler возвращает 422 явно, __send_*_request возвращает code если not None, иначе после 3 ретраев возвращает статус 401/403/422
- `src/bot/notifications/almost_expired_homework.py` — _handle_auth_error (3× кик + delete_user+delete_settings+notify), jitter, batch gather 20, sleep 0.05 между страницами, убраны print

## Верификация
- syntax OK для 3 файлов
- логика кика: 3×403 -> delete + notify, 2×403+успех -> сброс, батч 45 юзеров -> 45 вызовов

## Осталось
- Прод тест на реальных 100 юзерах в 59 минуту — наблюдать логи "Кикаю" и "Рассылка завершена"
