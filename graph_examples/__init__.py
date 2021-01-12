from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Optional, Reversible, Collection


class AbstractLinkedNode(ABC, Collection):
    value: object

    def __repr__(self) -> str:
        self.next: Optional[AbstractLinkedNode]
        return f'{self.__class__.__name__}(value={repr(self.value)}, ' \
               f'next={repr(self.next.value) if self.next is not None else "END"})'

    @classmethod
    @abstractmethod
    def from_iterable(cls, values: Iterable) -> Optional[AbstractLinkedNode]:
        pass

    @abstractmethod
    def appendleft(self, value) -> AbstractLinkedNode:
        pass

    @abstractmethod
    def popleft(self) -> tuple[AbstractLinkedNode, object]:
        pass

    @abstractmethod
    def reverse(self):
        pass


class NonCircularLinkedNode(AbstractLinkedNode, ABC):
    def __init__(self, value, next_: Optional[LinkedNode] = None):
        self.value = value
        self.next = next_

    def __len__(self) -> int:
        if self.next is None:
            return 1
        return 1 + len(self.next)

    def __iter__(self) -> Iterator:
        yield self.value
        if self.next is not None:
            yield from self.next

    def __contains__(self, value) -> bool:
        if value == self.value:
            return True
        return self.next is not None and value in self.next


class LinkedNode(NonCircularLinkedNode):
    next: Optional[LinkedNode]

    @classmethod
    def from_iterable(cls, values: Iterable) -> Optional[LinkedNode]:
        values_iter = iter(values)
        try:
            node = cls(next(values_iter))
        except StopIteration:
            return None
        node.next = cls.from_iterable(values_iter)
        return node

    def appendleft(self, value) -> LinkedNode:
        return LinkedNode(value, self)

    def popleft(self) -> tuple[LinkedNode, object]:
        return self.next, self.value

    def reverse(self, last_node: Optional[LinkedNode] = None):
        next_node = self.next
        self.next = last_node
        if next_node is None:
            return self
        return next_node.reverse(self)


class AbstractDoublyLinkedNode(AbstractLinkedNode, ABC, Reversible):
    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def append(self, value):
        pass


class DoublyLinkedNode(NonCircularLinkedNode, AbstractDoublyLinkedNode):
    def __init__(self, value, next_: Optional[DoublyLinkedNode] = None, last: Optional[DoublyLinkedNode] = None):
        super().__init__(value, next_)
        self.last = last

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value={repr(self.value)}, ' \
               f'next={repr(self.next.value) if self.next is not None else "END"}, ' \
               f'last={repr(self.last.value) if self.last is not None else "END"})'

    @classmethod
    def from_iterable(cls, values: Iterable, last: Optional[DoublyLinkedNode] = None) -> Optional[DoublyLinkedNode]:
        values_iter = iter(values)
        try:
            node = cls(next(values_iter), None, last)
        except StopIteration:
            return None
        node.next = cls.from_iterable(values_iter, node)
        return node

    @property
    def tail(self) -> DoublyLinkedNode:
        node = self
        while node.next is not None:
            node = node.next
        return node

    def __reversed__(self) -> Iterator:
        yield self.value
        if self.last is not None:
            yield from reversed(self.last)

    def append(self, value) -> DoublyLinkedNode:
        self.next = DoublyLinkedNode(value, None, self)
        return self.next

    def appendleft(self, value) -> DoublyLinkedNode:
        self.last = DoublyLinkedNode(value, self)
        return self.last

    def pop(self) -> tuple[DoublyLinkedNode, object]:
        if self.last is not None:
            self.last.next = None
        return self.last, self.value

    def popleft(self) -> tuple[DoublyLinkedNode, object]:
        if self.next is not None:
            self.next.last = None
        return self.next, self.value

    def reverse(self):
        self.next, self.last = self.last, self.next
        if self.last is None:
            return self
        return self.last.reverse()


class AbstractCircularLinkedNode(AbstractLinkedNode, ABC):
    def __init__(self, value, next_: Optional[CircularLinkedNode] = None):
        self.value = value
        self.next = next_ if next_ is not None else self

    def __len__(self, tail: Optional[CircularLinkedNode] = None) -> int:
        if self is tail:
            return 0
        return 1 + self.next.__len__(self if tail is None else tail)

    def __iter__(self, tail: Optional[CircularLinkedNode] = None) -> Iterator:
        if self is tail:
            return
        yield self.next.value
        yield from self.next.__iter__(self if tail is None else tail)

    def __contains__(self, value, tail: Optional[CircularLinkedNode] = None) -> bool:
        if self is tail:
            return False
        return value == self.value or self.next.__contains__(value, self if tail is None else tail)


