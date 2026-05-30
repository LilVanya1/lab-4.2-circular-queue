import tkinter as tk
from tkinter import messagebox, simpledialog
from ctypes import *
import os

backend_var = None
lib = None

def load_cpp():

    global lib

    path = os.path.join(os.path.dirname(__file__), "list_cpp.dll")

    dll = cdll.LoadLibrary(path)

    dll.createList.restype = None
    dll.clearList.restype = None
    dll.insertNode.argtypes = [c_int, c_ulonglong]
    dll.insertNode.restype = None
    dll.deleteNode.argtypes = [c_int]
    dll.deleteNode.restype = None
    dll.readByIndex.argtypes = [c_int]
    dll.readByIndex.restype = c_ulonglong
    dll.getCount.restype = c_int
    dll.getIndexByPos.argtypes = [c_int]
    dll.getIndexByPos.restype = c_int
    dll.getValueByPos.argtypes = [c_int]
    dll.getValueByPos.restype = c_ulonglong
    dll.extraFunction.argtypes = [c_int, c_int]
    dll.extraFunction.restype = None

    class CPPWrapper:

        def create_list(self):
            dll.createList()

        def clear_list(self):
            dll.clearList()

        def insert_node(self, i, v):
            dll.insertNode(i, v)

        def delete_node(self, i):
            dll.deleteNode(i)

        def read_node(self, i):
            return dll.readByIndex(i)

        def get_count(self):
            return dll.getCount()

        def get_index(self, p):
            return dll.getIndexByPos(p)

        def get_value(self, p):
            return dll.getValueByPos(p)

        def extra_function(self, o, p):
            dll.extraFunction(o, p)

    lib = CPPWrapper()


def load_python():

    global lib

    import list_python as py

    class PyWrapper:

        def create_list(self): py.create_list()
        def clear_list(self): py.clear_list()
        def insert_node(self, i, v): py.insert_node(i, v)
        def delete_node(self, i): py.delete_node(i)
        def read_node(self, i): return py.read_node(i)
        def get_count(self): return py.get_count()
        def get_index(self, p): return py.get_index(p)
        def get_value(self, p): return py.get_value(p)
        def extra_function(self, o, p): py.extra_function(o, p)

    lib = PyWrapper()


def switch_backend():

    choice = backend_var.get()

    if choice == "C++":
        try:
            load_cpp()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить C++ DLL:\n{e}\nПереключаю на Python.")
            backend_var.set("Python")
            load_python()
    else:
        load_python()

    refresh()


root = tk.Tk()
root.title("Лабораторная работа №4.2")
root.geometry("600x420")
root.configure(bg="#f2f2f2")

title = tk.Label(
    root,
    text="Работа со структурой данных",
    font=("Segoe UI", 16, "bold"),
    bg="#f2f2f2"
)
title.pack(pady=10)

backend_frame = tk.Frame(root, bg="#f2f2f2")
backend_frame.pack()

tk.Label(
    backend_frame,
    text="Библиотека:",
    bg="#f2f2f2"
).pack(side="left")

backend_var = tk.StringVar(value="C++")

tk.OptionMenu(
    backend_frame,
    backend_var,
    "C++",
    "Python",
    command=lambda e: switch_backend()
).pack(side="left")

input_frame = tk.Frame(root, bg="#f2f2f2")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Индекс").grid(row=0, column=0)
entry_index = tk.Entry(input_frame, width=10)
entry_index.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Значение").grid(row=1, column=0)
entry_value = tk.Entry(input_frame, width=10)
entry_value.grid(row=1, column=1, padx=5)

list_frame = tk.Frame(root)
list_frame.pack()

scrollbar = tk.Scrollbar(list_frame)

listbox = tk.Listbox(
    list_frame,
    width=40,
    height=12,
    yscrollcommand=scrollbar.set,
    font=("Consolas", 10)
)

scrollbar.config(command=listbox.yview)

listbox.pack(side="left")
scrollbar.pack(side="right", fill="y")


def refresh():

    listbox.delete(0, tk.END)

    if not lib:
        return

    count = lib.get_count()

    for i in range(count):

        idx = lib.get_index(i)
        val = lib.get_value(i)

        listbox.insert(tk.END, f"{idx} : {val}")


