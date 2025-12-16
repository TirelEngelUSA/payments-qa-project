class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __str__(self):
        # "Человекочитаемое" представление
        return f"Пользователь {self.username}"

    def __repr__(self):
        # "Однозначное" представление для разработчика
        # Обратите внимание на !r после имен атрибутов
        return f"User(username={self.username!r}, email={self.email!r})"

# Создаем пользователя
user_alex = User("Alex", "alex@example.com")

# 1. print() использует __str__ (если он есть)
print("--- Вывод print() ---")
print(user_alex)

# 2. repr() всегда использует __repr__
print("\n--- Вывод repr() ---")
print(repr(user_alex))

# 3. Печать контейнера использует __repr__ для своих элементов
print("\n--- Вывод списка с объектом ---")
users_list = [user_alex]
print(users_list)