class CircularLinkedNode(AbstractCircularLinkedNode):
    @classmethod
    def from_iterable(cls, values: Iterable, head=None, last_node=None) -> Optional[CircularLinkedNode]:
        values_iter = iter(values)
        try:
            node = cls(next(values_iter), head)
            if last_node is not None:
                last_node.next = node
            return cls.from_iterable(values_iter, node if head is None else head, node)
        except StopIteration:
            return last_node

    def appendleft(self, value) -> CircularLinkedNode:
        self.next = CircularLinkedNode(value, self.next)
        return self

    def popleft(self) -> tuple[CircularLinkedNode, object]:
        value = self.next.value
        if self is self.next:
            return None, value
        else:
            self.next = self.next.next
            return self, value

    def reverse(self, last_node: Optional[CircularLinkedNode] = None, tail: Optional[CircularLinkedNode] = None):
        next_node = self.next
        self.next = last_node
        if next_node is None:
            return tail
        return next_node.reverse(self, next_node if tail is None else tail)


class CircularDoublyLinkedNode(AbstractCircularLinkedNode, AbstractDoublyLinkedNode):
    def __init__(
            self,
            value,
            next_: Optional[CircularDoublyLinkedNode] = None,
            last: Optional[CircularDoublyLinkedNode] = None
    ):
        super().__init__(value, next_)
        self.last = last if last is not None else self

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value={repr(self.value)}, ' \
               f'next={repr(self.next.value) if self.next is not None else "END"}, ' \
               f'last={repr(self.last.value) if self.last is not None else "END"})'

    @classmethod
    def from_iterable(cls, values: Iterable, head=None, last_node=None) -> Optional[CircularDoublyLinkedNode]:
        values_iter = iter(values)
        try:
            node = cls(next(values_iter), head, last_node)
            if last_node is not None:
                last_node.next = node
                head.last = node
            return cls.from_iterable(values_iter, node if head is None else head, node)
        except StopIteration:
            return last_node

    def __reversed__(self, tail: Optional[CircularDoublyLinkedNode] = None) -> Iterator:
        if self is tail:
            return
        yield self.value
        yield from self.last.__reversed__(self if tail is None else tail)

    def append(self, value) -> CircularDoublyLinkedNode:
        self.next = CircularDoublyLinkedNode(value, self.next, self)
        self.next.next.last = self.next
        return self.next

    def appendleft(self, value) -> CircularDoublyLinkedNode:
        self.next = CircularDoublyLinkedNode(value, self.next, self)
        self.next.next.last = self.next
        return self

    def pop(self) -> tuple[CircularDoublyLinkedNode, object]:
        value = self.value
        if self is self.next:
            return None, value
        else:
            self.last.next = self.next
            self.next.last = self.last
            return self.last, value

    def popleft(self) -> tuple[CircularDoublyLinkedNode, object]:
        value = self.next.value
        if self is self.next:
            return None, value
        else:
            self.next = self.next.next
            self.next.last = self
            return self, value

    def reverse(self, head: Optional[CircularDoublyLinkedNode] = None):
        if self is head:
            return self.last
        self.next, self.last = self.last, self.next
        return self.last.reverse(self if head is None else head)


class AbstractLinkedList(ABC, Collection):
    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(self, values: Iterable = ()):
        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr([x for x in self])})'

    @abstractmethod
    def appendleft(self, value):
        pass

    @abstractmethod
    def popleft(self):
        pass

    @abstractmethod
    def reverse(self):
        pass


class AbstractDoublyLinkedList(AbstractLinkedList, ABC, Reversible):
    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def append(self, value):
        pass


class NonCircularLinkedList(AbstractLinkedList, ABC):
    head: Optional[NonCircularLinkedNode]

    def __bool__(self):
        return self.head is not None

    def __len__(self) -> int:
        length = 0
        node = self.head
        while node is not None:
            node = node.next
            length += 1
        return length

    def __iter__(self) -> Iterator:
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __contains__(self, value) -> bool:
        node = self.head
        while node is not None:
            if node.value == value:
                return True
            node = node.next
        return False


class LinkedList(NonCircularLinkedList):
    def __init__(self, values: Iterable = ()):
        values_iter = iter(values)
        try:
            self.head = LinkedNode(next(values_iter))
        except StopIteration:
            self.head = None
        node = self.head
        for value in values_iter:
            node.next = LinkedNode(value)
            node = node.next

    def appendleft(self, value):
        self.head = LinkedNode(value, self.head)

    def popleft(self):
        if not self:
            raise IndexError
        node = self.head
        self.head = node.next
        return node.value

    def reverse(self):
        node = self.head
        last_node = None
        while node is not None:
            node.next, last_node, node = last_node, node, node.next
        self.head = last_node


