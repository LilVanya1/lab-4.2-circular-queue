#include "pch.h"
#include <windows.h>
#include <stdlib.h>

typedef unsigned long long ULL;

struct Node
{
    int index;
    ULL value;
    Node* prev;
    Node* next;
};

Node* head = NULL;
Node* tail = NULL;


Node* createNode(int index, ULL value)
{
    Node* n = (Node*)malloc(sizeof(Node));

    n->index = index;
    n->value = value;
    n->prev = NULL;
    n->next = NULL;

    return n;
}


extern "C" __declspec(dllexport) void createList()
{
    head = NULL;
    tail = NULL;
}


extern "C" __declspec(dllexport) void clearList()
{
    Node* p = head;

    while (p)
    {
        Node* t = p;
        p = p->next;
        free(t);
    }

    head = NULL;
    tail = NULL;
}


extern "C" __declspec(dllexport) void insertNode(int index, ULL value)
{
    Node* n = createNode(index, value);

    if (!head)
    {
        head = tail = n;
        return;
    }

    Node* p = head;

    while (p && p->index < index)
        p = p->next;

    if (!p)
    {
        tail->next = n;
        n->prev = tail;
        tail = n;
    }
    else
    {
        n->next = p;
        n->prev = p->prev;

        if (p->prev)
            p->prev->next = n;
        else
            head = n;

        p->prev = n;
    }
}

Node* findByIndex(int index)
{
    Node* p = head;

    while (p)
    {
        if (p->index == index)
            return p;

        p = p->next;
    }

    return NULL;
}


extern "C" __declspec(dllexport) ULL readByIndex(int index)
{
    Node* p = findByIndex(index);

    if (p)
        return p->value;

    return 0;
}


extern "C" __declspec(dllexport) void deleteNode(int index)
{
    Node* p = findByIndex(index);

    if (!p)
        return;

    if (p->prev)
        p->prev->next = p->next;
    else
        head = p->next;

    if (p->next)
        p->next->prev = p->prev;
    else
        tail = p->prev;

    free(p);
}


extern "C" __declspec(dllexport) int getCount()
{
    int c = 0;

    Node* p = head;

    while (p)
    {
        c++;
        p = p->next;
    }

    return c;
}


extern "C" __declspec(dllexport) ULL getValueByPos(int pos)
{
    int i = 0;

    Node* p = head;

    while (p)
    {
        if (i == pos)
            return p->value;

        i++;
        p = p->next;
    }

    return 0;
}


extern "C" __declspec(dllexport) int getIndexByPos(int pos)
{
    int i = 0;

    Node* p = head;

    while (p)
    {
        if (i == pos)
            return p->index;

        i++;
        p = p->next;
    }

    return -1;
}

Node* getNodeByPosition(int pos)
{
    int i = 0;

    Node* p = head;

    while (p)
    {
        if (i == pos)
            return p;

        i++;
        p = p->next;
    }

    return NULL;
}

void shiftRightFrom(int startIndex)
{
    Node* p = tail;

    while (p)
    {
        if (p->index >= startIndex)
            p->index++;

        p = p->prev;
    }
}

extern "C" __declspec(dllexport) void extraFunction(int op, int place)
{
    if (!head)
        return;

    ULL result = (op == 1) ? 0ULL : 1ULL;

    Node* p = head;

    while (p)
    {
        if (op == 1)
            result += p->value;
        else
            result *= p->value;

        p = p->next;
    }

    int idx;

    if (place == 1)
    {
        idx = head->index;
        shiftRightFrom(idx);
    }
    else if (place == 3)
    {
        idx = tail->index + 1;
    }
    else
    {
        int middle = getCount() / 2;

        Node* mid = getNodeByPosition(middle);

        idx = mid->index;

        shiftRightFrom(idx);
    }

    insertNode(idx, result);
}
