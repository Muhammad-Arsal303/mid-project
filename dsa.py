"""
dsa.py - Core Custom Data Structures for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Covers Requirements:
- DS-1: Array / Deck (52 cards, Fisher-Yates shuffle with seed)
- DS-2: Stack (LIFO) for Foundations, Waste, Undo, Redo
- DS-3: Queue (FIFO) for Stock pile
- DS-4, DS-6: DoublyLinkedList for 7 Tableau piles (split_from, attach, peek_tail)
- DS-5, DS-9: HashMap with chaining for Card location & state tracking
- NFR-2: Push, pop, enqueue, dequeue are O(1); shuffle is O(n)
- DS-10: Data structure classes are self-contained and modular
"""

import random
from typing import Any, Optional, List, Callable, Iterator
from card import Card, Suit, Rank


# ==============================================================================
# DS-1: DECK & ARRAY
# ==============================================================================
class Deck:
    """
    DS-1: 52-card deck stored in a fixed-capacity contiguous array.
    Supports unbiased Fisher-Yates shuffle with deterministic seed support.
    """
    def __init__(self):
        self._cards: List[Card] = []
        self._reset()

    def _reset(self) -> None:
        """Populates exactly 52 unique standard playing cards (FR-1.3, TC-01)."""
        self._cards = []
        for suit in Suit:
            for rank in Rank:
                self._cards.append(Card(suit, rank, face_up=False))

    def shuffle(self, seed: Optional[int] = None) -> None:
        """
        Fisher-Yates O(n) unbiased shuffle algorithm (FR-1.4, FR-1.5, TC-02).
        If seed is provided, results are strictly reproducible.
        """
        rng = random.Random(seed) if seed is not None else random.Random()
        n = len(self._cards)
        for i in range(n - 1, 0, -1):
            j = rng.randint(0, i)
            self._cards[i], self._cards[j] = self._cards[j], self._cards[i]

    def deal(self) -> Optional[Card]:
        """Pops and returns the top card from the deck array."""
        if not self._cards:
            return None
        return self._cards.pop()

    def size(self) -> int:
        return len(self._cards)

    def is_empty(self) -> bool:
        return len(self._cards) == 0

    def get_cards(self) -> List[Card]:
        return list(self._cards)

    def __len__(self) -> int:
        return len(self._cards)


# ==============================================================================
# DS-2: STACK (LIFO)
# ==============================================================================
class StackNode:
    """Singly-linked node for Stack."""
    __slots__ = ('value', 'next')

    def __init__(self, value: Any, next_node: Optional['StackNode'] = None):
        self.value = value
        self.next = next_node


class Stack:
    """
    DS-2: Hand-written LIFO Stack implemented with linked nodes.
    Used for:
      - 4 Foundation piles (FR-5.1)
      - Waste pile (FR-3.4)
      - Undo stack (FR-7.1)
      - Redo stack (FR-7.3)
    Operations: push, pop, peek, size, is_empty - all strictly O(1) (NFR-2).
    """
    def __init__(self):
        self._top: Optional[StackNode] = None
        self._size: int = 0

    def push(self, item: Any) -> None:
        """Pushes an element onto the top of the stack. O(1)"""
        new_node = StackNode(item, self._top)
        self._top = new_node
        self._size += 1

    def pop(self) -> Any:
        """Pops and returns the top element. Returns None if empty. O(1)"""
        if self._top is None:
            return None
        popped = self._top.value
        self._top = self._top.next
        self._size -= 1
        return popped

    def peek(self) -> Any:
        """Returns top element without removing it. Returns None if empty. O(1)"""
        if self._top is None:
            return None
        return self._top.value

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        self._top = None
        self._size = 0

    def to_list(self) -> List[Any]:
        """Returns items ordered from bottom to top (for rendering / inspection)."""
        result = []
        curr = self._top
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        result.reverse()  # now bottom -> top
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        return iter(self.to_list())

    def __repr__(self) -> str:
        items = self.to_list()
        return f"Stack({items})"