class DoublyLinkedList(NonCircularLinkedList, AbstractDoublyLinkedList):
    def __init__(self, values: Iterable = ()):
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

    def __reversed__(self) -> Iterator:
        node = self.tail
        while node is not None:
            yield node.value
            node = node.last

    def append(self, value):
        old_tail = self.tail
        self.tail = DoublyLinkedNode(value, None, old_tail)
        if old_tail is None:
            self.head = self.tail
        else:
            old_tail.next = self.tail

    def appendleft(self, value):
        old_head = self.head
        self.head = DoublyLinkedNode(value, old_head)
        if old_head is None:
            self.tail = self.head
        else:
            old_head.last = self.head

    def pop(self):
        if not self:
            raise IndexError
        old_tail = self.tail
        self.tail = old_tail.last
        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        return old_tail.value

    def popleft(self):
        if not self:
            raise IndexError
        old_head = self.head
        self.head = old_head.next
        if self.head is None:
            self.tail = None
        else:
            self.head.last = None
        return old_head.value

    def reverse(self):
        node = self.head
        self.head, self.tail = self.tail, self.head
        while node is not None:
            node.next, node.last, node = node.last, node.next, node.next


class AbstractCircularLinkedList(AbstractLinkedList, ABC):
    tail: Optional[AbstractCircularLinkedNode]
    head: Optional[AbstractCircularLinkedNode]

    def __bool__(self):
        return self.tail is not None

    def __len__(self) -> int:
        if not self:
            return 0
        length = 1
        node = self.head
        while node is not self.tail:
            length += 1
            node = node.next
        return length

    def __iter__(self) -> Iterator:
        if not self:
            return
        head = self.head
        yield head.value
        node = head.next
        while node is not head:
            yield node.value
            node = node.next

    def infinite_iterator(self):
        if not self:
            return
        node = self.head
        while True:
            yield node.value
            node = node.next

    def __contains__(self, value: object) -> bool:
        if not self:
            return False
        node = self.head
        while node is not self.tail:
            if node.value == value:
                return True
            node = node.next
        return self.tail.value == value

    def popleft(self):
        if not self:
            raise IndexError
        value = self.head.value
        if self.tail is self.head:
            self.tail = None
        else:
            self.head = self.head.next
        return value


class CircularLinkedList(AbstractCircularLinkedList):
    def __init__(self, values: Iterable = ()):
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
    def head(self) -> CircularLinkedNode:
        return self.tail.next

    @head.setter
    def head(self, node: CircularLinkedNode):
        self.tail.next = node

    def appendleft(self, value):
        if not self:
            self.tail = CircularLinkedNode(value)
        else:
            self.head = CircularLinkedNode(value, self.head)

    def reverse(self):
        if not self:
            return
        node = self.head
        last_node = self.tail
        while node is not self.tail:
            node.next, last_node, node = last_node, node, node.next
        self.tail.next, self.tail = last_node, self.head


class CircularDoublyLinkedList(AbstractCircularLinkedList, AbstractDoublyLinkedList):
    tail: Optional[CircularDoublyLinkedNode]
    head: Optional[CircularDoublyLinkedNode]

    def __init__(self, values: Iterable = ()):
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
    def head(self) -> CircularDoublyLinkedNode:
        return self.tail.next

    def __reversed__(self) -> Iterator:
        if not self:
            return
        yield self.tail.value
        node = self.tail.last
        while node is not self.tail:
            yield node.value
            node = node.last

    def append(self, value):
        if not self:
            self.tail = CircularDoublyLinkedNode(value)
        else:
            self.tail = CircularDoublyLinkedNode(value, self.head, self.tail)
            self.tail.last.next = self.tail
            self.head.last = self.tail

    def appendleft(self, value):
        if not self:
            self.tail = CircularDoublyLinkedNode(value)
        else:
            self.tail.next = CircularDoublyLinkedNode(value, self.head, self.tail)
            self.head.next.last = self.tail.next

    def pop(self):
        if not self:
            raise IndexError
        value = self.tail.value
        if self.tail is self.head:
            self.tail = None
        else:
            self.tail.last.next, self.head.last, self.tail = self.head, self.tail.last, self.tail.last
        return value

    def popleft(self):
        if not self:
            raise IndexError
        value = self.head.value
        if self.tail is self.head:
            self.tail = None
        else:
            self.tail.next = self.tail.next.next
            self.tail.next.last = self.tail
        return value

    def reverse(self):
        if not self:
            return
        node = self.head
        while node is not self.tail:
            node.next, node.last, node = node.last, node.next, node.next
        self.tail.next, self.tail.last, self.tail = self.tail.last, self.tail.next, self.tail.next
