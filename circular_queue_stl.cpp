#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#include <list> // list сам управляет памятью
// std - пространство имён (standard)
static std::list<int> queue; // Создаём двусвязный список, принадлежащий std и задаём переменную

extern "C" {

EXPORT void lib_init() {
    queue.clear();
}

EXPORT int lib_add(int value) {
    queue.push_back(value); //добавляем в конец списка
    return 1;
}

EXPORT int lib_dequeue(int* value) {
    if (queue.empty()) {
        return 0;
    }

    *value = queue.front();
    queue.pop_front();
    return 1;
}

EXPORT int lib_peek(int* value) {
    if (queue.empty()) {
        return 0;
    }

    *value = queue.front();
    return 1;
}

EXPORT void lib_clear() {
    queue.clear();
}

EXPORT int lib_size() {
    return (int)queue.size();
}

EXPORT int lib_get_elements(int* buffer, int maxSize) {
    if (queue.empty() || maxSize <= 0) {
        return 0;
    }

    int count = 0; //begin() - первый элемент
    for (auto current = queue.begin(); current != queue.end() && count < maxSize; ++current) {
        buffer[count] = *current; //записываем в буфер текущее значение по индексу
        count++;
    }

    return count;
}

}