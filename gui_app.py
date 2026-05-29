import tkinter as tk
from tkinter import messagebox
import ctypes
import os
import sys
import math
import random

# Пытаемся импортировать файл circular_queue_py.py с классом Sruct
# Это нужно для работы Python-версии очереди
try:
    from circular_queue_py import Sruct
except ImportError:
    # Если файл не найден, будем использовать обычный список вместо Sruct
    Sruct = None


# Базовый класс (интерфейс), чтобы все реализации очереди выглядели одинаково
# Это позволяет легко менять Python на C++ и обратно, не меняя код кнопок
class QueueBackend:
    def init(self): pass
    def add(self, val): pass
    def dequeue(self): return None
    def peek(self): return None
    def clear(self): pass
    def size(self): return 0
    def get_elements(self): return []


# Реализация очереди на языке Python
# Этот класс работает либо с Sruct (если есть), либо с обычным list
class PythonBackend(QueueBackend):
    def __init__(self):
        self.q = None
        # Флаг, указывающий, используем ли мы заглушку (список) или реальный класс
        self.is_list = Sruct is None

    # Инициализация структуры данных
    def init(self):
        if Sruct:
            self.q = Sruct()
            self.is_list = False
        else:
            self.q = []
            self.is_list = True

    # Добавление элемента в конец
    def add(self, val):
        if self.q is None:
            return
        if self.is_list:
            self.q.append(val)
        else:
            self.q.add(val)

    # Удаление элемента из начала
    def dequeue(self):
        if self.q is None:
            return None
        if self.is_list:
            # Если список не пуст, удаляем нулевой элемент
            return self.q.pop(0) if self.q else None
        return self.q.dequeue()

    # Просмотр первого элемента без удаления
    def peek(self):
        if self.q is None:
            return None
        if self.is_list:
            return self.q[0] if self.q else None
        return self.q.peek()

    # Полная очистка очереди
    def clear(self):
        if self.q is None:
            return
        if self.is_list:
            self.q.clear()
        else:
            self.q.clear()

    # Получение текущего количества элементов
    def size(self):
        if self.q is None:
            return 0
        return len(self.q) if self.is_list else self.q.get_size()

    # Возвращает список всех элементов для рисования на экране
    def get_elements(self):
        if self.q is None:
            return []
        # Конвертируем структуру в список Python для удобства
        return list(self.q) if self.is_list else self.q.get_elements()


# Реализация очереди через вызов внешних C++ функций (DLL/.so)
# Использует библиотеку ctypes для связи Python и C++
class CppBackend(QueueBackend):
    def __init__(self, path):
        self.lib = None
        # Проверяем, существует ли файл библиотеки по указанному пути
        if os.path.exists(path):
            # Загружаем динамическую библиотеку
            self.lib = ctypes.CDLL(path)

            # Настраиваем типы данных для функции инициализации (void)
            self.lib.lib_init.restype = None

            # Настраиваем функцию добавления: принимает int, возвращает int (код ошибки)
            self.lib.lib_add.restype = ctypes.c_int
            self.lib.lib_add.argtypes = [ctypes.c_int]

            # Настраиваем dequeue: принимает указатель на int (куда записать результат)
            self.lib.lib_dequeue.restype = ctypes.c_int
            self.lib.lib_dequeue.argtypes = [ctypes.POINTER(ctypes.c_int)]

            # Настраиваем peek: аналогично принимает указатель
            self.lib.lib_peek.restype = ctypes.c_int
            self.lib.lib_peek.argtypes = [ctypes.POINTER(ctypes.c_int)]

            # Настраиваем очистку и получение размера
            self.lib.lib_clear.restype = None
            self.lib.lib_size.restype = ctypes.c_int

            # Настраиваем получение массива: принимает указатель на буфер и его размер
            self.lib.lib_get_elements.restype = ctypes.c_int
            self.lib.lib_get_elements.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]

    # Проверка: загрузилась ли библиотека успешно
    def is_valid(self):
        return self.lib is not None

    # Вызов C++ функции инициализации
    def init(self):
        if self.lib:
            self.lib.lib_init()

    # Вызов C++ функции добавления
    def add(self, val):
        if self.lib:
            self.lib.lib_add(val)

    # Вызов C++ функции удаления
    def dequeue(self):
        if not self.lib:
            return None
        # Создаем C-переменную типа int для получения результата
        val = ctypes.c_int()
        # Передаем её по ссылке (byref), чтобы C++ мог записать туда значение
        res = self.lib.lib_dequeue(ctypes.byref(val))
        # Если res (результат функции) true/1, возвращаем значение, иначе None
        return val.value if res else None

    # Вызов C++ функции просмотра
    def peek(self):
        if not self.lib:
            return None
        val = ctypes.c_int()
        res = self.lib.lib_peek(ctypes.byref(val))
        return val.value if res else None

    # Очистка памяти в C++
    def clear(self):
        if self.lib:
            self.lib.lib_clear()

    # Получение размера очереди из C++
    def size(self):
        return self.lib.lib_size() if self.lib else 0

    # Получение всех элементов из C++ для отрисовки
    def get_elements(self):
        if not self.lib:
            return []
        # Создаем C-массив (буфер) на 10000 элементов
        buf = (ctypes.c_int * 10000)()
        # Заполняем буфер данными из DLL
        count = self.lib.lib_get_elements(buf, 10000)
        # Превращаем C-массив в обычный Python-список через генератор
        return [buf[i] for i in range(count)]


