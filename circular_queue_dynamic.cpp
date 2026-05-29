#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

struct Uzl {
    int data;
    Uzl* next;
};

struct Sruct {
    Uzl* tail;
    int size;
};

static Sruct queue; // глобальная очередь, живёт пока загружена DLL

// extern "C" отключает name mangling чтобы ctypes нашёл функции по имени
extern "C" {

EXPORT void lib_init() {
    queue.tail = nullptr;
    queue.size = 0;
}

EXPORT int lib_add(int value) {
    Uzl* newUzl = new Uzl;
    newUzl->data = value;

    if (queue.tail == nullptr) {
        newUzl->next = newUzl; // единственный узел ссылается сам на себя
        queue.tail = newUzl;
    } else {
        newUzl->next = queue.tail->next; // новый узел -> старая голова
        queue.tail->next = newUzl;       // старый хвост -> новый узел
        queue.tail = newUzl;             // хвост сдвигается на новый узел
    }

    queue.size++;
    return 1;
}

EXPORT int lib_dequeue(int* value) {
    if (queue.tail == nullptr) {
        return 0;
    }

    Uzl* head = queue.tail->next; // голова = следующий за хвостом в кольце
    *value = head->data;

    if (queue.tail == head) { // был один элемент
        queue.tail = nullptr;
    } else {
        queue.tail->next = head->next; // исключаем голову из кольца
    }

    delete head;
    queue.size--;
    return 1;
}

EXPORT int lib_peek(int* value) {
    if (queue.tail == nullptr) {
        return 0;
    }

    *value = queue.tail->next->data; // tail->next это голова
    return 1;
}

EXPORT void lib_clear() {
    int value;
    while (queue.size > 0) {
        lib_dequeue(&value);
    }
}

EXPORT int lib_size() {
    return queue.size;
}

// копирует элементы в буфер для передачи в Python через ctypes
EXPORT int lib_get_elements(int* buffer, int maxSize) {
    if (queue.tail == nullptr || maxSize <= 0) {
        return 0;
    }

    Uzl* current = queue.tail->next; // начинаем с головы
    int count = 0;

    for (int i = 0; i < queue.size && i < maxSize; i++) {
        buffer[i] = current->data;
        current = current->next;
        count++;
    }

    return count;
}

}