def create_list():

    if messagebox.askyesno(
        "Подтверждение",
        "Хотите создать новый список?\nТогда старый будет удалён."
    ):
        lib.clear_list()
        lib.create_list()
        refresh()


def clear_list():

    lib.clear_list()
    refresh()


def insert_node():

    try:

        idx = int(entry_index.get())
        val = int(entry_value.get())

        if idx < 1:
            messagebox.showerror("Ошибка", "Индекс должен быть больше единицы")
            return

        lib.insert_node(idx, val)

        refresh()

    except Exception:
        messagebox.showerror("Ошибка", "Введите ЧИСЛО")


def delete_node():

    try:

        idx = int(entry_index.get())

        count = lib.get_count()

        if count == 0:
            messagebox.showwarning("Ошибка", "Список пуст")
            return

        lib.delete_node(idx)

        refresh()

    except Exception:
        messagebox.showerror("Ошибка", "Введите индекс")


def read_node():

    try:

        idx = int(entry_index.get())

        if idx < 1:
            messagebox.showerror("Ошибка", "Индекс должен быть больше единицы")
            return

        count = lib.get_count()

        if count == 0:
            messagebox.showwarning("Ошибка", "Список пуст")
            return

        val = lib.read_node(idx)

        if val == 0:
            messagebox.showwarning("Ошибка", "Элемент не найден")
            return

        messagebox.showinfo(
            "Элемент",
            f"Индекс: {idx}\nЗначение: {val}"
        )

    except Exception:
        messagebox.showerror("Ошибка", "Введите индекс")


def show_all():

    count = lib.get_count()

    if count == 0:
        messagebox.showinfo("Список", "Список пуст")
        return

    text = ""

    for i in range(count):

        idx = lib.get_index(i)
        val = lib.get_value(i)

        text += f"{idx} : {val}\n"

    messagebox.showinfo("Все элементы", text)


def extra_function():
    count = lib.get_count()

    if count == 0:
        messagebox.showwarning("Ошибка", "Список пуст")
        return

    window = tk.Toplevel(root)
    window.title("доп возможность")
    window.geometry("300x300")
    window.configure(bg="#f2f2f2")

    tk.Label(window, text="выбор операции:", bg="#f2f2f2").pack(pady=5)

    op_var = tk.StringVar(value="Сложение")
    op_menu = tk.OptionMenu(window, op_var, "Сложение", "Умножение")
    op_menu.pack()

    tk.Label(window, text="куда вставить результат?", bg="#f2f2f2").pack(pady=5)

    place_var = tk.StringVar(value="В начало")
    place_menu = tk.OptionMenu(window, place_var, "В начало", "В середину", "В конец")
    place_menu.pack()

    def ready():
        op_value = 1 if op_var.get() == "Сложение" else 2

        if place_var.get() == "В начало":
            place_value = 1
        elif place_var.get() == "В середину":
            place_value = 2
        else:
            place_value = 3

        window.destroy()
        lib.extra_function(op_value, place_value)
        refresh()

    tk.Button(window, text="выполнить", command=ready).pack(pady=20)


def dops():
    window = tk.Toplevel(root)
    window.title("о программе")
    window.geometry("450x300")
    window.configure(bg="#f2f2f2")

    tk.Label(window, text="работа с двусвязным списком").pack(pady=20)


btn_frame = tk.Frame(root, bg="#f2f2f2")
btn_frame.pack(pady=10)


def btn(text, cmd, row):

    tk.Button(
        btn_frame,
        text=text,
        command=cmd,
        width=24
    ).grid(row=row, column=0, pady=3)


btn("Создать структуру", create_list, 0)
btn("Очистить структуру", clear_list, 1)
btn("Вставить элемент", insert_node, 2)
btn("Прочитать элемент", read_node, 3)
btn("Удалить элемент", delete_node, 4)
btn("Показать все элементы", show_all, 5)
btn("Дополнительная возможность", extra_function, 6)
btn("О программе", dops, 7)

# Пробуем C++, при ошибке автоматически падаем на Python
try:
    load_cpp()
except Exception:
    backend_var.set("Python")
    load_python()

refresh()

root.mainloop()
