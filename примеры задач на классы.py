class Account:
    def __init__(self, balance):
        self.balance = balance

    def transfer(self, other, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        if not hasattr(other, "balance"):
            raise TypeError("Получатель должен иметь атрибут balance")

        self.balance -= amount
        other.balance += amount

class User:
    user_count = 0  # переменная класса

    def __init__(self, name, email):
        self.name = name
        self.email = email
        User.user_count += 1  # увеличиваем при создании объекта

class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount

class SavingsAccount(Account):
    def __init__(self, balance, interest_rate):
        super().__init__(balance)
        self.interest_rate = interest_rate

    def apply_interest(self):
        self.balance += self.balance * self.interest_rate

class Example:
    class_var = 0

    def __init__(self, value):
        self.value = value

    def instance_method(self):
        return self.value * 2

    @classmethod
    def class_method(cls):
        cls.class_var += 1
        return cls.class_var

    @staticmethod
    def static_method(x, y):
        return x + y

Вызовы:
obj = Example(10)

# метод экземпляра
obj.instance_method()        # 20

# метод класса
Example.class_method()       # 1
obj.class_method()           # 2 (работает через объект тоже)

# статический метод
Example.static_method(3, 4)  # 7
obj.static_method(5, 6)      # 11

🔹 1. Сумма элементов списка
Задача

Написать функцию, которая возвращает сумму всех чисел в списке.

def sum_list(nums):
    total = 0
    for n in nums:
        total += n
    return total


💡 Пояснение:

Используем цикл для накопления суммы

Можно также использовать sum(nums) для короткой версии

🔹 2. Проверка на палиндром
Задача

Функция проверяет, является ли строка палиндромом.

def is_palindrome(s):
    s = s.lower()  # приведение к одному регистру
    return s == s[::-1]


💡 Пояснение:

[::-1] переворачивает строку

Сравниваем с исходной строкой

🔹 3. Максимум в списке
Задача

Найти максимальное число в списке.

def find_max(nums):
    if not nums:
        return None
    max_num = nums[0]
    for n in nums:
        if n > max_num:
            max_num = n
    return max_num


💡 Пояснение:

Инициализация максимума первым элементом

Проверка всех элементов списка

🔹 4. Чётные числа
Задача

Вернуть все чётные числа из списка.

def get_even(nums):
    result = []
    for n in nums:
        if n % 2 == 0:
            result.append(n)
    return result


💡 Пояснение:

Используем % 2 для проверки чётности

Сохраняем в новый список

🔹 5. Подсчёт уникальных элементов
Задача

Посчитать количество уникальных чисел в списке.

def count_unique(nums):
    return len(set(nums))


💡 Пояснение:

set автоматически убирает дубликаты

len возвращает количество

🔹 6. Фильтр положительных чисел
Задача

Вернуть только положительные числа из списка.

def positive_numbers(nums):
    return [n for n in nums if n > 0]


💡 Пояснение:

Списковые включения (list comprehension)

Проверка n > 0

🔹 7. Факториал числа
Задача

Вычислить факториал числа n.

def factorial(n):
    result = 1
    for i in range(2, n+1):
        result *= i
    return result


💡 Пояснение:

Используем цикл от 2 до n

Накапливаем произведение

🔹 8. Проверка делимости
Задача

Проверить, делится ли число на 3 и на 5 одновременно.

def divisible_by_3_and_5(n):
    return n % 3 == 0 and n % 5 == 0


💡 Пояснение:

Используем логическое and

% для остатка

🔹 9. Обратная строка
Задача

Вернуть обратную строку.

def reverse_string(s):
    return s[::-1]


💡 Пояснение:

Срез [::-1] — простейший способ переворота строки

🔹 10. Сумма положительных чисел
Задача

Вернуть сумму только положительных чисел из списка.

def sum_positive(nums):
    total = 0
    for n in nums:
        if n > 0:
            total += n
    return total