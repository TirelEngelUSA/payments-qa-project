# Базовый класс (наш "контракт")
class BaseHandler:
    def process(self, data):
        # Этот метод должны будут переопределить все потомки
        raise NotImplementedError("Дочерний класс должен реализовать метод process()!")

# Конкретные классы-обработчики
class TextFileHandler(BaseHandler):
    def process(self, text_data):
        print(f"[Текст]: Обработка {len(text_data)} символов...")
        # ... какая-то логика ...
        return "TEXT_OK"

class JsonHandler(BaseHandler):
    def process(self, json_data):
        print(f"[JSON]: Найдено ключей: {len(json_data.keys())}")
        # ... какая-то логика ...
        return "JSON_OK"


# Наша "фабрика"
def process_data(data):
    print(f"\nПолучены данные типа: {type(data)}")

    # Создаем экземпляры всех наших обработчиков
    handlers = [TextFileHandler(), JsonHandler()]

    # А теперь ищем подходящий
    for handler in handlers:
        # Вот здесь мы используем isinstance() для гибкости!
        if isinstance(data, str) and isinstance(handler, TextFileHandler):
            print("Найден обработчик для текста.")
            return handler.process(data)
        elif isinstance(data, dict) and isinstance(handler, JsonHandler):
            print("Найден обработчик для JSON (словаря).")
            return handler.process(data)

    print("Ошибка: Подходящий обработчик не найден.")
    return None


# --- Тестируем ---
text_from_file = "Это пример простого текстового файла."
json_from_web = {"user_id": 123, "status": "active", "items": [1, 2, 3]}
list_from_db = [10, 20, 30]

process_data(text_from_file)
process_data(json_from_web)
process_data(list_from_db)  # Для этого типа у нас нет обработчика