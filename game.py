"""
game.py - Game Logic Engine for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Covers Requirements:
- FR-2.1 to 2.6: Initial deal (7 tableau piles, stock, waste, foundations, draw modes)
- FR-3.1 to 3.6: Stock draw, FIFO queue, waste recycling in original order
- FR-4.1 to 4.6: Tableau moves, alternating colors, King on empty, run moves
- FR-5.1 to 5.5: Foundation moves, Ace first, ascending suit, foundation to tableau
- FR-6.1 to 6.5: Move validation, error messages, automatic card flip, HashMap tracking
- FR-7.1 to 7.6: Complete Undo and Redo stacks
- FR-8.1 to 8.4: Win condition detection, auto-complete
- FR-10.1 to 10.6: Strategic hints, timer, and Solitaire scoring system with combos
"""

import time
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

from card import Card, Suit, Rank
from dsa import Deck, Stack, Queue, LinkedList, HashMap, ListNode


class MoveType(Enum):
    DRAW = 'DRAW'
    RECYCLE_WASTE = 'RECYCLE_WASTE'
    TABLEAU_TO_TABLEAU = 'TABLEAU_TO_TABLEAU'
    TABLEAU_TO_FOUNDATION = 'TABLEAU_TO_FOUNDATION'
    WASTE_TO_TABLEAU = 'WASTE_TO_TABLEAU'
    WASTE_TO_FOUNDATION = 'WASTE_TO_FOUNDATION'
    FOUNDATION_TO_TABLEAU = 'FOUNDATION_TO_TABLEAU'
    AUTO_COMPLETE = 'AUTO_COMPLETE'


class LocationRecord:
    """DS-5, DS-9: Card location and face state recorded in HashMap."""
    __slots__ = ('pile_type', 'pile_index', 'position', 'face_up')

    def __init__(self, pile_type: str, pile_index: int, position: int, face_up: bool):
        self.pile_type = pile_type    # 'STOCK', 'WASTE', 'TABLEAU', 'FOUNDATION'
        self.pile_index = pile_index  # 0..6 for tableau, 0..3 for foundation, 0 for stock/waste
        self.position = position      # 0-indexed position within pile
        self.face_up = face_up

    def to_dict(self) -> dict:
        return {
            'pileType': self.pile_type,
            'pileIndex': self.pile_index,
            'position': self.position,
            'faceUp': self.face_up
        }

    def __repr__(self) -> str:
        return f"Loc({self.pile_type}[{self.pile_index}], pos={self.position}, up={self.face_up})"


class Move:
    """
    DS-8: Memento record for every successful action placed onto the Undo/Redo Stacks.
    """
    def __init__(self, move_type: MoveType, source: str, dest: str, cards: List[Card],
                 flipped_card: Optional[Card] = None, drawn_count: int = 0,
                 recycled_cards: Optional[List[Card]] = None, score_delta: int = 0,
                 combo_delta: int = 0):
        self.move_type = move_type
        self.source = source
        self.dest = dest
        self.cards = cards                          # Cards that were relocated
        self.flipped_card = flipped_card            # Card flipped face-up by this move
        self.drawn_count = drawn_count              # Number of cards drawn from stock
        self.recycled_cards = recycled_cards or []  # Preserved cards during recycle
        self.score_delta = score_delta
        self.combo_delta = combo_delta

    def __repr__(self) -> str:
        return f"Move({self.move_type.value}, src={self.source}, dst={self.dest}, count={len(self.cards)})"


