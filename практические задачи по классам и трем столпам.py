class Vehicle:
    vehicles_created = 0

    def __init__(self, brand, max_speed):
        Vehicle.vehicles_created += 1
        self.brand = brand
        self._max_speed = max_speed
        self._mileage = 0

    def get_max_speed(self):
        return self._max_speed

    def get_mileage(self):
        return self._mileage

    def drive(self, distance):
        self._mileage += distance

    def display_info(self):
        print(f"Марка: {self.brand}\nМакс. скорость: {self._max_speed} км/ч\nПробег: {self._mileage} км")


class Car(Vehicle):
    def __init__(self, brand, max_speed, engine_type):
        super().__init__(brand, max_speed)
        self.engine_type = engine_type

    def display_info(self):
        super().display_info()
        print(f"Тип двигателя: {self.engine_type}")


class Bicycle(Vehicle):
    def __init__(self, brand, max_speed, frame_material):
        super().__init__(brand, max_speed)
        self.frame_material = frame_material

    def display_info(self):
        super().display_info()
        print(f"Материал рамы: {self.frame_material}")


# Создаем объекты разных классов
tesla = Car("Tesla", 250, "Электро")
bmw = Car("BMW", 280, "Бензин")
trek = Bicycle("Trek", 40, "Карбон")

# Демонстрируем полиморфизм: работаем с разными объектами через общий интерфейс
vehicles = [tesla, bmw, trek]
for vehicle in vehicles:
    print("---")
    vehicle.display_info() # Один и тот же вызов - разное поведение
    vehicle.drive(100)
    print(f"Пробег после поездки: {vehicle.get_mileage()} км")

print("\n" + "="*30)
# Демонстрируем работу атрибута класса
print(f"Всего создано транспортных средств: {Vehicle.vehicles_created}")


# Базовый класс Publication (Издание)
class Publication:
    def __init__(self, title, author, year):
        self.title = title         # Публичный атрибут
        self._author = author      # Защищенный атрибут
        self._year = year          # Защищенный атрибут

    def get_info(self):
        # Возвращает строку с базовой информацией
        return f'"{self.title}" ({self._author}, {self._year})'


# Дочерний класс Book (Книга)
class Book(Publication):
    def __init__(self, title, author, year, isbn):
        super().__init__(title, author, year)
        self.isbn = isbn           # ISBN к книге

    def get_info(self):
        # Расширение родительского метода get_info
        base_info = super().get_info()  # Получаем информацию из родительского класса
        return f'{base_info}, ISBN: {self.isbn}'  # Добавляем информацию об ISBN


# Дочерний класс Magazine (Журнал)
class Magazine(Publication):
    def __init__(self, title, editor, year, issue_number):
        super().__init__(title, editor, year)
        self.issue_number = issue_number  # Номер выпуска журнала

    def get_info(self):
        base_info = super().get_info()  # Получаем информацию из родительского класса
        # Переписываем представление, обозначив редактора и добавив номер выпуска
        return f'"{self.title}" (Ред. {self._author}, {self._year}), Выпуск №{self.issue_number}'

# Создаем объекты разных классов
book = Book("Война и мир", "Лев Толстой", 1869, "978-5-389-06254-2")
magazine = Magazine("National Geographic", "Сьюзан Голдберг", 2021, 8)

# Демонстрируем полиморфизм
publications = [book, magazine]
for pub in publications:
    # Один и тот же вызов - разное поведение
    print(pub.get_info())



# Базовый класс персонажа
class Character:
    def __init__(self, name, damage):
        self.name = name              # Публичный атрибут (имя персонажа)
        self._health = 100            # Защищённый атрибут (начальное здоровье)
        self._damage = damage         # Защищённый атрибут (урон)

    def attack(self, target):
        # Метод атаки: если цель имеет метод take_damage, вызываем его
        if hasattr(target, 'take_damage'):
            target.take_damage(self._damage)

    def take_damage(self, amount):
        # Метод уменьшения здоровья
        self._health -= amount

    def get_status(self):
        # Метод для получения статуса персонажа
        return f"Имя: {self.name}, Здоровье: {self._health}"


# Дочерний класс Warrior (Воин)
class Warrior(Character):
    def __init__(self, name, damage, armor):
        super().__init__(name, damage)  # Инициализация базовых атрибутов
        self.armor = armor              # Дополнительный атрибут (броня)

    def take_damage(self, amount):
        # Воин получает урон, уменьшенный на величину брони
        reduced_damage = max(0, amount - self.armor)  # Урон не может быть отрицательным
        self._health -= reduced_damage


# Дочерний класс Mage (Маг)
class Mage(Character):
    def __init__(self, name, damage, mana):
        super().__init__(name, damage)  # Инициализация базовых атрибутов
        self.mana = mana                # Дополнительный атрибут (мана)

    def attack(self, target):
        # Маг тратит 10 единиц маны за атаку
        if self.mana >= 10:
            self.mana -= 10  # Мана уменьшается
            super().attack(target)  # Вызываем родительский метод атаки

# Создаем персонажей
warrior = Warrior("Конан", 15, 5) # Урон 15, Броня 5
mage = Mage("Раистлин", 20, 100) # Урон 20, Мана 100

print(warrior.get_status())
print(mage.get_status())
print("--- Битва ---")

# Маг атакует воина
mage.attack(warrior)
print(warrior.get_status()) # Воин должен получить 15 урона (20 - 5 брони)

# Воин атакует мага
warrior.attack(mage)
print(mage.get_status()) # Маг должен получить 15 урона

# Проверка логики мага
mage.mana = 5 # Устанавливаем мало маны
mage.attack(warrior)
print(warrior.get_status()) # Здоровье воина не должно измениться