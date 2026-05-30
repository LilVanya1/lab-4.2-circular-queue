class Node:

    def __init__(self, index, value):

        self.index = index
        self.value = value
        self.prev = None
        self.next = None


head = None
tail = None


def create_list():

    global head, tail

    head = None
    tail = None


def clear_list():

    global head, tail

    head = None
    tail = None


def insert_node(index, value):

    global head, tail

    new = Node(index, value)

    if head is None:

        head = tail = new
        return

    p = head

    while p and p.index < index:
        p = p.next

    if p is None:

        tail.next = new
        new.prev = tail
        tail = new

    else:

        new.next = p
        new.prev = p.prev

        if p.prev:
            p.prev.next = new
        else:
            head = new

        p.prev = new


def find_node(index):

    p = head

    while p:

        if p.index == index:
            return p

        p = p.next

    return None


def read_node(index):

    n = find_node(index)

    return n.value if n else 0


def delete_node(index):

    global head, tail

    p = find_node(index)

    if not p:
        return

    if p.prev:
        p.prev.next = p.next
    else:
        head = p.next

    if p.next:
        p.next.prev = p.prev
    else:
        tail = p.prev


def get_count():

    c = 0
    p = head

    while p:

        c += 1
        p = p.next

    return c


def get_index(pos):

    i = 0
    p = head

    while p:

        if i == pos:
            return p.index

        i += 1
        p = p.next

    return -1


def get_value(pos):

    i = 0
    p = head

    while p:

        if i == pos:
            return p.value

        i += 1
        p = p.next

    return 0


def shift_right_from(start_index):

    global tail

    p = tail

    while p:

        if p.index >= start_index:
            p.index += 1

        p = p.prev


def extra_function(op, place):

    global head, tail

    if head is None:
        return

    result = 0 if op == 1 else 1

    p = head

    while p:

        if op == 1:
            result += p.value
        else:
            result *= p.value

        p = p.next

    if place == 1:

        idx = head.index
        shift_right_from(idx)

    elif place == 3:

        idx = tail.index + 1

    else:

        middle_pos = get_count() // 2
        idx = get_index(middle_pos)

        shift_right_from(idx)

    insert_node(idx, result)
