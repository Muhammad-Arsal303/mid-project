# NEON COAST // VICE CITY SOLITAIRE (CSC200 DSA EDITION)
**Course:** CSC200 Data Structures & Algorithms | Mid Term Project  
**Implementation Language / Tech:** Python (Core Engine & Backend) + HTML5 / CSS3 / JavaScript (Neon Coast / Vice City HUD Presentation Layer)

---

## 1. Project Overview & Architecture

The application is engineered strictly following the **Three-Layer Architecture** required by the SRS:

```
+-----------------------------------------------------------------------------------+
|                           PRESENTATION LAYER (UI)                                 |
|  - Web UI (Neon Coast - Vice City Solitaire HUD): web/index.html                  |
|    * Retro 80s Synthwave aesthetic, sunset grid, palm trees, glowing cards       |
|    * Live X-Ray Mode: live inspector for Queue, Stacks, LinkedLists, HashMap     |
|    * Procedural Web Audio API sound synthesis                                    |
|  - Text-Based Console CLI: ui.py (per Section 6.4 of SRS)                          |
+------------------------------------------+----------------------------------------+
                                           |  (Calls methods / REST API only)
                                           v
+-----------------------------------------------------------------------------------+
|                             LOGIC LAYER (ENGINE)                                  |
|  - game.py: KlondikeGame                                                          |
|    * Move validation & error messages                                            |
|    * Stock draw (Draw-1 / Draw-3) & Waste recycle in original order (DS-7)        |
|    * Tableau & Foundation movement rules                                         |
|    * Automatic card flipping (FR-6.3)                                            |
|    * Full Undo/Redo history via Memento pattern                                  |
|    * Strategic hints, Solitaire scoring & Combo counter                          |
|    * Win condition detection (FR-8.1) & Auto-complete (FR-8.4)                   |
+------------------------------------------+----------------------------------------+
                                           |  (Direct data structure manipulation)
                                           v
+-----------------------------------------------------------------------------------+
|                             MODEL LAYER (DATA STRUCTURES)                         |
|  - card.py: Card, Suit, Rank                                                      |
|  - dsa.py: Custom Hand-Written Data Structures                                    |
|    * DS-1: Deck / Array (52 cards, Fisher-Yates O(n) shuffle with optional seed) |
|    * DS-2: Stack (LIFO) -> Foundations (4), Waste, Undo, Redo                     |
|    * DS-3: Queue (FIFO) -> Stock draw pile (enqueue, dequeue, enqueue_front)      |
|    * DS-4 & DS-6: DoublyLinkedList -> 7 Tableau piles (split_from, attach)        |
|    * DS-5 & DS-9: HashMap -> O(1) Card ID to LocationRecord mapping              |
+-----------------------------------------------------------------------------------+
```

> **Strict Isolation Guarantee:** The Presentation layer (UI) **never** touches or modifies piles directly. The UI interacts exclusively through the `KlondikeGame` engine and renders the returned state snapshot (`to_dict()`).

---

## 2. Where Each Required Data Structure is Used

| ID | Data Structure | Used For | Key Operations & Complexity | SRS Reference |
|---|---|---|---|---|
| **DS-1** | **Array / Deck** | 52-card standard deck | Contiguous array, index swap, unbiased Fisher-Yates shuffle `O(n)`. | FR-1.3, FR-1.4, FR-1.5 |
| **DS-2** | **Stack (LIFO)** | 4 Foundation piles, Waste pile, Undo stack, Redo stack | Linked-node implementation: `push()`, `pop()`, `peek()`, `size()` — all strictly `O(1)`. | FR-3.4, FR-5.1, FR-7.1, FR-7.3 |
| **DS-3** | **Queue (FIFO)** | Stock (draw pile) | Linked-node with head & tail pointers: `enqueue()`, `dequeue()`, `peek()` — all strictly `O(1)`. | FR-3.1, DS-3 |
| **DS-4 & DS-6** | **Doubly LinkedList** | 7 Tableau columns | Head at bottom card, Tail at top card. Direct top access (`peek_tail()`, `pop_tail()`), `split_from(node)` to detach runs, `attach(run)` to reconnect — all `O(1)` pointer swaps. | FR-4.1, FR-4.2, DS-6 |
| **DS-5 & DS-9** | **HashMap** | Card location & face status tracking | Separate chaining collision resolution. Maps `card.id` (0..51) to `LocationRecord(pile_type, pile_index, position, face_up)` in `O(1)` average time. | FR-6.5, DS-5, DS-9 |

---

## 3. How to Run the Game

### Quick 1-Click Launchers (Windows)
- **Graphical UI (Tekken 8 HUD):** Double-click `run_game.bat`
- **Text Console CLI:** Double-click `run_cli.bat`
- **Automated Test Suite (TC-01 to TC-22):** Double-click `run_tests.bat`

### Command Line Execution
```bash
# Interactive Launcher Menu
python main.py

# Launch Tekken 8 Themed Graphical HUD directly
python main.py --gui

# Launch Text-Based Console CLI directly
python main.py --cli

# Run Complete 22-Test Automated Validation Suite
python main.py --test
```

*Note: The included batch files automatically locate the Python interpreter whether in the parent directory (`..\.python\python.exe`) or in system `PATH`.*