class KlondikeGame:
    """
    Core Game Logic Engine (FR-2 through FR-10)
    Maintains clean separation: UI calls this engine and renders returned state.
    Data structures:
      - stock: Queue (FIFO)
      - waste: Stack (LIFO)
      - foundations: List of 4 Stacks (one per suit: S, H, D, C)
      - tableau: List of 7 LinkedLists (head = bottom, tail = top)
      - location_map: HashMap (card id -> LocationRecord)
      - undo_stack: Stack (LIFO of Move objects)
      - redo_stack: Stack (LIFO of Move objects)
    """
    SUIT_ORDER = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]

    def __init__(self, draw_mode: int = 1, seed: Optional[int] = None):
        self.draw_mode: int = draw_mode  # 1 or 3 (FR-2.5)
        self.seed: Optional[int] = seed

        # Game structures
        self.stock: Queue = Queue()
        self.waste: Stack = Stack()
        self.foundations: List[Stack] = [Stack() for _ in range(4)]
        self.tableau: List[LinkedList] = [LinkedList() for _ in range(7)]

        # Tracking and history
        self.location_map: HashMap = HashMap()
        self.undo_stack: Stack = Stack()
        self.redo_stack: Stack = Stack()

        # Metrics and state
        self.score: int = 0
        self.move_count: int = 0
        self.combo: int = 0
        self.max_combo: int = 0
        self.start_time: float = time.time()
        self.is_won: bool = False
        self.last_message: str = "Welcome to Klondike Solitaire! Make your first move."
        self.last_move_legal: bool = True

        self.new_game(seed=seed, draw_mode=draw_mode)

    # --------------------------------------------------------------------------
    # GAME SETUP & INITIALIZATION
    # --------------------------------------------------------------------------
    def new_game(self, seed: Optional[int] = None, draw_mode: Optional[int] = None) -> None:
        """
        Initializes and deals a fresh game of Klondike Solitaire (FR-2.1 to FR-2.6).
        """
        if draw_mode is not None:
            self.draw_mode = draw_mode
        self.seed = seed

        # Reset all data structures
        self.stock.clear()
        self.waste.clear()
        for f in self.foundations:
            f.clear()
        for t in self.tableau:
            t._head = None
            t._tail = None
            t._size = 0
        self.location_map.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()

        self.score = 0
        self.move_count = 0
        self.combo = 0
        self.max_combo = 0
        self.is_won = False
        self.start_time = time.time()

        # Create 52-card deck and shuffle (DS-1, FR-1.3, FR-1.4, FR-1.5)
        deck = Deck()
        deck.shuffle(seed=self.seed)

        # Deal to 7 Tableau piles (FR-2.1, FR-2.2, TC-03)
        # Pile i (0..6) receives i + 1 cards; only the top card is face-up
        for col in range(7):
            num_cards = col + 1
            for pos in range(num_cards):
                card = deck.deal()
                if card is None:
                    break
                card.face_up = (pos == num_cards - 1)  # Only the last card is face-up
                self.tableau[col].append(card)

        # Remaining 24 cards go into Stock Queue face-down (FR-2.3, DS-3)
        while not deck.is_empty():
            card = deck.deal()
            if card:
                card.face_up = False
                self.stock.enqueue(card)

        # Sync location map (DS-5, DS-9, FR-6.5)
        self._update_location_map()
        self.last_message = f"New Game started (Draw-{self.draw_mode}). Good luck!"
        self.last_move_legal = True

    # --------------------------------------------------------------------------
    # STOCK & WASTE OPERATIONS (FR-3)
    # --------------------------------------------------------------------------
    def draw(self) -> Tuple[bool, str]:
        """
        Draws 1 or up to 3 cards from the stock into waste (FR-3.1 to FR-3.6, UC-02).
        If stock is empty, recycles waste back into stock in original order (DS-7).
        """
        if self.is_won:
            return False, "Game is already won!"

        # Case 1: Stock has cards
        if not self.stock.is_empty():
            draw_target = 1 if self.draw_mode == 1 else 3
            drawn_cards: List[Card] = []

            for _ in range(draw_target):
                if self.stock.is_empty():
                    break
                card: Card = self.stock.dequeue()
                card.face_up = True
                self.waste.push(card)
                drawn_cards.append(card)

            # Record undo action
            record = Move(
                move_type=MoveType.DRAW,
                source='STOCK',
                dest='WASTE',
                cards=drawn_cards,
                drawn_count=len(drawn_cards),
                combo_delta=-self.combo
            )
            self.undo_stack.push(record)
            self.redo_stack.clear()
            self.combo = 0
            self.move_count += 1
            self._update_location_map()

            msg = f"Drew {len(drawn_cards)} card(s) from Stock to Waste."
            self.last_message = msg
            self.last_move_legal = True
            return True, msg

        # Case 2: Stock empty, Waste non-empty -> Recycle waste
        elif not self.waste.is_empty():
            # DS-7: Waste is recycled into Stock in original draw order.
            # Using a temporary stack reverses the LIFO waste back into the original FIFO sequence.
            temp_stack = Stack()
            recycled_cards: List[Card] = []

            # Pop all from waste into temp stack
            while not self.waste.is_empty():
                c = self.waste.pop()
                c.face_up = False
                temp_stack.push(c)
                recycled_cards.append(c)

            # Push from temp stack into stock queue
            while not temp_stack.is_empty():
                self.stock.enqueue(temp_stack.pop())

            # Solitaire rule: recycling in Draw-1 incurs -100 pts penalty
            score_delta = -100 if self.draw_mode == 1 else 0
            self.score = max(0, self.score + score_delta)

            # Then perform the draw (FR-3.5, UC-02 step 3)
            draw_target = 1 if self.draw_mode == 1 else 3
            drawn_cards: List[Card] = []
            for _ in range(draw_target):
                if self.stock.is_empty():
                    break
                card: Card = self.stock.dequeue()
                card.face_up = True
                self.waste.push(card)
                drawn_cards.append(card)

            record = Move(
                move_type=MoveType.RECYCLE_WASTE,
                source='WASTE',
                dest='STOCK',
                cards=drawn_cards,
                recycled_cards=recycled_cards,
                score_delta=score_delta,
                combo_delta=-self.combo
            )
            self.undo_stack.push(record)
            self.redo_stack.clear()
            self.combo = 0
            self.move_count += 1
            self._update_location_map()

            msg = f"Recycled Waste into Stock and drew {len(drawn_cards)} card(s)."
            self.last_message = msg
            self.last_move_legal = True
            return True, msg
            self.last_message = msg
            self.last_move_legal = True
            return True, msg

        # Case 3: Both Stock and Waste are empty (FR-3.6)
        else:
            msg = "Stock and Waste are both empty. Nothing to draw."
            self.last_message = msg
            self.last_move_legal = False
            return False, msg

    # --------------------------------------------------------------------------
    # TABLEAU TO TABLEAU MOVES (FR-4, UC-03)
    # --------------------------------------------------------------------------
    def move_tableau_to_tableau(self, src_idx: int, dst_idx: int, count: int = 1) -> Tuple[bool, str]:
        """
        Moves `count` cards from Tableau `src_idx` to Tableau `dst_idx`.
        Validates descending rank, alternating color, and King on empty (FR-4.2 to FR-4.6).
        """
        if self.is_won:
            return False, "Game is already won!"

        # Bounds and validity check (FR-6.4)
        if src_idx < 0 or src_idx >= 7 or dst_idx < 0 or dst_idx >= 7:
            return self._reject("Invalid tableau pile index. Must be between 0 and 6 (T1-T7).")
        if src_idx == dst_idx:
            return self._reject("Source and destination tableau piles cannot be identical.")

        src_pile = self.tableau[src_idx]
        dst_pile = self.tableau[dst_idx]

        if src_pile.is_empty():
            return self._reject(f"Source pile T{src_idx+1} is empty.")
        if count <= 0 or count > src_pile.size():
            return self._reject(f"Cannot move {count} cards. Source pile has {src_pile.size()} card(s).")

        # Find starting node of the run (FR-4.1, DS-4)
        run_start_node = src_pile.get_run_from_top(count)
        if run_start_node is None:
            return self._reject("Failed to locate run in source pile.")

        # Check all cards in the run are face-up (FR-4.5, TC-10)
        curr = run_start_node
        run_cards: List[Card] = []
        while curr is not None:
            if not curr.value.face_up:
                return self._reject("Cannot move a run containing face-down cards.")
            run_cards.append(curr.value)
            curr = curr.next

        moving_base_card = run_cards[0]

        # Destination validation (FR-4.3, FR-4.4)
        if dst_pile.is_empty():
            if moving_base_card.rank != Rank.KING:
                return self._reject(f"Only a King can be moved to an empty tableau pile (tried {moving_base_card}).")
        else:
            dst_top = dst_pile.peek_tail()
            if dst_top is None:
                return self._reject("Destination pile top is unavailable.")
            # Must be one rank lower and opposite color
            if moving_base_card.color == dst_top.color:
                return self._reject(f"Color mismatch: {moving_base_card.code} ({moving_base_card.color}) cannot be placed on {dst_top.code} ({dst_top.color}). Alternating colors required.")
            if moving_base_card.rank.value != dst_top.rank.value - 1:
                return self._reject(f"Rank mismatch: {moving_base_card.code} (rank {moving_base_card.rank.value}) must be exactly one below {dst_top.code} (rank {dst_top.rank.value}).")

        # Detach run from source and attach to destination (DS-4, FR-4.6, TC-06)
        detached_run = src_pile.split_from(run_start_node)
        dst_pile.attach(detached_run)

        # Check if source now ends in a face-down card and auto-flip it (FR-6.3, TC-13)
        flipped_card = None
        score_delta = 0
        new_src_top = src_pile.peek_tail()
        if new_src_top is not None and not new_src_top.face_up:
            new_src_top.face_up = True
            flipped_card = new_src_top
            score_delta += 5  # +5 points for turning over tableau card
            self.score += 5

        # Record undo
        record = Move(
            move_type=MoveType.TABLEAU_TO_TABLEAU,
            source=f"T{src_idx+1}",
            dest=f"T{dst_idx+1}",
            cards=run_cards,
            flipped_card=flipped_card,
            score_delta=score_delta,
            combo_delta=-self.combo
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.combo = 0
        self.move_count += 1
        self._update_location_map()

        msg = f"Moved {count} card(s) from T{src_idx+1} to T{dst_idx+1}."
        if flipped_card:
            msg += f" (Revealed {flipped_card.code})"
        self.last_message = msg
        self.last_move_legal = True
        self.check_win()
        return True, msg

    # --------------------------------------------------------------------------
    # FOUNDATION MOVES (FR-5, UC-04)
    # --------------------------------------------------------------------------
    def move_tableau_to_foundation(self, src_idx: int) -> Tuple[bool, str]:
        """
        Moves top card of Tableau `src_idx` to its corresponding Foundation.
        """
        if self.is_won:
            return False, "Game is already won!"

        if src_idx < 0 or src_idx >= 7:
            return self._reject("Invalid tableau pile index (must be 0-6).")

        src_pile = self.tableau[src_idx]
        if src_pile.is_empty():
            return self._reject(f"Tableau pile T{src_idx+1} is empty.")

        card = src_pile.peek_tail()
        if card is None or not card.face_up:
            return self._reject("Card at top of tableau is not face-up.")

        # Find target foundation for card's suit
        f_idx = self.SUIT_ORDER.index(card.suit)
        foundation = self.foundations[f_idx]

        # Validate legal foundation placement (FR-5.2, FR-5.3, TC-12)
        legal, reason = self._can_place_on_foundation(card, foundation)
        if not legal:
            return self._reject(reason)

        # Pop from tableau and push onto foundation stack
        src_pile.pop_tail()
        foundation.push(card)

        # Auto-flip exposed card if present
        flipped_card = None
        score_delta = 10  # +10 points for foundation move
        new_src_top = src_pile.peek_tail()
        if new_src_top is not None and not new_src_top.face_up:
            new_src_top.face_up = True
            flipped_card = new_src_top
            score_delta += 5

        self.score += score_delta
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        record = Move(
            move_type=MoveType.TABLEAU_TO_FOUNDATION,
            source=f"T{src_idx+1}",
            dest=f"F{f_idx+1}",
            cards=[card],
            flipped_card=flipped_card,
            score_delta=score_delta,
            combo_delta=1
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.move_count += 1
        self._update_location_map()

        msg = f"Moved {card.code} from T{src_idx+1} to Foundation {card.suit.code}."
        if flipped_card:
            msg += f" (Revealed {flipped_card.code})"
        self.last_message = msg
        self.last_move_legal = True
        self.check_win()
        return True, msg

    def move_waste_to_foundation(self) -> Tuple[bool, str]:
        """
        Moves top card of Waste stack to its corresponding Foundation (FR-5.4).
        """
        if self.is_won:
            return False, "Game is already won!"

        if self.waste.is_empty():
            return self._reject("Waste pile is empty.")

        card: Card = self.waste.peek()
        f_idx = self.SUIT_ORDER.index(card.suit)
        foundation = self.foundations[f_idx]

        legal, reason = self._can_place_on_foundation(card, foundation)
        if not legal:
            return self._reject(reason)

        self.waste.pop()
        foundation.push(card)

        score_delta = 10
        self.score += score_delta
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        record = Move(
            move_type=MoveType.WASTE_TO_FOUNDATION,
            source='WASTE',
            dest=f"F{f_idx+1}",
            cards=[card],
            score_delta=score_delta,
            combo_delta=1
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.move_count += 1
        self._update_location_map()

        msg = f"Moved {card.code} from Waste to Foundation {card.suit.code}."
        self.last_message = msg
        self.last_move_legal = True
        self.check_win()
        return True, msg

    def move_waste_to_tableau(self, dst_idx: int) -> Tuple[bool, str]:
        """
        Moves top card of Waste to Tableau `dst_idx` (FR-4.3, FR-4.4).
        """
        if self.is_won:
            return False, "Game is already won!"

        if dst_idx < 0 or dst_idx >= 7:
            return self._reject("Invalid tableau pile index (must be 0-6).")

        if self.waste.is_empty():
            return self._reject("Waste pile is empty.")

        card: Card = self.waste.peek()
        dst_pile = self.tableau[dst_idx]

        if dst_pile.is_empty():
            if card.rank != Rank.KING:
                return self._reject(f"Only a King can be placed on an empty tableau pile (tried {card.code}).")
        else:
            dst_top = dst_pile.peek_tail()
            if dst_top is None:
                return self._reject("Destination pile top is unavailable.")
            if card.color == dst_top.color:
                return self._reject(f"Color mismatch: {card.code} ({card.color}) cannot go on {dst_top.code} ({dst_top.color}). Alternating colors required.")
            if card.rank.value != dst_top.rank.value - 1:
                return self._reject(f"Rank mismatch: {card.code} must be one rank below {dst_top.code}.")

        self.waste.pop()
        dst_pile.append(card)

        score_delta = 5  # +5 points for Waste to Tableau
        self.score += score_delta

        record = Move(
            move_type=MoveType.WASTE_TO_TABLEAU,
            source='WASTE',
            dest=f"T{dst_idx+1}",
            cards=[card],
            score_delta=score_delta,
            combo_delta=-self.combo
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.combo = 0
        self.move_count += 1
        self._update_location_map()

        msg = f"Moved {card.code} from Waste to T{dst_idx+1}."
        self.last_message = msg
        self.last_move_legal = True
        self.check_win()
        return True, msg

    def move_foundation_to_tableau(self, f_idx: int, dst_idx: int) -> Tuple[bool, str]:
        """
        Moves top card of Foundation `f_idx` back to Tableau `dst_idx` (FR-5.5).
        Incurs -15 points penalty.
        """
        if self.is_won:
            return False, "Game is already won!"

        if f_idx < 0 or f_idx >= 4 or dst_idx < 0 or dst_idx >= 7:
            return self._reject("Invalid foundation or tableau index.")

        foundation = self.foundations[f_idx]
        if foundation.is_empty():
            return self._reject(f"Foundation F{f_idx+1} is empty.")

        card: Card = foundation.peek()
        dst_pile = self.tableau[dst_idx]

        if dst_pile.is_empty():
            if card.rank != Rank.KING:
                return self._reject(f"Only a King can be placed on an empty tableau pile (tried {card.code}).")
        else:
            dst_top = dst_pile.peek_tail()
            if dst_top is None:
                return self._reject("Destination pile top is unavailable.")
            if card.color == dst_top.color:
                return self._reject(f"Color mismatch: {card.code} ({card.color}) cannot go on {dst_top.code} ({dst_top.color}).")
            if card.rank.value != dst_top.rank.value - 1:
                return self._reject(f"Rank mismatch: {card.code} must be one rank below {dst_top.code}.")

        foundation.pop()
        dst_pile.append(card)

        score_delta = -15
        self.score = max(0, self.score + score_delta)

        record = Move(
            move_type=MoveType.FOUNDATION_TO_TABLEAU,
            source=f"F{f_idx+1}",
            dest=f"T{dst_idx+1}",
            cards=[card],
            score_delta=score_delta,
            combo_delta=-self.combo
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.combo = 0
        self.move_count += 1
        self._update_location_map()

        msg = f"Moved {card.code} from Foundation F{f_idx+1} to T{dst_idx+1}."
        self.last_message = msg
        self.last_move_legal = True
        return True, msg

    def auto_foundation_card(self, card_id: int) -> Tuple[bool, str]:
        """
        Convenience method for double-clicking or targeting a specific card
        to send it to its Foundation if legal.
        """
        loc = self.location_map.get(card_id)
        if loc is None:
            return self._reject("Card not found in location map.")

        if loc.pile_type == 'TABLEAU':
            t_idx = loc.pile_index
            t_pile = self.tableau[t_idx]
            if t_pile.is_empty() or t_pile.peek_tail().id != card_id:
                return self._reject("Only the top card of a tableau pile can move to a foundation.")
            return self.move_tableau_to_foundation(t_idx)

        elif loc.pile_type == 'WASTE':
            if self.waste.is_empty() or self.waste.peek().id != card_id:
                return self._reject("Only the top waste card can move to a foundation.")
            return self.move_waste_to_foundation()

        return self._reject("Selected card is not eligible for foundation move.")

    # --------------------------------------------------------------------------
    # UNDO & REDO (FR-7)
    # --------------------------------------------------------------------------
    def undo(self) -> Tuple[bool, str]:
        """
        Reverses the most recent action on the Undo Stack (FR-7.1, FR-7.2, TC-15, TC-16).
        """
        if self.undo_stack.is_empty():
            msg = "Undo stack is empty. No moves to undo."
            self.last_message = msg
            self.last_move_legal = False
            return False, msg

        m: Move = self.undo_stack.pop()

        # Revert score and combo
        self.score = max(0, self.score - m.score_delta)
        if m.combo_delta > 0:
            self.combo = max(0, self.combo - m.combo_delta)

        # 1. Undo stock draw
        if m.move_type == MoveType.DRAW:
            # Drawn cards were pushed to waste face-up. Pop from waste, turn face-down, enqueue front to stock.
            for card in reversed(m.cards):
                popped = self.waste.pop()
                popped.face_up = False
                self.stock.enqueue_front(popped)

        # 2. Undo waste recycle
        elif m.move_type == MoveType.RECYCLE_WASTE:
            # Drain any drawn cards from waste
            for _ in m.cards:
                self.waste.pop()
            # Clear stock and restore original waste stack
            self.stock.clear()
            for card in m.recycled_cards:
                card.face_up = True
                self.waste.push(card)

        # 3. Undo Tableau to Tableau
        elif m.move_type == MoveType.TABLEAU_TO_TABLEAU:
            src_idx = int(m.source[1:]) - 1
            dst_idx = int(m.dest[1:]) - 1
            src_pile = self.tableau[src_idx]
            dst_pile = self.tableau[dst_idx]

            # If a card was flipped on source, un-flip it (FR-7.2, TC-15)
            if m.flipped_card is not None:
                m.flipped_card.face_up = False

            # Detach run from destination and attach back to source
            run_count = len(m.cards)
            run_start_node = dst_pile.get_run_from_top(run_count)
            detached = dst_pile.split_from(run_start_node)
            src_pile.attach(detached)

        # 4. Undo Tableau to Foundation
        elif m.move_type == MoveType.TABLEAU_TO_FOUNDATION:
            src_idx = int(m.source[1:]) - 1
            f_idx = int(m.dest[1:]) - 1
            src_pile = self.tableau[src_idx]
            foundation = self.foundations[f_idx]

            card = foundation.pop()
            if m.flipped_card is not None:
                m.flipped_card.face_up = False
            src_pile.append(card)

        # 5. Undo Waste to Foundation
        elif m.move_type == MoveType.WASTE_TO_FOUNDATION:
            f_idx = int(m.dest[1:]) - 1
            foundation = self.foundations[f_idx]
            card = foundation.pop()
            self.waste.push(card)

        # 6. Undo Waste to Tableau
        elif m.move_type == MoveType.WASTE_TO_TABLEAU:
            dst_idx = int(m.dest[1:]) - 1
            dst_pile = self.tableau[dst_idx]
            card = dst_pile.pop_tail()
            self.waste.push(card)

        # 7. Undo Foundation to Tableau
        elif m.move_type == MoveType.FOUNDATION_TO_TABLEAU:
            f_idx = int(m.source[1:]) - 1
            dst_idx = int(m.dest[1:]) - 1
            foundation = self.foundations[f_idx]
            dst_pile = self.tableau[dst_idx]
            card = dst_pile.pop_tail()
            foundation.push(card)

        # Push to redo stack (FR-7.3)
        self.redo_stack.push(m)
        self.is_won = False
        self._update_location_map()

        msg = f"Undid move: {m.move_type.value} ({m.source} -> {m.dest})."
        self.last_message = msg
        self.last_move_legal = True
        return True, msg

    def redo(self) -> Tuple[bool, str]:
        """
        Re-applies the most recently undone action (FR-7.4, TC-16).
        """
        if self.redo_stack.is_empty():
            msg = "Redo stack is empty. No moves to redo."
            self.last_message = msg
            self.last_move_legal = False
            return False, msg

        m: Move = self.redo_stack.pop()

        # Re-apply based on type
        if m.move_type == MoveType.DRAW:
            for card in m.cards:
                self.stock.dequeue()
                card.face_up = True
                self.waste.push(card)
        elif m.move_type == MoveType.RECYCLE_WASTE:
            self.waste.clear()
            self.stock.clear()
            temp_stack = Stack()
            for card in m.recycled_cards:
                card.face_up = False
                temp_stack.push(card)
            while not temp_stack.is_empty():
                self.stock.enqueue(temp_stack.pop())
            for card in m.cards:
                self.stock.dequeue()
                card.face_up = True
                self.waste.push(card)
        elif m.move_type == MoveType.TABLEAU_TO_TABLEAU:
            src_idx = int(m.source[1:]) - 1
            dst_idx = int(m.dest[1:]) - 1
            src_pile = self.tableau[src_idx]
            dst_pile = self.tableau[dst_idx]
            run_start_node = src_pile.get_run_from_top(len(m.cards))
            detached = src_pile.split_from(run_start_node)
            dst_pile.attach(detached)
            if m.flipped_card:
                m.flipped_card.face_up = True
        elif m.move_type == MoveType.TABLEAU_TO_FOUNDATION:
            src_idx = int(m.source[1:]) - 1
            f_idx = int(m.dest[1:]) - 1
            card = self.tableau[src_idx].pop_tail()
            self.foundations[f_idx].push(card)
            if m.flipped_card:
                m.flipped_card.face_up = True
        elif m.move_type == MoveType.WASTE_TO_FOUNDATION:
            f_idx = int(m.dest[1:]) - 1
            card = self.waste.pop()
            self.foundations[f_idx].push(card)
        elif m.move_type == MoveType.WASTE_TO_TABLEAU:
            dst_idx = int(m.dest[1:]) - 1
            card = self.waste.pop()
            self.tableau[dst_idx].append(card)
        elif m.move_type == MoveType.FOUNDATION_TO_TABLEAU:
            f_idx = int(m.source[1:]) - 1
            dst_idx = int(m.dest[1:]) - 1
            card = self.foundations[f_idx].pop()
            self.tableau[dst_idx].append(card)

        self.score += m.score_delta
        if m.combo_delta > 0:
            self.combo += m.combo_delta

        # Push back onto undo stack
        self.undo_stack.push(m)
        self._update_location_map()
        self.check_win()

        msg = f"Redid move: {m.move_type.value} ({m.source} -> {m.dest})."
        self.last_message = msg
        self.last_move_legal = True
        return True, msg

    # --------------------------------------------------------------------------
    # WIN CONDITION & AUTO-COMPLETE (FR-8)
    # --------------------------------------------------------------------------
    def check_win(self) -> bool:
        """
        Checks whether all 4 foundation piles hold 13 cards each (FR-8.1, TC-18, TC-19).
        """
        for f in self.foundations:
            if f.size() != 13:
                self.is_won = False
                return False
        self.is_won = True
        self.last_message = "VICTORY! All 52 cards built into Foundations!"
        return True

    def can_auto_complete(self) -> bool:
        """
        Checks if auto-complete condition is satisfied:
        Stock is empty, Waste is empty, and all cards in Tableau are face-up (FR-8.4).
        """
        if not self.stock.is_empty() or not self.waste.is_empty():
            return False
        for t in self.tableau:
            for card in t:
                if not card.face_up:
                    return False
        return True

    def auto_complete(self) -> Tuple[bool, str]:
        """
        Automatically cascades remaining cards to foundation if can_auto_complete() is true.
        """
        if not self.can_auto_complete():
            return False, "Auto-complete not available: reveal all tableau cards and empty draw pile first."

        moves_made = 0
        while not self.is_won:
            moved_this_round = False
            for t_idx in range(7):
                if not self.tableau[t_idx].is_empty():
                    top_card = self.tableau[t_idx].peek_tail()
                    f_idx = self.SUIT_ORDER.index(top_card.suit)
                    legal, _ = self._can_place_on_foundation(top_card, self.foundations[f_idx])
                    if legal:
                        self.move_tableau_to_foundation(t_idx)
                        moves_made += 1
                        moved_this_round = True
                        break
            if not moved_this_round:
                break

        self.check_win()
        return True, f"Auto-complete finished {moves_made} moves. Victory achieved!"

    # --------------------------------------------------------------------------
    # STRATEGIC HINT ENGINE (FR-10, Bonus)
    # Priority order:
    #   1. Move to foundation (Tableau or Waste)
    #   2. Tableau move that reveals a face-down card
    #   3. Waste to Tableau
    #   4. Other legal Tableau moves (e.g. King to empty or pile consolidation)
    #   5. Draw from stock
    # --------------------------------------------------------------------------
    def get_hint(self) -> Dict[str, Any]:
        """
        Analyzes the current board and suggests the highest priority strategic move.
        """
        if self.is_won:
            return {'hasHint': False, 'message': "Game is already won!"}

        # 1. Foundation moves
        # 1a. From Tableau
        for t_idx in range(7):
            t_pile = self.tableau[t_idx]
            if not t_pile.is_empty():
                top = t_pile.peek_tail()
                if top and top.face_up:
                    f_idx = self.SUIT_ORDER.index(top.suit)
                    legal, _ = self._can_place_on_foundation(top, self.foundations[f_idx])
                    if legal:
                        return {
                            'hasHint': True,
                            'type': 'FOUNDATION',
                            'source': f"T{t_idx+1}",
                            'dest': f"F{f_idx+1}",
                            'card': top.code,
                            'cardId': top.id,
                            'message': f"Send {top.code} from T{t_idx+1} to Foundation {top.suit.symbol}."
                        }

        # 1b. From Waste
        if not self.waste.is_empty():
            w_top: Card = self.waste.peek()
            f_idx = self.SUIT_ORDER.index(w_top.suit)
            legal, _ = self._can_place_on_foundation(w_top, self.foundations[f_idx])
            if legal:
                return {
                    'hasHint': True,
                    'type': 'FOUNDATION',
                    'source': 'W',
                    'dest': f"F{f_idx+1}",
                    'card': w_top.code,
                    'cardId': w_top.id,
                    'message': f"Send {w_top.code} from Waste to Foundation {w_top.suit.symbol}."
                }

        # 2. Tableau move that exposes a face-down card
        for src_idx in range(7):
            src_pile = self.tableau[src_idx]
            if src_pile.is_empty():
                continue

            # Check if there is at least one face-down card in this pile
            has_down_cards = any(not c.face_up for c in src_pile)
            if not has_down_cards:
                continue

            # Find the bottom-most face-up card
            curr = src_pile._head
            while curr and not curr.value.face_up:
                curr = curr.next

            if curr is None:
                continue

            # Run length from this card to tail
            moving_card = curr.value
            run_count = 0
            temp = curr
            while temp:
                run_count += 1
                temp = temp.next

            # See if this run can move to another tableau pile
            for dst_idx in range(7):
                if src_idx == dst_idx:
                    continue
                dst_pile = self.tableau[dst_idx]
                if dst_pile.is_empty():
                    if moving_card.rank == Rank.KING and curr.prev is not None:
                        # Moving King to expose face-down card
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': f"T{src_idx+1}",
                            'dest': f"T{dst_idx+1}",
                            'count': run_count,
                            'card': moving_card.code,
                            'cardId': moving_card.id,
                            'message': f"Move {moving_card.code} run ({run_count} cards) from T{src_idx+1} to empty T{dst_idx+1} to reveal hidden card."
                        }
                else:
                    dst_top = dst_pile.peek_tail()
                    if dst_top and moving_card.color != dst_top.color and moving_card.rank.value == dst_top.rank.value - 1:
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': f"T{src_idx+1}",
                            'dest': f"T{dst_idx+1}",
                            'count': run_count,
                            'card': moving_card.code,
                            'cardId': moving_card.id,
                            'message': f"Move {moving_card.code} run ({run_count} cards) from T{src_idx+1} onto {dst_top.code} (T{dst_idx+1}) to reveal hidden card."
                        }

        # 3. Waste to Tableau
        if not self.waste.is_empty():
            w_top = self.waste.peek()
            for dst_idx in range(7):
                dst_pile = self.tableau[dst_idx]
                if dst_pile.is_empty():
                    if w_top.rank == Rank.KING:
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': 'W',
                            'dest': f"T{dst_idx+1}",
                            'count': 1,
                            'card': w_top.code,
                            'cardId': w_top.id,
                            'message': f"Place King {w_top.code} from Waste onto empty T{dst_idx+1}."
                        }
                else:
                    dst_top = dst_pile.peek_tail()
                    if dst_top and w_top.color != dst_top.color and w_top.rank.value == dst_top.rank.value - 1:
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': 'W',
                            'dest': f"T{dst_idx+1}",
                            'count': 1,
                            'card': w_top.code,
                            'cardId': w_top.id,
                            'message': f"Move {w_top.code} from Waste onto {dst_top.code} (T{dst_idx+1})."
                        }

        # 4. Other Tableau consolidation moves
        for src_idx in range(7):
            src_pile = self.tableau[src_idx]
            if src_pile.is_empty():
                continue
            curr = src_pile._head
            while curr and not curr.value.face_up:
                curr = curr.next
            if curr is None:
                continue

            # Don't move a King from an already clean pile to an empty pile
            if curr.value.rank == Rank.KING and curr == src_pile._head:
                continue

            moving_card = curr.value
            run_count = 0
            temp = curr
            while temp:
                run_count += 1
                temp = temp.next

            for dst_idx in range(7):
                if src_idx == dst_idx:
                    continue
                dst_pile = self.tableau[dst_idx]
                if dst_pile.is_empty():
                    if moving_card.rank == Rank.KING:
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': f"T{src_idx+1}",
                            'dest': f"T{dst_idx+1}",
                            'count': run_count,
                            'card': moving_card.code,
                            'cardId': moving_card.id,
                            'message': f"Move King {moving_card.code} run to empty T{dst_idx+1}."
                        }
                else:
                    dst_top = dst_pile.peek_tail()
                    if dst_top and moving_card.color != dst_top.color and moving_card.rank.value == dst_top.rank.value - 1:
                        return {
                            'hasHint': True,
                            'type': 'TABLEAU',
                            'source': f"T{src_idx+1}",
                            'dest': f"T{dst_idx+1}",
                            'count': run_count,
                            'card': moving_card.code,
                            'cardId': moving_card.id,
                            'message': f"Move {moving_card.code} run from T{src_idx+1} onto {dst_top.code} (T{dst_idx+1})."
                        }

        # 5. Draw from stock
        if not self.stock.is_empty() or not self.waste.is_empty():
            return {
                'hasHint': True,
                'type': 'DRAW',
                'source': 'STOCK',
                'dest': 'WASTE',
                'message': "Draw from the Stock pile."
            }

        # 6. Stuck
        return {
            'hasHint': False,
            'message': "No legal moves remain. The game may be stuck!"
        }

    # --------------------------------------------------------------------------
    # CONSOLE COMMAND PARSER (Section 6.3)
    # --------------------------------------------------------------------------
    def execute_command(self, cmd_line: str) -> Tuple[bool, str]:
        """
        Parses and executes standard text console commands (FR-9.2, FR-9.3):
          - 'd'              : Draw from stock
          - 'm SRC DST [N]'  : Move N cards from SRC to DST (e.g. 'm T3 T5 2', 'm W T1')
          - 'f SRC'          : Move top of SRC to foundation (e.g. 'f W', 'f T4')
          - 'u'              : Undo last move
          - 'r'              : Redo last move
          - 'h'              : Show hint
          - 'n'              : New game
          - '?'              : Help
          - 'q'              : Quit
        """
        tokens = cmd_line.strip().split()
        if not tokens:
            return False, "Empty command. Type '?' for help."

        cmd = tokens[0].lower()

        if cmd == 'd':
            return self.draw()

        elif cmd == 'u':
            return self.undo()

        elif cmd == 'r':
            return self.redo()

        elif cmd == 'h':
            hint = self.get_hint()
            msg = hint['message']
            self.last_message = f"HINT: {msg}"
            return True, self.last_message

        elif cmd == 'n':
            self.new_game(seed=None, draw_mode=self.draw_mode)
            return True, "Started a new game."

        elif cmd == 'f':
            if len(tokens) < 2:
                return self._reject("Foundation command requires source: 'f W' or 'f T1' through 'f T7'")
            src = tokens[1].upper()
            if src == 'W':
                return self.move_waste_to_foundation()
            elif src.startswith('T') and len(src) == 2 and src[1].isdigit():
                t_idx = int(src[1]) - 1
                return self.move_tableau_to_foundation(t_idx)
            else:
                return self._reject(f"Unknown foundation source '{src}'. Use 'W' or 'T1'-'T7'.")

        elif cmd == 'm':
            if len(tokens) < 3:
                return self._reject("Move command requires: 'm SRC DST [COUNT]'. Example: 'm T3 T5 2' or 'm W T1'")
            src = tokens[1].upper()
            dst = tokens[2].upper()
            count = 1
            if len(tokens) >= 4 and tokens[3].isdigit():
                count = int(tokens[3])

            # Case: Tableau to Tableau
            if src.startswith('T') and dst.startswith('T'):
                if not (src[1:].isdigit() and dst[1:].isdigit()):
                    return self._reject("Tableau piles must be T1 to T7.")
                return self.move_tableau_to_tableau(int(src[1:]) - 1, int(dst[1:]) - 1, count=count)

            # Case: Waste to Tableau
            elif src == 'W' and dst.startswith('T'):
                if not dst[1:].isdigit():
                    return self._reject("Destination tableau must be T1 to T7.")
                return self.move_waste_to_tableau(int(dst[1:]) - 1)

            # Case: Waste to Foundation
            elif src == 'W' and (dst.startswith('F') or dst in ('FS', 'FH', 'FD', 'FC')):
                return self.move_waste_to_foundation()

            # Case: Tableau to Foundation
            elif src.startswith('T') and (dst.startswith('F') or dst in ('FS', 'FH', 'FD', 'FC')):
                if not src[1:].isdigit():
                    return self._reject("Source tableau must be T1 to T7.")
                return self.move_tableau_to_foundation(int(src[1:]) - 1)

            # Case: Foundation to Tableau
            elif src.startswith('F') and dst.startswith('T'):
                if not (src[1:].isdigit() and dst[1:].isdigit()):
                    return self._reject("Foundation must be F1-F4 and Tableau must be T1-T7.")
                return self.move_foundation_to_tableau(int(src[1:]) - 1, int(dst[1:]) - 1)

            else:
                return self._reject(f"Unsupported move from '{src}' to '{dst}'.")

        elif cmd in ('?', 'help'):
            help_text = (
                "COMMAND REFERENCE:\n"
                "  d               : Draw from stock\n"
                "  m SRC DST [N]   : Move N cards from SRC to DST (e.g. 'm T3 T5 2', 'm W T1')\n"
                "  f SRC           : Move top card of SRC to its foundation (e.g. 'f W', 'f T4')\n"
                "  u               : Undo previous move\n"
                "  r               : Redo undone move\n"
                "  h               : Get strategic hint\n"
                "  n               : Start new game\n"
                "  ?               : Show this help screen\n"
                "  q               : Quit game"
            )
            self.last_message = help_text
            return True, help_text

        elif cmd == 'q':
            return True, "QUIT"

        else:
            return self._reject(f"Unknown command '{cmd}'. Type '?' for help.")

    # --------------------------------------------------------------------------
    # INTERNAL HELPERS & VALIDATION
    # --------------------------------------------------------------------------
    def _can_place_on_foundation(self, card: Card, foundation: Stack) -> Tuple[bool, str]:
        """
        Validates whether `card` can legally be placed onto `foundation` (FR-5.2, FR-5.3).
        """
        if foundation.is_empty():
            if card.rank == Rank.ACE:
                return True, "Legal Ace foundation placement."
            return False, f"Foundation is empty. Only an Ace can start it (tried {card.code})."
        else:
            top_f: Card = foundation.peek()
            if card.suit != top_f.suit:
                return False, f"Suit mismatch: {card.code} does not match foundation suit {top_f.suit.code}."
            if card.rank.value != top_f.rank.value + 1:
                return False, f"Rank mismatch: {card.code} (rank {card.rank.value}) must be exactly one above {top_f.code} (rank {top_f.rank.value})."
            return True, "Legal foundation placement."

    def _reject(self, reason: str) -> Tuple[bool, str]:
        """Handles illegal moves: state unchanged, records reason (FR-6.2, NFR-6)."""
        self.last_message = f"INVALID MOVE: {reason}"
        self.last_move_legal = False
        self.combo = 0  # Mistake resets combo counter
        return False, self.last_message

    def _update_location_map(self) -> None:
        """
        DS-5, DS-9: Re-syncs the HashMap with current location and face status of all 52 cards.
        Key: card.id (0..51)
        Value: LocationRecord (pile_type, pile_index, position, face_up)
        """
        self.location_map.clear()

        # Stock queue
        stock_list = self.stock.to_list()
        for pos, c in enumerate(stock_list):
            self.location_map.put(c.id, LocationRecord('STOCK', 0, pos, c.face_up))

        # Waste stack
        waste_list = self.waste.to_list()
        for pos, c in enumerate(waste_list):
            self.location_map.put(c.id, LocationRecord('WASTE', 0, pos, c.face_up))

        # Foundations (4 stacks)
        for f_idx, f_stack in enumerate(self.foundations):
            f_list = f_stack.to_list()
            for pos, c in enumerate(f_list):
                self.location_map.put(c.id, LocationRecord('FOUNDATION', f_idx, pos, c.face_up))

        # Tableau (7 linked lists)
        for t_idx, t_pile in enumerate(self.tableau):
            t_list = t_pile.to_list()
            for pos, c in enumerate(t_list):
                self.location_map.put(c.id, LocationRecord('TABLEAU', t_idx, pos, c.face_up))

    # --------------------------------------------------------------------------
    # SERIALIZATION FOR UI & API
    # --------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Produces clean, JSON-serializable snapshot of entire game state for presentation layer.
        """
        elapsed = int(time.time() - self.start_time)
        return {
            'drawMode': self.draw_mode,
            'score': self.score,
            'moves': self.move_count,
            'combo': self.combo,
            'maxCombo': self.max_combo,
            'elapsedTime': elapsed,
            'isWon': self.is_won,
            'canAutoComplete': self.can_auto_complete(),
            'lastMessage': self.last_message,
            'lastMoveLegal': self.last_move_legal,
            'canUndo': not self.undo_stack.is_empty(),
            'canRedo': not self.redo_stack.is_empty(),
            'stock': {
                'count': self.stock.size()
            },
            'waste': {
                'count': self.waste.size(),
                'topCard': self.waste.peek().to_dict() if not self.waste.is_empty() else None,
                'cards': [c.to_dict() for c in self.waste.to_list()]
            },
            'foundations': [
                {
                    'index': i,
                    'suit': self.SUIT_ORDER[i].code,
                    'symbol': self.SUIT_ORDER[i].symbol,
                    'count': self.foundations[i].size(),
                    'topCard': self.foundations[i].peek().to_dict() if not self.foundations[i].is_empty() else None
                }
                for i in range(4)
            ],
            'tableau': [
                {
                    'index': i,
                    'count': self.tableau[i].size(),
                    'cards': [c.to_dict() for c in self.tableau[i].to_list()]
                }
                for i in range(7)
            ]
        }
