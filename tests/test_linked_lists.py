from abc import ABC
from itertools import islice
from typing import TypeVar

from pytest import mark, fixture, raises

from graph_examples.linked_lists import (
    BaseCircularLinkedList,
    BaseDoublyLinkedList,
    BaseLinkedList,
    BaseLinkedNode,
    CircularDoublyLinkedNode,
    DoublyLinkedNode,
)

# pytestmark = mark.timeout(.1)

T = TypeVar('T', bound=type)


def concrete_subclasses(cls: T, *except_: T) -> list[T]:
    except_ = set(except_)
    seen = {cls}
    queue = [cls]
    concrete = []
    while queue:
        subclasses = set(queue.pop(0).__subclasses__())
        to_see = sorted(subclasses - seen - except_, key=lambda x: x.__name__)  # sort to be deterministic
        for cls in to_see:
            seen.add(cls)
            queue.append(cls)
            if ABC not in cls.__bases__:
                concrete.append(cls)
    return concrete


@fixture(params=['a', 'ab', 'abc'])
def letters(request) -> str:
    return request.param


@fixture(params=['', 'a', 'ab', 'abc'])
def letters_and_empty(request) -> str:
    return request.param


@mark.parametrize('cls', concrete_subclasses(BaseLinkedNode))
class TestAbstractLinkedNode:
    def test_len(self, cls, letters):
        node = cls.from_iterable(letters)
        assert len(node) == len(letters)

    def test_iter(self, cls, letters):
        node = cls.from_iterable(letters)
        assert list(node) == list(letters)

    def test_contains(self, cls, letters):
        node = cls.from_iterable(letters)
        for letter in letters:
            assert letter in node
        assert object() not in node

    def test_appendleft(self, cls, letters):
        node = cls.from_iterable(letters)
        node = node.appendleft('x')
        assert list(node) == list('x' + letters)
        try:
            tail = node.tail
        except AttributeError:
            pass
        else:
            assert list(reversed(tail)) == list(reversed('x' + letters))

    def test_popleft(self, cls, letters):
        node = cls.from_iterable(letters)
        values = []
        while node:
            assert list(node) == list(letters[-len(node):])
            try:
                tail = node.tail
            except AttributeError:
                pass
            else:
                assert list(reversed(tail)) == list(letters[:-len(node) - 1:-1])
            node, value = node.popleft()
            values.append(value)
        assert node is None
        assert values == list(letters)

    def test_reverse(self, cls, letters):
        node = cls.from_iterable(letters)
        node = node.reverse()
        assert list(node) == list(reversed(letters))


class TestCircularDoublyLinkedNode:
    def test_reversed(self, letters):
        node = CircularDoublyLinkedNode.from_iterable(letters)
        assert list(reversed(node)) == list(reversed(letters))

    def test_pop(self, letters):
        node = CircularDoublyLinkedNode.from_iterable(letters)
        values = []
        while node:
            assert list(node) == list(letters[:len(node)])
            assert list(reversed(node)) == list(letters[len(node) - 1::-1])
            node, value = node.pop()
            values.append(value)
        assert values == list(reversed(letters))

    def test_append(self, letters):
        node = CircularDoublyLinkedNode.from_iterable(letters)
        node = node.append('x')
        assert list(node) == list(letters + 'x')
        assert list(reversed(node)) == list(reversed(letters + 'x'))


class TestDoublyLinkedNode:
    def test_reversed(self, letters):
        head = DoublyLinkedNode.from_iterable(letters)
        tail = head.tail
        assert list(reversed(tail)) == list(reversed(letters))

    def test_pop(self, letters):
        head = DoublyLinkedNode.from_iterable(letters)
        tail = head.tail
        values = []
        while tail:
            assert list(reversed(tail)) == list(letters[len(head) - 1::-1])
            assert list(head) == list(letters[:len(head)])
            tail, value = tail.pop()
            values.append(value)
        assert values == list(reversed(letters))

    def test_append(self, letters):
        head = DoublyLinkedNode.from_iterable(letters)
        tail = head.tail.append('x')
        assert list(head) == list(letters + 'x')
        assert list(reversed(tail)) == list(reversed(letters + 'x'))


@mark.parametrize('cls', concrete_subclasses(BaseLinkedList))
class TestAbstractLinkedList:
    def test_len(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        assert len(li) == len(letters_and_empty)

    def test_iter(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        assert list(li) == list(letters_and_empty)

    def test_contains(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        for letter in letters_and_empty:
            assert letter in li
        assert object() not in li

    def test_bool(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        assert bool(li) == bool(letters_and_empty)

    def test_appendleft(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        li.appendleft('x')
        assert list(li) == list('x' + letters_and_empty)
        try:
            reversed_li = reversed(li)
        except TypeError:
            pass
        else:
            assert list(reversed_li) == list(reversed('x' + letters_and_empty))

    def test_popleft(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        values = []
        while li:
            assert list(li) == list(letters_and_empty[-len(li):])
            try:
                reversed_li = reversed(li)
            except TypeError:
                pass
            else:
                assert list(reversed_li) == list(letters_and_empty[:-len(li) - 1:-1])
            value = li.popleft()
            values.append(value)
        assert not li
        assert values == list(letters_and_empty)

    def test_popleft_empty(self, cls):
        li = cls()
        with raises(IndexError):
            li.popleft()

    def test_reverse(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        li.reverse()
        assert list(li) == list(reversed(letters_and_empty))


@mark.parametrize('cls', concrete_subclasses(BaseDoublyLinkedList))
class TestAbstractDoublyLinkedList:
    def test_reversed(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        assert list(reversed(li)) == list(reversed(letters_and_empty))

    def test_pop(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        values = []
        while li:
            assert list(li) == list(letters_and_empty[:len(li)])
            assert list(reversed(li)) == list(letters_and_empty[len(li) - 1::-1])
            value = li.pop()
            values.append(value)
        assert not li
        assert values == list(reversed(letters_and_empty))

    def test_pop_empty(self, cls):
        li = cls()
        with raises(IndexError):
            li.pop()

    def test_append(self, cls, letters_and_empty):
        li = cls(letters_and_empty)
        li.append('x')
        assert list(li) == list(letters_and_empty + 'x')
        assert list(reversed(li)) == list(reversed(letters_and_empty + 'x'))


@mark.parametrize('cls', concrete_subclasses(BaseCircularLinkedList))
class TestAbstractCircularLinkedList:
    def test_infinite_iterator(self, cls, letters):
        li = cls(letters)
        assert list(islice(li.infinite_iterator(), len(letters) * 3)) == list(letters * 3)

    def test_infinite_iterator_empty(self, cls):
        li = cls()
        assert not list(li.infinite_iterator())