---

## 4. Controls & Visual Features (Tekken 8 Style)

### Visual Style
- **Aesthetic:** Dark cinematic fighting game HUD with dynamic particle embers and energy lines.
- **Palette:** Near-black background (`#050608`), fiery red-orange accent (`#ff1e1e`), electric cyan (`#00f0ff`), and gold highlights (`#ffcc00`).
- **Shapes & Panels:** Aggressive slanted parallelogram boxes (`clip-path: polygon(...)`) with neon glows.
- **Foundation Health Bars:** 4 slanted health bars (Spades, Hearts, Diamonds, Clubs) filling from 0 to 13 with gold glow on completion.
- **Combo Counter:** Consecutive foundation moves trigger `2 HIT`, `3 HIT`, `4 HIT COMBINATION!` popups.
- **Audio Synthesizer:** 100% offline, zero-asset Web Audio API procedural sound effects (punchy hits, whooshes, card flips, combo chimes, victory fanfare) with a mute toggle.

### Controls
- **Drag-and-Drop:** Drag any face-up card or run of cards onto legal tableau columns or foundations.
- **Click-to-Move:** Click a card to select it (cyan border highlight), then click the destination column or foundation.
- **Double-Click:** Instantly sends eligible cards to their suit foundation.
- **Stock Draw:** Click the Stock slot or press `D` on your keyboard.
- **Keyboard Shortcuts:**
  - `D`: Draw from Stock
  - `U`: Undo
  - `R`: Redo
  - `H`: Strategic Hint (golden outline pulse)
  - `C` or `/`: Toggle In-Game Console Command Bar
  - `?`: How to Play / Rules
  - `Esc`: Pause / Match Menu

---

## 5. Automated Validation & Test Suite

The test suite in `test_solitaire.py` covers **all 22 required test cases** from Section 10 of the SRS:
- **TC-01:** Deck integrity (52 unique cards, 13 per suit, 26 red, 26 black)
- **TC-02:** Unbiased Fisher-Yates shuffle & seed reproducibility
- **TC-03:** Initial deal (Tableau 1..7, only top cards face-up, stock 24, waste/foundations empty)
- **TC-04:** Stack LIFO behavior (push, pop, peek, empty handling)
- **TC-05:** Queue FIFO behavior (enqueue, dequeue, peek, empty handling)
- **TC-06:** DoublyLinkedList run detachment (`split_from`) and attachment (`attach`)
- **TC-07:** Draw-1 and Draw-3 modes
- **TC-08:** Waste recycling in original draw order (DS-7)
- **TC-09:** Legal tableau moves (descending rank, alternating colors)
- **TC-10:** Rejection of illegal moves (color mismatch, rank mismatch, face-down cards)
- **TC-11:** Empty pile King-only rule
- **TC-12:** Foundation rules (Ace first, ascending same suit)
- **TC-13:** Automatic card flipping of exposed tableau cards
- **TC-14:** HashMap location & state synchronization across all 52 cards
- **TC-15:** Undo a card flip (restores card to face-down state)
- **TC-16:** Undo and Redo chain integrity
- **TC-17:** Safe handling of empty undo/redo operations
- **TC-18:** Win detection (all 4 foundations hold 13 cards)
- **TC-19:** Non-win verification (51 cards in foundations is not a win)
- **TC-20:** Resilience to malformed/invalid user input (zero crashes)
- **TC-21:** Full end-to-end game flow and 52-card conservation
- **TC-22:** Strategic hint priority hierarchy

---

## 6. Viva Defense Guide (How UI Connects to Engine)

When presenting this project in your viva, use these points to defend your architectural design:

1. **Separation of Concerns:**
   - The UI contains **no game rules**. It cannot check whether a red 6 can be placed on a black 7, and it cannot directly alter node pointers or card face states.
   - When the user drags a card, the UI issues a command to `EngineClient.moveTableau(src, dst, count)` or `EngineClient.foundation()`.
   - The engine validates the move against Solitaire rules (`FR-4.3`, `FR-5.2`, etc.). If illegal, it leaves the state untouched and returns an explicit rejection reason (`UI-4`, `FR-6.2`). If legal, it updates the hand-written data structures, pushes to the Undo stack, syncs the HashMap, and returns a sanitized JSON snapshot (`to_dict()`).
   - The UI simply re-renders whatever state the engine returns.

2. **Why Hand-Written Data Structures Matter:**
   - **Queue for Stock:** Cards are drawn in FIFO order. When recycled, waste is emptied through a temporary stack into the queue so the first card drawn in round 1 is again the first card drawn in round 2 (`DS-7`).
   - **Stack for Foundations:** Only the top card is ever inspected or added (`O(1)` LIFO).
   - **Doubly LinkedList for Tableau:** Tableau cards frequently need to be detached in the middle of a column (a run of 3 or 4 cards) and spliced onto another column. A doubly linked list allows `split_from` and `attach` to be executed via `O(1)` pointer reconnections without shifting array elements.
   - **HashMap for Tracking:** Card lookups by ID (for double-click auto-foundation, hint validation, and state verification) occur in `O(1)` average time rather than scanning 7 tableau piles and 4 foundations.