# Главный класс приложения (GUI и логика взаимодействия)
class App:
    def __init__(self, root):
        self.root = root
        self.backend = None # Здесь будет храниться текущий активный бэкенд
        self.is_created = False #Проверка на то создана ли структура
        # Определяем папку, где лежит скрипт
        base = os.path.dirname(os.path.abspath(__file__))
        # Выбираем расширение файла библиотеки в зависимости от ОС (Windows или Linux)
        ext = ".dll" if sys.platform == "win32" else ".so"

        # Словарь всех доступных бэкендов с путями к файлам
        self.backends = {
            "Python": PythonBackend(),
            "C++ Dynamic": CppBackend(os.path.join(base, "circular_queue_dynamic" + ext)),
            "C++ STL": CppBackend(os.path.join(base, "circular_queue_stl" + ext))
        }

        # Запускаем создание интерфейса
        self.setup_ui()

    # Метод настройки всех кнопок, полей и надписей
    def setup_ui(self):
        # Верхняя панель для выбора типа очереди (Radiobuttons)
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top, text="Бэкенд:").pack(side=tk.LEFT)

        # Переменная для хранения выбора пользователя
        self.bk_var = tk.StringVar(value="Python")

        # Создаем радиокнопки динамически
        for name, bk in self.backends.items():
            # Показываем C++ опции, ТОЛЬКО если библиотека реально загрузилась
            if name == "Python" or (isinstance(bk, CppBackend) and bk.is_valid()):
                tk.Radiobutton(top, text=name, variable=self.bk_var, value=name,
                               command=self.on_change_backend).pack(side=tk.LEFT)

        # Текстовая метка статуса (красная/зеленая)
        self.lbl_status = tk.Label(self.root, text="Не создано", fg="red")
        self.lbl_status.pack()

        # Холст (Canvas), на котором мы будем рисовать круги и стрелки
        self.canvas = tk.Canvas(self.root, width=880, height=380, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(padx=10, pady=5)
        self.draw_text("Структура не создана")

        # Панель для полей ввода (Input)
        inp = tk.Frame(self.root)
        inp.pack(fill=tk.X, padx=10)

        # Создаем поля ввода с помощью вспомогательной функции (чтобы кода было меньше)
        self.ent_val = self.mk_entry(inp, "Значение:", 8)
        self.ent_cnt = self.mk_entry(inp, "Кол-во:", 5)
        self.ent_min = self.mk_entry(inp, "Мин:", 5)
        self.ent_max = self.mk_entry(inp, "Макс:", 5)

        # Панель для кнопок действий
        btns = tk.Frame(self.root)
        btns.pack(fill=tk.X, padx=10, pady=5)

        # Создаем кнопки и привязываем их к функциям класса
        self.mk_btn(btns, "Создать", self.create)
        self.mk_btn(btns, "Добавить", self.add)
        self.mk_btn(btns, "Удалить", self.dequeue)
        self.mk_btn(btns, "Peek", self.peek)
        self.mk_btn(btns, "Случайные", self.rand_add)
        self.mk_btn(btns, "Очистить", self.clear)

        # Нижнее текстовое поле для логов (история действий)
        self.log_txt = tk.Text(self.root, height=6, state=tk.DISABLED, bg="#f0f0f0")
        self.log_txt.pack(fill=tk.BOTH, padx=10, pady=5)

    # Функция-помощник: создает Label + Entry и возвращает Entry
    def mk_entry(self, parent, txt, w):
        tk.Label(parent, text=txt).pack(side=tk.LEFT, padx=5)
        e = tk.Entry(parent, width=w)
        e.pack(side=tk.LEFT)
        return e

    # Функция-помощник: создает Button
    def mk_btn(self, parent, txt, cmd):
        tk.Button(parent, text=txt, command=cmd, width=10).pack(side=tk.LEFT, padx=2)

    # Функция логирования: добавляет текст в нижнее окно и прокручивает его
    def log(self, msg):
        self.log_txt.config(state=tk.NORMAL) # Разрешаем редактирование
        self.log_txt.insert(tk.END, msg + "\n") # Пишем текст
        self.log_txt.see(tk.END) # Прокручиваем вниз
        self.log_txt.config(state=tk.DISABLED) # Запрещаем редактирование

    # нажата ли кнопка создать
    def check_created(self):
        if not self.is_created:
            messagebox.showinfo("Внимание", "Создайте структуру!")
            return False
        return True

    # Срабатывает при смене радиокнопки (Python <-> C++)
    def on_change_backend(self):
        self.is_created = False # Сбрасываем флаг
        self.backend = None
        self.lbl_status.config(text="Сменен бэкенд (не создано)", fg="red")
        self.canvas.delete("all") # Очищаем рисунок
        self.draw_text("Структура не создана")
        self.log("Бэкенд сменён на: " + self.bk_var.get())

    # Кнопка "Создать": инициализирует выбранный бэкенд
    def create(self):
        name = self.bk_var.get() # Получаем имя (Python или C++...)
        self.backend = self.backends[name] # Берем нужный объект из словаря
        self.backend.init() # Вызываем его init
        self.is_created = True
        self.refresh() # Перерисовываем экран
        self.log("Создана структура: " + name)

    # Кнопка "Добавить": читает число и добавляет в очередь
    def add(self):
        if not self.check_created():
            return
        val_str = self.ent_val.get()
        # Проверка на пустоту
        if val_str == "":
            messagebox.showerror("Ошибка", "Введите число!")
            return
        # Проверка на то, что введено целое число
        try:
            val = int(val_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число!")
            return
        # Добавляем в бэкенд
        self.backend.add(val)
        self.ent_val.delete(0, tk.END) # Очищаем поле ввода
        self.refresh() # Обновляем картинку
        self.log("Добавлен: " + str(val))

    # Кнопка "Удалить": извлекает элемент из головы очереди
    def dequeue(self):
        if not self.check_created():
            return
        # Нельзя удалять из пустой очереди
        if self.backend.size() == 0:
            messagebox.showwarning("Внимание", "Очередь пуста! Нечего удалять.")
            self.log("Ошибка: удаление из пустой очереди.")
            return
        val = self.backend.dequeue()
        self.refresh()
        self.log("Удален: " + str(val))

    # Кнопка "Peek": показывает первый элемент, не удаляя его
    def peek(self):
        if not self.check_created():
            return
        if self.backend.size() == 0:
            messagebox.showwarning("Внимание", "Очередь пуста!")
            self.log("Ошибка: peek из пустой очереди.")
            return
        val = self.backend.peek()
        messagebox.showinfo("Peek", "Первый элемент: " + str(val))
        self.log("Peek: " + str(val))

    # Кнопка "Случайные": добавляет N случайных чисел
    def rand_add(self):
        if not self.check_created():
            return
        try:
            cnt = int(self.ent_cnt.get()) # Кол-во
            mn = int(self.ent_min.get())  # Минимум
            mx = int(self.ent_max.get())  # Максимум
        except ValueError:
            messagebox.showerror("Ошибка", "Заполните все поля целыми числами!")
            return

        # Логические проверки входных данных
        if cnt <= 0:
            messagebox.showerror("Ошибка", "Количество должно быть положительным!")
            return
        if mn > mx:
            messagebox.showerror("Ошибка", "Минимум больше максимума!")
            return

        # Цикл добавления случайных чисел
        for _ in range(cnt):
            self.backend.add(random.randint(mn, mx))
        self.refresh()
        self.log("Добавлено " + str(cnt) + " случайных чисел [" + str(mn) + ", " + str(mx) + "]")

    # Кнопка "Очистить": удаляет всё
    def clear(self):
        if not self.check_created():
            return
        old_size = self.backend.size()
        self.backend.clear()
        self.refresh()
        self.log("Очередь очищена. Удалено: " + str(old_size))

    # Основная функция отрисовки на Canvas
    def refresh(self):
        self.canvas.delete("all") # Удаляем старый рисунок
        if not self.is_created:
            self.draw_text("Структура не создана")
            return

        # Получаем актуальные данные из бэкенда
        elems = self.backend.get_elements()
        sz = len(elems)

        # Обновляем метку статуса
        self.lbl_status.config(
            text="Бэкенд: " + self.bk_var.get() + " | Размер: " + str(sz),
            fg="green")

        if sz == 0:
            self.draw_text("Очередь пуста")
            return

        # Настройки геометрии круга
        cx = 440 # Центр по X
        cy = 200 # Центр по Y
        # Если элементов много, увеличиваем радиус круга
        r = 30 + sz * 12 if sz < 10 else 150
        nr = 22 # Радиус маленького кружка (узла)

        # Вычисляем координаты всех узлов по кругу
        coords = []
        for i in range(sz):
            # Математика: угол для текущего элемента
            # -pi/2 означает начало сверху (12 часов)
            ang = -math.pi / 2 + 2 * math.pi * i / sz
            # Формула перевода полярных координат в декартовы
            coords.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

        # 1. Сначала рисуем стрелки (связи), чтобы они были ПОД кружками
        for i in range(sz):
            x1, y1 = coords[i] # Текущий узел
            x2, y2 = coords[(i + 1) % sz] # Следующий узел (кольцевой буфер)

            # Вычисляем вектор направления, чтобы стрелка не заходила внутрь кружка
            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx * dx + dy * dy)
            if dist == 0:
                continue

            # Смещаем начало и конец линии на радиус узла
            sx = x1 + (dx / dist) * nr
            sy = y1 + (dy / dist) * nr
            ex = x2 - (dx / dist) * nr
            ey = y2 - (dy / dist) * nr

            # Рисуем линию со стрелочкой на конце
            self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, fill="#555", width=2)

        # 2. Рисуем сами узлы поверх стрелок
        for i in range(sz):
            x, y = coords[i]
            # Выбираем цвет: первый - зеленый, последний - красный, остальные - синие
            if i == 0:
                col = "#4CAF50" # HEAD
            elif i == sz - 1:
                col = "#F44336" # TAIL
            else:
                col = "#2196F3"

            # Рисуем цветной круг
            self.canvas.create_oval(x - nr, y - nr, x + nr, y + nr, fill=col, width=2)
            # Пишем число внутри круга
            self.canvas.create_text(x, y, text=str(elems[i]), fill="white",
                                    font=("Arial", 10, "bold"))

        # Добавляем текстовые подписи HEAD и TAIL рядом с первым и последним
        self.canvas.create_text(coords[0][0], coords[0][1] - nr - 12,
                                text="HEAD", fill="green", font=("Arial", 9, "bold"))
        self.canvas.create_text(coords[-1][0], coords[-1][1] + nr + 12,
                                text="TAIL", fill="red", font=("Arial", 9, "bold"))

    # Вспомогательная функция рисования текста в центре (для ошибок/статусов)
    def draw_text(self, txt):
        self.canvas.create_text(440, 190, text=txt, font=("Arial", 16), fill="gray")


# Точка входа в программу. Если файл запущен напрямую, создаем окно.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Циклическая очередь")
    root.geometry("1x720")
    root.resizable(True, True) # Запрещаем менять размер окна
    app = App(root) # Создаем экземпляр приложения
    root.mainloop() # Запускаем бесконечный цикл обработки событий