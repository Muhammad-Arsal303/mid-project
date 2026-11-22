"""
card.py - Card Representation for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Covers Requirements:
- FR-1.1: Represent a card with a suit, a rank, and a face-up/face-down state.
- FR-1.2: Derive a card's color (red or black) from its suit.
- FR-1.6: Display a card as a short label (e.g., 10H, QS, AD) or hidden marker ([##]).
"""

from enum import Enum
from typing import Optional


class Suit(Enum):
    """
    Standard card suits with unicode symbols and color classifications.
    Spades (S) & Clubs (C) -> Black
    Hearts (H) & Diamonds (D) -> Red
    """
    SPADES = ('S', '♠', 'black')
    HEARTS = ('H', '♥', 'red')
    DIAMONDS = ('D', '♦', 'red')
    CLUBS = ('C', '♣', 'black')

    def __init__(self, code: str, symbol: str, color: str):
        self.code = code
        self.symbol = symbol
        self._color = color

    @property
    def color(self) -> str:
        """Derives card color: red or black (FR-1.2)."""
        return self._color

    @classmethod
    def from_code(cls, code: str) -> Optional['Suit']:
        code_upper = code.upper()
        for s in cls:
            if s.code == code_upper or s.name == code_upper:
                return s
        return None


class Rank(Enum):
    """
    Standard card ranks from Ace (1) to King (13).
    """
    ACE = (1, 'A', 'Ace')
    TWO = (2, '2', '2')
    THREE = (3, '3', '3')
    FOUR = (4, '4', '4')
    FIVE = (5, '5', '5')
    SIX = (6, '6', '6')
    SEVEN = (7, '7', '7')
    EIGHT = (8, '8', '8')
    NINE = (9, '9', '9')
    TEN = (10, '10', '10')
    JACK = (11, 'J', 'Jack')
    QUEEN = (12, 'Q', 'Queen')
    KING = (13, 'K', 'King')

    def __init__(self, value: int, symbol: str, name_str: str):
        self._val = value
        self.symbol = symbol
        self.name_str = name_str

    @property
    def value(self) -> int:
        return self._val

    @classmethod
    def from_value(cls, val: int) -> Optional['Rank']:
        for r in cls:
            if r.value == val:
                return r
        return None

    @classmethod
    def from_symbol(cls, sym: str) -> Optional['Rank']:
        sym_upper = sym.upper()
        for r in cls:
            if r.symbol == sym_upper:
                return r
        return None


class Card:
    """
    Card Class (FR-1.1, FR-1.2, FR-1.6)
    Represents a playing card with suit, rank, and face-up state.
    """
    __slots__ = ('_suit', '_rank', '_face_up', '_id')

    def __init__(self, suit: Suit, rank: Rank, face_up: bool = False):
        self._suit = suit
        self._rank = rank
        self._face_up = face_up
        # Unique identifier 0..51 for hash map tracking (DS-5, DS-9)
        suit_order = {Suit.SPADES: 0, Suit.HEARTS: 1, Suit.DIAMONDS: 2, Suit.CLUBS: 3}
        self._id = suit_order[suit] * 13 + (rank.value - 1)

    @property
    def suit(self) -> Suit:
        return self._suit

    @property
    def rank(self) -> Rank:
        return self._rank

    @property
    def face_up(self) -> bool:
        return self._face_up

    @face_up.setter
    def face_up(self, val: bool) -> None:
        self._face_up = bool(val)

    @property
    def color(self) -> str:
        """Derive card color: 'red' or 'black' (FR-1.2)."""
        return self._suit.color

    @property
    def id(self) -> int:
        """Unique integer id [0..51] used as key in HashMap (DS-9)."""
        return self._id

    @property
    def code(self) -> str:
        """Short label, e.g. '10H', 'QS', 'AD' (FR-1.6)."""
        return f"{self._rank.symbol}{self._suit.code}"

    def flip(self) -> None:
        """Toggles face-up state."""
        self._face_up = not self._face_up

    def __str__(self) -> str:
        """Display label or hidden marker [##] (FR-1.6, UI-2)."""
        if self._face_up:
            return f"{self._rank.symbol}{self._suit.code}"
        return "[##]"

    def __repr__(self) -> str:
        state = "UP" if self._face_up else "DN"
        return f"Card({self.code}, {state})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return self._suit == other._suit and self._rank == other._rank

    def __hash__(self) -> int:
        return hash(self._id)

    def to_dict(self) -> dict:
        """Serializes card state for API / UI consumption."""
        return {
            'id': self._id,
            'suit': self._suit.code,
            'symbol': self._suit.symbol,
            'rank': self._rank.value,
            'rankSymbol': self._rank.symbol,
            'color': self.color,
            'faceUp': self._face_up,
            'code': self.code,
            'label': str(self)
        }
