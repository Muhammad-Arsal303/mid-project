"""
test_solitaire.py - Automated Test Suite for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Covers all 22 SRS Test Cases (TC-01 through TC-22 per Section 10).
Runs with Python standard library unittest.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from card import Card, Suit, Rank
from dsa import Deck, Stack, Queue, LinkedList, HashMap
from game import KlondikeGame, MoveType


class TestKlondikeSolitaire(unittest.TestCase):

    # --------------------------------------------------------------------------
    # TC-01: Deck integrity (FR-1.1 to FR-1.3)
    # --------------------------------------------------------------------------
    def test_tc01_deck_integrity(self):
        deck = Deck()
        cards = deck.get_cards()
        self.assertEqual(len(cards), 52, "Deck must contain exactly 52 cards.")

        # Check uniqueness
        ids = {c.id for c in cards}
        self.assertEqual(len(ids), 52, "All 52 cards must have unique identities.")

        # Check 13 per suit
        for s in Suit:
            suit_cards = [c for c in cards if c.suit == s]
            self.assertEqual(len(suit_cards), 13, f"Suit {s} must have exactly 13 cards.")

        # Check 26 red and 26 black
        red_cards = [c for c in cards if c.color == 'red']
        black_cards = [c for c in cards if c.color == 'black']
        self.assertEqual(len(red_cards), 26, "Must be exactly 26 red cards.")
        self.assertEqual(len(black_cards), 26, "Must be exactly 26 black cards.")

    # --------------------------------------------------------------------------
    # TC-02: Shuffle (FR-1.4, FR-1.5)
    # --------------------------------------------------------------------------
    def test_tc02_shuffle(self):
        d1 = Deck()
        d1.shuffle(seed=42)
        order1 = [c.code for c in d1.get_cards()]

        d2 = Deck()
        d2.shuffle(seed=42)
        order2 = [c.code for c in d2.get_cards()]

        d3 = Deck()
        d3.shuffle(seed=999)
        order3 = [c.code for c in d3.get_cards()]

        self.assertEqual(order1, order2, "Same seed must produce identical shuffle order.")
        self.assertNotEqual(order1, order3, "Different seeds should produce different shuffle orders.")
        self.assertEqual(len(set(order1)), 52, "Shuffled deck must retain 52 unique cards.")

    # --------------------------------------------------------------------------
    # TC-03: Initial deal (FR-2.1 to FR-2.4)
    # --------------------------------------------------------------------------
    def test_tc03_initial_deal(self):
        game = KlondikeGame(draw_mode=1, seed=123)
        # Tableau sizes 1 to 7
        for i in range(7):
            pile = game.tableau[i]
            self.assertEqual(pile.size(), i + 1, f"Tableau T{i+1} must contain {i+1} cards.")
            cards = pile.to_list()
            # All face-down except the last card
            for pos, c in enumerate(cards):
                if pos == len(cards) - 1:
                    self.assertTrue(c.face_up, f"Top card of T{i+1} must be face-up.")
                else:
                    self.assertFalse(c.face_up, f"Underlying card {pos} of T{i+1} must be face-down.")

        # Stock has 24 cards
        self.assertEqual(game.stock.size(), 24, "Stock must contain 24 cards.")
        # Waste and foundations empty
        self.assertTrue(game.waste.is_empty(), "Waste must be empty at start.")
        for f in game.foundations:
            self.assertTrue(f.is_empty(), "Foundations must be empty at start.")

    # --------------------------------------------------------------------------
    # TC-04: Stack behavior (DS-2)
    # --------------------------------------------------------------------------
    def test_tc04_stack_behavior(self):
        stack = Stack()
        self.assertTrue(stack.is_empty())
        self.assertIsNone(stack.pop())

        stack.push("Alpha")
        stack.push("Beta")
        stack.push("Gamma")
        self.assertEqual(stack.size(), 3)
        self.assertEqual(stack.peek(), "Gamma")

        self.assertEqual(stack.pop(), "Gamma")
        self.assertEqual(stack.pop(), "Beta")
        self.assertEqual(stack.pop(), "Alpha")
        self.assertTrue(stack.is_empty())
        self.assertIsNone(stack.pop(), "Pop on empty stack should return None without crashing.")

    # --------------------------------------------------------------------------
    # TC-05: Queue behavior (DS-3)
    # --------------------------------------------------------------------------
    def test_tc05_queue_behavior(self):
        q = Queue()
        self.assertTrue(q.is_empty())
        self.assertIsNone(q.dequeue())

        q.enqueue("First")
        q.enqueue("Second")
        q.enqueue("Third")
        self.assertEqual(q.size(), 3)
        self.assertEqual(q.peek(), "First")

        self.assertEqual(q.dequeue(), "First")
        self.assertEqual(q.dequeue(), "Second")
        self.assertEqual(q.dequeue(), "Third")
        self.assertTrue(q.is_empty())
        self.assertIsNone(q.dequeue(), "Dequeue on empty queue should return None without crashing.")

    # --------------------------------------------------------------------------
    # TC-06: Linked list run detach (DS-4, FR-4.6)
    # --------------------------------------------------------------------------
    def test_tc06_linked_list_run_detach(self):
        src = LinkedList()
        dst = LinkedList()

        c1 = Card(Suit.SPADES, Rank.KING, face_up=True)
        c2 = Card(Suit.HEARTS, Rank.QUEEN, face_up=True)
        c3 = Card(Suit.CLUBS, Rank.JACK, face_up=True)
        c4 = Card(Suit.DIAMONDS, Rank.TEN, face_up=True)
        c5 = Card(Suit.SPADES, Rank.NINE, face_up=True)

        for c in [c1, c2, c3, c4, c5]:
            src.append(c)
        self.assertEqual(src.size(), 5)

        # Detach top 3 cards (c3, c4, c5)
        run_start = src.get_run_from_top(3)
        self.assertIsNotNone(run_start)
        self.assertEqual(run_start.value, c3)

        detached = src.split_from(run_start)
        self.assertEqual(src.size(), 2)
        self.assertEqual(detached.size(), 3)
        self.assertEqual(src.to_list(), [c1, c2])
        self.assertEqual(detached.to_list(), [c3, c4, c5])

        # Attach to dst
        dst.append(Card(Suit.HEARTS, Rank.KING, face_up=True))
        dst.attach(detached)
        self.assertEqual(dst.size(), 4)
        self.assertEqual(dst.peek_tail(), c5)

    # --------------------------------------------------------------------------
    # TC-07: Draw-1 and Draw-3 (FR-3.2, FR-3.3)
    # --------------------------------------------------------------------------
    def test_tc07_draw_modes(self):
        # Draw-1
        g1 = KlondikeGame(draw_mode=1, seed=1)
        ok, _ = g1.draw()
        self.assertTrue(ok)
        self.assertEqual(g1.waste.size(), 1)
        self.assertEqual(g1.stock.size(), 23)

        # Draw-3
        g3 = KlondikeGame(draw_mode=3, seed=1)
        ok, _ = g3.draw()
        self.assertTrue(ok)
        self.assertEqual(g3.waste.size(), 3)
        self.assertEqual(g3.stock.size(), 21)

    # --------------------------------------------------------------------------
    # TC-08: Waste recycle (FR-3.5, DS-7)
    # --------------------------------------------------------------------------
    def test_tc08_waste_recycle(self):
        game = KlondikeGame(draw_mode=1, seed=77)
        # Capture initial stock cards in sequence
        original_stock = [c.code for c in game.stock.to_list()]

        # Draw all 24 cards
        for _ in range(24):
            game.draw()
        self.assertEqual(game.stock.size(), 0)
        self.assertEqual(game.waste.size(), 24)

        # Draw again -> triggers recycle
        ok, _ = game.draw()
        self.assertTrue(ok)
        # In original order, so first card of original stock should be drawn
        self.assertEqual(game.waste.size(), 1)
        self.assertEqual(game.waste.peek().code, original_stock[0])
        self.assertEqual(game.stock.size(), 23)

    # --------------------------------------------------------------------------
    # TC-09: Legal tableau move (FR-4.3)
    # --------------------------------------------------------------------------
    def test_tc09_legal_tableau_move(self):
        game = KlondikeGame(draw_mode=1)
        # Force deterministic state
        game.tableau[0].pop_tail()
        game.tableau[1].pop_tail()

        black_7 = Card(Suit.SPADES, Rank.SEVEN, face_up=True)
        red_6 = Card(Suit.HEARTS, Rank.SIX, face_up=True)

        game.tableau[0].append(black_7)
        game.tableau[1].append(red_6)

        ok, msg = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertTrue(ok, f"Expected move to succeed: {msg}")
        self.assertEqual(game.tableau[0].peek_tail(), red_6)

    # --------------------------------------------------------------------------
    # TC-10: Illegal tableau moves (FR-4.3, FR-4.5, FR-6.2)
    # --------------------------------------------------------------------------
    def test_tc10_illegal_tableau_moves(self):
        game = KlondikeGame(draw_mode=1)
        game.tableau[0].pop_tail()
        game.tableau[1].pop_tail()

        black_7 = Card(Suit.SPADES, Rank.SEVEN, face_up=True)
        black_6 = Card(Suit.CLUBS, Rank.SIX, face_up=True)  # Same color!
        game.tableau[0].append(black_7)
        game.tableau[1].append(black_6)

        # Same color rejected
        ok, msg = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertFalse(ok)
        self.assertIn("Color mismatch", msg)

        # Wrong rank rejected
        red_5 = Card(Suit.HEARTS, Rank.FIVE, face_up=True)
        game.tableau[1].pop_tail()
        game.tableau[1].append(red_5)
        ok, msg = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertFalse(ok)
        self.assertIn("Rank mismatch", msg)

    # --------------------------------------------------------------------------
    # TC-11: Empty pile rule (FR-4.4)
    # --------------------------------------------------------------------------
    def test_tc11_empty_pile_rule(self):
        game = KlondikeGame(draw_mode=1)
        # Clear T1
        while not game.tableau[0].is_empty():
            game.tableau[0].pop_tail()

        # Non-King should fail
        queen = Card(Suit.SPADES, Rank.QUEEN, face_up=True)
        game.waste.push(queen)
        ok, msg = game.move_waste_to_tableau(dst_idx=0)
        self.assertFalse(ok)
        self.assertIn("Only a King", msg)

        # King should succeed
        game.waste.pop()
        king = Card(Suit.HEARTS, Rank.KING, face_up=True)
        game.waste.push(king)
        ok, msg = game.move_waste_to_tableau(dst_idx=0)
        self.assertTrue(ok)
        self.assertEqual(game.tableau[0].peek_tail(), king)

    # --------------------------------------------------------------------------
    # TC-12: Foundation rules (FR-5.2, FR-5.3)
    # --------------------------------------------------------------------------
    def test_tc12_foundation_rules(self):
        game = KlondikeGame(draw_mode=1)
        # Empty foundation rejects 2
        two_h = Card(Suit.HEARTS, Rank.TWO, face_up=True)
        game.waste.push(two_h)
        ok, msg = game.move_waste_to_foundation()
        self.assertFalse(ok)
        self.assertIn("Only an Ace", msg)

        # Ace accepted
        game.waste.pop()
        ace_h = Card(Suit.HEARTS, Rank.ACE, face_up=True)
        game.waste.push(ace_h)
        ok, msg = game.move_waste_to_foundation()
        self.assertTrue(ok)

        # 2 of same suit accepted
        game.waste.push(two_h)
        ok, msg = game.move_waste_to_foundation()
        self.assertTrue(ok)

        # 3 of different suit rejected
        three_s = Card(Suit.SPADES, Rank.THREE, face_up=True)
        game.waste.push(three_s)
        # Suit order: Spades=0, Hearts=1, Diamonds=2, Clubs=3. Spades foundation is empty.
        ok, msg = game.move_waste_to_foundation()
        self.assertFalse(ok)

    # --------------------------------------------------------------------------
    # TC-13: Card flipping (FR-6.3)
    # --------------------------------------------------------------------------
    def test_tc13_card_flipping(self):
        game = KlondikeGame(draw_mode=1, seed=42)
        # T2 has 2 cards: index 0 face-down, index 1 face-up
        t2 = game.tableau[1]
        self.assertEqual(t2.size(), 2)
        bottom_card = t2._head.value
        self.assertFalse(bottom_card.face_up)

        # Clear T1 and put opposite color rank+1
        top_t2 = t2.peek_tail()
        while not game.tableau[0].is_empty():
            game.tableau[0].pop_tail()

        target_color = Suit.HEARTS if top_t2.color == 'black' else Suit.SPADES
        target_rank = Rank.from_value(min(13, top_t2.rank.value + 1))
        target_card = Card(target_color, target_rank, face_up=True)
        game.tableau[0].append(target_card)

        # Move top card from T2 to T1
        ok, msg = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertTrue(ok)
        # Bottom card of T2 must now be flipped face-up automatically
        self.assertTrue(bottom_card.face_up, "Exposed card must be automatically flipped face-up.")

    # --------------------------------------------------------------------------
    # TC-14: Location map (FR-6.5, DS-9)
    # --------------------------------------------------------------------------
    def test_tc14_location_map(self):
        game = KlondikeGame(draw_mode=1, seed=55)
        # Do a few draws and moves
        game.draw()
        game.draw()

        # Check every card in location map matches reality
        self.assertEqual(game.location_map.size(), 52)
        for c_id in range(52):
            loc = game.location_map.get(c_id)
            self.assertIsNotNone(loc, f"Card id {c_id} must exist in HashMap.")
            if loc.pile_type == 'STOCK':
                found = any(c.id == c_id for c in game.stock.to_list())
                self.assertTrue(found)
            elif loc.pile_type == 'WASTE':
                found = any(c.id == c_id for c in game.waste.to_list())
                self.assertTrue(found)
            elif loc.pile_type == 'TABLEAU':
                found = any(c.id == c_id for c in game.tableau[loc.pile_index].to_list())
                self.assertTrue(found)
            elif loc.pile_type == 'FOUNDATION':
                found = any(c.id == c_id for c in game.foundations[loc.pile_index].to_list())
                self.assertTrue(found)

    # --------------------------------------------------------------------------
    # TC-15: Undo a flip (FR-7.1, FR-7.2)
    # --------------------------------------------------------------------------
    def test_tc15_undo_flip(self):
        game = KlondikeGame(draw_mode=1, seed=42)
        t2 = game.tableau[1]
        bottom_card = t2._head.value
        self.assertFalse(bottom_card.face_up)

        top_t2 = t2.peek_tail()
        while not game.tableau[0].is_empty():
            game.tableau[0].pop_tail()
        target_color = Suit.HEARTS if top_t2.color == 'black' else Suit.SPADES
        target_rank = Rank.from_value(min(13, top_t2.rank.value + 1))
        game.tableau[0].append(Card(target_color, target_rank, face_up=True))

        game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertTrue(bottom_card.face_up)

        # Undo the move
        ok, _ = game.undo()
        self.assertTrue(ok)
        self.assertFalse(bottom_card.face_up, "Undoing must restore card to face-down state.")
        self.assertEqual(game.tableau[1].peek_tail(), top_t2)

    # --------------------------------------------------------------------------
    # TC-16: Undo and redo chain (FR-7.3 to FR-7.5)
    # --------------------------------------------------------------------------
    def test_tc16_undo_redo_chain(self):
        game = KlondikeGame(draw_mode=1, seed=88)
        # Make 5 draws
        for _ in range(5):
            game.draw()
        self.assertEqual(game.waste.size(), 5)
        self.assertEqual(game.undo_stack.size(), 5)

        # Undo 3 times
        game.undo()
        game.undo()
        game.undo()
        self.assertEqual(game.waste.size(), 2)
        self.assertEqual(game.redo_stack.size(), 3)

        # Redo 2 times
        game.redo()
        game.redo()
        self.assertEqual(game.waste.size(), 4)
        self.assertEqual(game.redo_stack.size(), 1)

        # New move must clear redo stack
        game.draw()
        self.assertEqual(game.redo_stack.size(), 0)

    # --------------------------------------------------------------------------
    # TC-17: Empty undo/redo (FR-7.6)
    # --------------------------------------------------------------------------
    def test_tc17_empty_undo_redo(self):
        game = KlondikeGame(draw_mode=1)
        ok_u, msg_u = game.undo()
        self.assertFalse(ok_u)
        self.assertIn("empty", msg_u.lower())

        ok_r, msg_r = game.redo()
        self.assertFalse(ok_r)
        self.assertIn("empty", msg_r.lower())

    # --------------------------------------------------------------------------
    # TC-18: Win detection (FR-8.1 to FR-8.3)
    # --------------------------------------------------------------------------
    def test_tc18_win_detection(self):
        game = KlondikeGame(draw_mode=1)
        # Populate foundations nearly solved: 3 full (13 cards), 1 with 12 cards
        for f_idx in range(3):
            suit = game.SUIT_ORDER[f_idx]
            for r in range(1, 14):
                game.foundations[f_idx].push(Card(suit, Rank.from_value(r), face_up=True))

        suit4 = game.SUIT_ORDER[3]
        for r in range(1, 13):
            game.foundations[3].push(Card(suit4, Rank.from_value(r), face_up=True))

        self.assertFalse(game.check_win())

        # Place the final King (rank 13)
        king_card = Card(suit4, Rank.KING, face_up=True)
        game.waste.push(king_card)
        ok, msg = game.move_waste_to_foundation()
        self.assertTrue(ok)
        self.assertTrue(game.is_won, "Game must announce win when all 4 foundations hold 13 cards.")

        # Further moves must be refused
        ok2, _ = game.draw()
        self.assertFalse(ok2, "Further moves refused after win.")

    # --------------------------------------------------------------------------
    # TC-19: Not a win (FR-8.1)
    # --------------------------------------------------------------------------
    def test_tc19_not_a_win(self):
        game = KlondikeGame(draw_mode=1)
        for f_idx in range(3):
            suit = game.SUIT_ORDER[f_idx]
            for r in range(1, 14):
                game.foundations[f_idx].push(Card(suit, Rank.from_value(r), face_up=True))
        suit4 = game.SUIT_ORDER[3]
        for r in range(1, 13):
            game.foundations[3].push(Card(suit4, Rank.from_value(r), face_up=True))

        self.assertFalse(game.check_win(), "51 cards in foundation is not a win.")

    # --------------------------------------------------------------------------
    # TC-20: Bad input (FR-9.3, NFR-3)
    # --------------------------------------------------------------------------
    def test_tc20_bad_input(self):
        game = KlondikeGame(draw_mode=1)
        bad_commands = ["", "xyz", "m T99 T88", "m T1", "f invalid", "f T9"]
        for cmd in bad_commands:
            ok, msg = game.execute_command(cmd)
            self.assertFalse(ok, f"Command '{cmd}' should be safely rejected.")
            self.assertIsInstance(msg, str)

    # --------------------------------------------------------------------------
    # TC-21: Full game flow (NFR-4, all FR)
    # --------------------------------------------------------------------------
    def test_tc21_full_game_flow(self):
        game = KlondikeGame(draw_mode=1, seed=12345)
        # Verify 52 unique cards across all piles
        all_cards = []
        all_cards.extend(game.stock.to_list())
        all_cards.extend(game.waste.to_list())
        for f in game.foundations:
            all_cards.extend(f.to_list())
        for t in game.tableau:
            all_cards.extend(t.to_list())

        self.assertEqual(len(all_cards), 52)
        self.assertEqual(len(set(c.id for c in all_cards)), 52)

        # Execute multiple actions
        game.draw()
        game.draw()
        hint = game.get_hint()
        self.assertIn('hasHint', hint)
        game.undo()
        self.assertEqual(len(all_cards), 52)

    # --------------------------------------------------------------------------
    # TC-22: Hint strategic order (FR-10.1, FR-10.2)
    # --------------------------------------------------------------------------
    def test_tc22_hint_priority(self):
        game = KlondikeGame(draw_mode=1)
        # Put an Ace on waste
        ace = Card(Suit.SPADES, Rank.ACE, face_up=True)
        game.waste.push(ace)
        hint = game.get_hint()
        self.assertTrue(hint['hasHint'])
        self.assertEqual(hint['type'], 'FOUNDATION', "Foundation move should be prioritized in hints.")


if __name__ == '__main__':
    unittest.main()
