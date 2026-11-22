"""
ui.py - Console Text-Based User Interface for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project

Covers Requirements:
- UI-1: Show stock count, waste top, foundations, and 7 tableau piles after every action.
- UI-2: Face-down cards as [##], face-up as rank and suit (e.g. 7H, 10S).
- UI-3: Distinguishable suit representations with symbols.
- UI-4: One-line error messages on rejected actions.
- FR-9.1 to 9.5: Board display, commands (d, m, f, u, r, h, n, ?, q), confirmations.
"""

import sys
import os
from typing import Optional
from game import KlondikeGame


class ConsoleUI:
    """
    Console presentation layer for Klondike Solitaire.
    Strictly decoupled from model: interacts solely through KlondikeGame engine.
    """
    def __init__(self, game: Optional[KlondikeGame] = None):
        self.game = game if game is not None else KlondikeGame(draw_mode=1)
        self.running = True

    def clear_screen(self) -> None:
        """Clears terminal screen cross-platform."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_board(self) -> None:
        """
        Renders the complete board state matching Section 6.4 of the SRS.
        """
        # Stock representation
        stock_str = f"Stock: {self.game.stock.size():<2}"

        # Waste representation
        if not self.game.waste.is_empty():
            waste_card = self.game.waste.peek()
            waste_str = f"Waste: {waste_card.code:<3}"
        else:
            waste_str = "Waste: -- "

        # Foundations representation (F1 to F4)
        foundations_strs = []
        for i in range(4):
            f_stack = self.game.foundations[i]
            suit_sym = self.game.SUIT_ORDER[i].symbol
            if not f_stack.is_empty():
                top_card = f_stack.peek()
                foundations_strs.append(f"F{i+1}({suit_sym}): {top_card.code:<3}")
            else:
                foundations_strs.append(f"F{i+1}({suit_sym}): -- ")

        foundations_line = "  ".join(foundations_strs)

        print("\n" + "=" * 76)
        print(f" {stock_str}    {waste_str}       Foundations: {foundations_line}")
        print("=" * 76)

        # Tableau representation: 7 columns side by side
        print("   T1     T2     T3     T4     T5     T6     T7")
        print("  ----   ----   ----   ----   ----   ----   ----")

        # Determine max height among tableau piles
        max_height = max((pile.size() for pile in self.game.tableau), default=0)

        # Retrieve card lists for each column
        columns = [pile.to_list() for pile in self.game.tableau]

        for row in range(max_height):
            row_items = []
            for col in range(7):
                if row < len(columns[col]):
                    card = columns[col][row]
                    card_str = str(card)  # [##] or 7H / 10S
                    row_items.append(f"{card_str:^6}")
                else:
                    row_items.append("      ")
            print("  " + " ".join(row_items))

        print("-" * 76)
        score_info = f"Score: {self.game.score} | Moves: {self.game.move_count}"
        if self.game.combo > 1:
            score_info += f" | COMBO: {self.game.combo} HIT!"
        print(f" {score_info}")

        # Show message / error / win banner
        if self.game.is_won:
            print("\n" + "*" * 76)
            print(" *** VICTORY! YOU HAVE SUCCESSFULLY SOLVED KLONDIKE SOLITAIRE! ***")
            print("*" * 76)
        elif self.game.last_message:
            indicator = ">>" if self.game.last_move_legal else "[X]"
            print(f" {indicator} {self.game.last_message}")

        print(" Type '?' for help | 'd' draw | 'm T1 T2' move | 'f W' foundation | 'u' undo | 'q' quit")

    def start_loop(self) -> None:
        """Main game loop for text console."""
        self.clear_screen()
        print("============================================================================")
        print("       KLONDIKE SOLITAIRE - CSC200 DATA STRUCTURES & ALGORITHMS")
        print("============================================================================")

        # Prompt for draw mode
        while True:
            choice = input("Select Draw Mode (1 for Draw-1, 3 for Draw-3) [default 1]: ").strip()
            if not choice or choice == '1':
                self.game.draw_mode = 1
                break
            elif choice == '3':
                self.game.draw_mode = 3
                break
            else:
                print("Please enter 1 or 3.")

        self.game.new_game(draw_mode=self.game.draw_mode)

        while self.running:
            self.render_board()

            if self.game.is_won:
                ans = input("\nStart a New Game? (y/n): ").strip().lower()
                if ans == 'y':
                    self.game.new_game(draw_mode=self.game.draw_mode)
                    continue
                else:
                    print("Thank you for playing!")
                    break

            try:
                cmd = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Solitaire. Goodbye!")
                break

            if not cmd:
                continue

            if cmd.lower() == 'q':
                confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
                if confirm == 'y':
                    print("Goodbye!")
                    self.running = False
                    break
                else:
                    continue

            if cmd.lower() == 'n':
                confirm = input("Abandon current game and start new? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.game.new_game(draw_mode=self.game.draw_mode)
                continue

            # Execute command through game engine
            self.game.execute_command(cmd)


if __name__ == '__main__':
    ui = ConsoleUI()
    ui.start_loop()
