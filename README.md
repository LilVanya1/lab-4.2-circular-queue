# Лабораторная 4.2 — GUI + структура данных

**Студент:** Изместьев М.Н., гр. ИВТб-1302-06-00  
**Тема:** tkinter + интеграция модулей C++ / Python  
**Структура в отчёте:** кольцевая очередь (Circular Queue)  
**GitHub (upload):** `lab-4.2-circular-queue`

## Статус

| Компонент | Статус |
|-----------|--------|
| Код (`app.py`, `list_python.py`, `list_cpp.cpp`) | ✅ |
| Блок-схемы `drawio/` (35 файлов) | ✅ drawio |
| PNG из drawio | ❌ не отрендерены |
| Отчёт `report/main.tex` | ✅ |
| Скрины GUI `report/img/1.png`…`5.png` | ❌ |
| `list_cpp.dll` | ❌ нужна сборка |

## Структура

```
lab4dot2/
├── app.py              # GUI tkinter
├── list_python.py      # Python-бэкенд
├── list_cpp.cpp        # C++ DLL (исходник)
├── drawio/             # блок-схемы (единственная лаба, где они в отчёте)
├── FLOWCHART_GUIDE.md  # стандарт оформления схем
└── report/
    ├── main.tex
    └── img/            # ← сюда 5 скринов GUI
```

## Запуск

```powershell
cd c:\Users\stud222640\Documents\proga\lab4dot2

# 1. Собрать DLL (MinGW)
g++ -shared -o list_cpp.dll list_cpp.cpp -std=c++17

# 2. GUI
python app.py
```

Без DLL работает только Python-бэкенд (переключатель в интерфейсе).

## Блок-схемы

```powershell
cd c:\Users\stud222640\Documents\proga
python _tools\sync_drawio.py
```

Подробности — `FLOWCHART_GUIDE.md`.

## Сдача

1. Скрины GUI → `report/img/1.png` … `5.png`
2. PDF из `report/main.tex`
3. Ссылка на репозиторий в отчёте