# ==============================================================================
# DS-3: QUEUE (FIFO)
# ==============================================================================
class QueueNode:
    """Singly-linked node for Queue."""
    __slots__ = ('value', 'next')

    def __init__(self, value: Any, next_node: Optional['QueueNode'] = None):
        self.value = value
        self.next = next_node


class Queue:
    """
    DS-3: Hand-written FIFO Queue with head and tail pointers.
    Used for:
      - Stock draw pile (FR-3.1, DS-3)
    Operations: enqueue, dequeue, peek, size, is_empty - all strictly O(1) (NFR-2).
    """
    def __init__(self):
        self._head: Optional[QueueNode] = None
        self._tail: Optional[QueueNode] = None
        self._size: int = 0

    def enqueue(self, item: Any) -> None:
        """Appends item to the rear of the queue. O(1)"""
        new_node = QueueNode(item, None)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def enqueue_front(self, item: Any) -> None:
        """Pushes item to the front of the queue (used for undoing stock draw). O(1)"""
        new_node = QueueNode(item, self._head)
        self._head = new_node
        if self._tail is None:
            self._tail = new_node
        self._size += 1

    def dequeue(self) -> Any:
        """Removes and returns item from front of queue. O(1)"""
        if self._head is None:
            return None
        dequeued = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return dequeued

    def peek(self) -> Any:
        """Returns front item without removing it. O(1)"""
        if self._head is None:
            return None
        return self._head.value

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        self._head = None
        self._tail = None
        self._size = 0

    def to_list(self) -> List[Any]:
        """Returns items in FIFO order (front to back)."""
        result = []
        curr = self._head
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        return iter(self.to_list())

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"


# ==============================================================================
# DS-4, DS-6: DOUBLY LINKED LIST (TABLEAU)
# ==============================================================================
class ListNode:
    """Doubly-linked node for Tableau LinkedList."""
    __slots__ = ('value', 'prev', 'next')

    def __init__(self, value: Card, prev_node: Optional['ListNode'] = None, next_node: Optional['ListNode'] = None):
        self.value: Card = value
        self.prev: Optional['ListNode'] = prev_node
        self.next: Optional['ListNode'] = next_node


class LinkedList:
    """
    DS-4 & DS-6: Hand-written Doubly Linked List for Tableau piles.
    Head = bottom-most card (base of column)
    Tail = top-most card (exposed card on top of pile)

    Key operations:
      - append(card): O(1) at tail
      - pop_tail(): O(1) from tail
      - peek_tail(): O(1) at tail
      - split_from(node): O(1) detaches subtree/run starting at node to tail
      - attach(run_head, run_tail, count): O(1) connects a detached run to this tail
      - size: O(1) cached counter
    """
    def __init__(self):
        self._head: Optional[ListNode] = None
        self._tail: Optional[ListNode] = None
        self._size: int = 0

    def append(self, card: Card) -> ListNode:
        """Appends a card at the top of the pile (tail). O(1)"""
        new_node = ListNode(card, prev_node=self._tail, next_node=None)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1
        return new_node

    def peek_tail(self) -> Optional[Card]:
        """Returns the top card (tail). O(1)"""
        if self._tail is None:
            return None
        return self._tail.value

    def peek_tail_node(self) -> Optional[ListNode]:
        """Returns the tail node."""
        return self._tail

    def pop_tail(self) -> Optional[Card]:
        """Removes and returns top card (tail). O(1)"""
        if self._tail is None:
            return None
        popped = self._tail.value
        if self._head == self._tail:
            self._head = None
            self._tail = None
        else:
            self._tail = self._tail.prev
            self._tail.next = None
        self._size -= 1
        return popped

    def find_node_by_card_id(self, card_id: int) -> Optional[ListNode]:
        """Searches for node holding card with given id. O(k)"""
        curr = self._head
        while curr is not None:
            if curr.value.id == card_id:
                return curr
            curr = curr.next
        return None

    def get_run_from_top(self, count: int) -> Optional[ListNode]:
        """
        Returns starting node of a run consisting of the top `count` cards.
        Walks backwards from tail by `count - 1` steps. O(k)
        """
        if count <= 0 or count > self._size:
            return None
        curr = self._tail
        for _ in range(count - 1):
            if curr is None:
                return None
            curr = curr.prev
        return curr

    def split_from(self, start_node: ListNode) -> 'LinkedList':
        """
        Detaches the segment from `start_node` through `tail` as a new LinkedList.
        Leaves this list ending at start_node.prev.
        O(1) pointer updates. (DS-4, FR-4.2)
        """
        detached = LinkedList()
        detached._head = start_node
        detached._tail = self._tail

        # Count nodes in the detached segment
        count = 0
        curr = start_node
        while curr is not None:
            count += 1
            curr = curr.next
        detached._size = count

        # Update this list
        if start_node.prev is not None:
            start_node.prev.next = None
            self._tail = start_node.prev
            start_node.prev = None
        else:
            self._head = None
            self._tail = None

        self._size -= count
        return detached

    def attach(self, run_list: 'LinkedList') -> None:
        """
        Attaches an entire detached LinkedList onto the tail of this list.
        O(1) pointer reconnection. (FR-4.6)
        """
        if run_list.is_empty():
            return
        if self.is_empty():
            self._head = run_list._head
            self._tail = run_list._tail
            self._size = run_list._size
        else:
            self._tail.next = run_list._head
            run_list._head.prev = self._tail
            self._tail = run_list._tail
            self._size += run_list._size

        # Invalidate attached list so it cannot be double-used
        run_list._head = None
        run_list._tail = None
        run_list._size = 0

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def to_list(self) -> List[Card]:
        """Returns cards from head (bottom) to tail (top)."""
        result = []
        curr = self._head
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Card]:
        return iter(self.to_list())

    def __repr__(self) -> str:
        return f"LinkedList({[str(c) for c in self.to_list()]})"


