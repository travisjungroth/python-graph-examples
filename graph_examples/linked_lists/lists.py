from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Optional

from graph_examples.linked_lists.base_lists import (
    BaseCircularLinkedList,
    BaseLinearLinkedList,
    BaseDoublyLinkedList,
    BaseSinglyLinkedList,
)
from graph_examples.linked_lists.nodes import LinkedNode, DoublyLinkedNode, CircularLinkedNode, CircularDoublyLinkedNode
from graph_examples.linked_lists.base_nodes import T


class LinkedList(BaseLinearLinkedList[T], BaseSinglyLinkedList[T]):
    def __init__(self, values: Iterable[T] = ()) -> None:
        values_iter = iter(values)
        try:
            self.head = LinkedNode(next(values_iter))
        except StopIteration:
            self.head = None
        node = self.head
        for value in values_iter:
            node.next = LinkedNode(value)
            node = node.next

    def appendleft(self, value: T) -> None:
        self.head = LinkedNode(value, self.head)

    def popleft(self) -> T:
        if not self:
            raise IndexError
        node = self.head
        self.head = node.next
        return node.value

    def reverse(self) -> None:
        node = self.head
        last_node = None
        while node is not None:
            node.next, last_node, node = last_node, node, node.next
        self.head = last_node


class DoublyLinkedList(BaseLinearLinkedList[T], BaseDoublyLinkedList[T]):
    def __init__(self, values: Iterable = ()) -> None:
        values_iter = iter(values)
        try:
            self.head = DoublyLinkedNode(next(values_iter))
        except StopIteration:
            self.head = None
        node = self.head
        for value in values_iter:
            node.next = DoublyLinkedNode(value, None, node)
            node = node.next
        self.tail = node

    def __reversed__(self) -> Iterator[T]:
        node = self.tail
        while node is not None:
            yield node.value
            node = node.last

    def append(self, value: T):
        old_tail = self.tail
        self.tail = DoublyLinkedNode(value, None, old_tail)
        if old_tail is None:
            self.head = self.tail
        else:
            old_tail.next = self.tail

    def appendleft(self, value: T):
        old_head = self.head
        self.head = DoublyLinkedNode(value, old_head)
        if old_head is None:
            self.tail = self.head
        else:
            old_head.last = self.head

    def pop(self) -> T:
        if not self:
            raise IndexError
        old_tail = self.tail
        self.tail = old_tail.last
        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        return old_tail.value

    def popleft(self) -> T:
        if not self:
            raise IndexError
        old_head = self.head
        self.head = old_head.next
        if self.head is None:
            self.tail = None
        else:
            self.head.last = None
        return old_head.value

    def reverse(self) -> None:
        node = self.head
        self.head, self.tail = self.tail, self.head
        while node is not None:
            node.next, node.last, node = node.last, node.next, node.next


class CircularLinkedList(BaseCircularLinkedList[T], BaseSinglyLinkedList[T]):
    def __init__(self, values: Iterable[T] = ()):
        values_iter = iter(values)
        try:
            head = CircularLinkedNode(next(values_iter))
        except StopIteration:
            head = None
        node = head
        for value in values_iter:
            node.next = CircularLinkedNode(value, head)
            node = node.next
        self.tail = node

    @property
    def head(self) -> CircularLinkedNode[T]:
        return self.tail.next

    @head.setter
    def head(self, node: CircularLinkedNode[T]):
        self.tail.next = node

    def appendleft(self, value: T) -> None:
        if not self:
            self.tail = CircularLinkedNode(value)
        else:
            self.head = CircularLinkedNode(value, self.head)

    def reverse(self) -> None:
        if not self:
            return
        node = self.head
        last_node = self.tail
        while node is not self.tail:
            node.next, last_node, node = last_node, node, node.next
        self.tail.next, self.tail = last_node, self.head


class CircularDoublyLinkedList(BaseCircularLinkedList[T], BaseDoublyLinkedList[T]):
    tail: Optional[CircularDoublyLinkedNode[T]]
    head: Optional[CircularDoublyLinkedNode[T]]

    def __init__(self, values: Iterable[T] = ()) -> None:
        values_iter = iter(values)
        try:
            head = CircularDoublyLinkedNode(next(values_iter))
        except StopIteration:
            head = None
        node = head
        for value in values_iter:
            node.next = CircularDoublyLinkedNode(value, head, node)
            node = node.next
            head.last = node
        self.tail = node

    @property
    def head(self) -> CircularDoublyLinkedNode[T]:
        return self.tail.next

    def __reversed__(self) -> Iterator[T]:
        if not self:
            return
        yield self.tail.value
        node = self.tail.last
        while node is not self.tail:
            yield node.value
            node = node.last

    def append(self, value: T) -> None:
        if not self:
            self.tail = CircularDoublyLinkedNode(value)
        else:
            self.tail = CircularDoublyLinkedNode(value, self.head, self.tail)
            self.tail.last.next = self.tail
            self.head.last = self.tail

    def appendleft(self, value: T) -> None:
        if not self:
            self.tail = CircularDoublyLinkedNode(value)
        else:
            self.tail.next = CircularDoublyLinkedNode(value, self.head, self.tail)
            self.head.next.last = self.tail.next

    def pop(self) -> T:
        if not self:
            raise IndexError
        value = self.tail.value
        if self.tail is self.head:
            self.tail = None
        else:
            self.tail.last.next, self.head.last, self.tail = self.head, self.tail.last, self.tail.last
        return value

    def popleft(self) -> T:
        if not self:
            raise IndexError
        value = self.head.value
        if self.tail is self.head:
            self.tail = None
        else:
            self.tail.next = self.tail.next.next
            self.tail.next.last = self.tail
        return value

    def reverse(self) -> None:
        if not self:
            return
        node = self.head
        while node is not self.tail:
            node.next, node.last, node = node.last, node.next, node.next
        self.tail.next, self.tail.last, self.tail = self.tail.last, self.tail.next, self.tail.next