# ==============================================================================
# DS-5, DS-9: HASH MAP (CARD LOCATIONS & STATES)
# ==============================================================================
class HashEntry:
    """Key-value pair node with chaining for collision resolution."""
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key: int, value: Any, next_entry: Optional['HashEntry'] = None):
        self.key: int = key
        self.value: Any = value
        self.next: Optional['HashEntry'] = next_entry


class HashMap:
    """
    DS-5 & DS-9: Hand-written Hash Map using separate chaining.
    Key: unique card id (0..51)
    Value: LocationRecord (pile_type, pile_index, position, face_up)
    Average time complexity: O(1) for put, get, update, contains, remove.
    """
    DEFAULT_CAPACITY = 64  # Power of 2, exceeds 52 cards so load factor <= 0.81

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self._capacity: int = capacity
        self._buckets: List[Optional[HashEntry]] = [None] * self._capacity
        self._size: int = 0

    def _hash(self, key: int) -> int:
        """Computes bucket index for integer card id."""
        # Multiplicative hashing for uniform distribution
        return (key * 2654435761) % self._capacity

    def put(self, key: int, value: Any) -> None:
        """Inserts or updates key-value pair. O(1) avg"""
        idx = self._hash(key)
        curr = self._buckets[idx]
        while curr is not None:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Key not present; insert new node at head of chain
        new_entry = HashEntry(key, value, self._buckets[idx])
        self._buckets[idx] = new_entry
        self._size += 1

    def get(self, key: int) -> Any:
        """Retrieves value by key. Returns None if not found. O(1) avg"""
        idx = self._hash(key)
        curr = self._buckets[idx]
        while curr is not None:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return None

    def contains(self, key: int) -> bool:
        """Returns True if key is present."""
        return self.get(key) is not None

    def remove(self, key: int) -> bool:
        """Removes key from map. Returns True if removed, False otherwise."""
        idx = self._hash(key)
        curr = self._buckets[idx]
        prev = None
        while curr is not None:
            if curr.key == key:
                if prev is None:
                    self._buckets[idx] = curr.next
                else:
                    prev.next = curr.next
                self._size -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        self._buckets = [None] * self._capacity
        self._size = 0

    def to_dict(self) -> dict:
        """Exports all entries as standard python dict (for serialization / testing)."""
        res = {}
        for entry in self._buckets:
            curr = entry
            while curr is not None:
                res[curr.key] = curr.value
                curr = curr.next
        return res

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"HashMap(size={self._size}, entries={self.to_dict()})"
