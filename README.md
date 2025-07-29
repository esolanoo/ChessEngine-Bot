# Simple Chess Engine — Documentation

*Version: 0.1 · Last updated: **23 Jul 2025***

---

## Table of Contents

- [Simple Chess Engine — Documentation](#simple-chess-engine--documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Quick Start](#quick-start)
  - [Module Architecture](#module-architecture)
    - [Constants](#constants)
    - [Class `Cell`](#class-cell)
    - [Class `Piece` *(inherits `Cell`)*](#class-piece-inherits-cell)
    - [Class `Game`](#class-game)
  - [API Reference](#api-reference)
    - [`Game(board_fen: str = initFEN)` → `Game`](#gameboard_fen-str--initfen--game)
      - [Methods](#methods)
    - [Utility Functions](#utility-functions)
  - [Illustrative Usage](#illustrative-usage)
  - [Design Decisions \& Trade‑offs](#design-decisions--tradeoffs)
  - [Extensibility Roadmap](#extensibility-roadmap)
  - [License](#license)

---

## Introduction

This single‑file Python module provides a minimal yet functional **chess engine core**. It focuses on:

* Lightweight **board representation** powered by **NumPy** for convenient slicing/masking.
* Parsing and serializing game states via **FEN** (Forsyth‑Edwards Notation).
* Basic generation of **pawn moves** with capture, double push, and first‑move tracking.

While not a full engine, the skeleton is ideal for:

* Educational purposes (data structures, game state encoding).
* Prototyping machine‑learning models on chess data.
* Serving as a foundation to incrementally add full move legality, check detection, perft testing, or UCI support.

---

## Quick Start

```bash
pip install numpy
```

```python
from chess_core import Game

# Initialise standard position
game = Game()

game.show()              # Human‑readable board printout
print(game.toFEN())       # "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Generate legal pawn moves for White
game.possible_moves('w')
print(game.pos_moves)     # e.g. ['Pae2e4', 'Pae2e3', ...]
```

---

## Module Architecture

### Constants

| Name             | Description                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `initFEN`        | Starting position in FEN.                                                                  |
| `val2str_pieces` | *int → char* lookup mapping engine‑internal piece codes (1–14) to their algebraic symbols. |
| `str2val_pieces` | Reverse mapping generated from `val2str_pieces`.                                           |

### Class `Cell`

Represents a **single square** on the 8×8 board grid.

```python
class Cell:
    def __init__(self, row, column):
        self.column = column            # 0‑indexed file (a→0 … h→7)
        self.row = row                  # 1‑indexed rank (1→bottom … 8→top)
        self.id = f"{chr(97+column)}{row}"  # Algebraic id, e.g. "e4"
        self.empty = True
        self.val = 0                    # Engine‑internal piece code (0 = empty)
```

* **`__str__` / `__repr__`** → `'.'` for printing empty squares.

### Class `Piece` *(inherits `Cell`)*

Wraps every non‑empty square with additional **piece metadata**.

```python
class Piece(Cell):
    def __init__(self, row, column, c):
        super().__init__(row, column)
        self.c = c                      # Symbol, e.g. 'p', 'N', 'K'
        self.empty = False
        self.color = 0 if c.islower() else 1   # 0 = black, 1 = white
        self.val = str2val_pieces[c]    # Numeric code (1–14)
        self.first_move = True          # Needed for pawn double push / castling
```
| Pieza 	| Color 	    | b<sub>2</sub> 	| Letra     | b<sub>10</sub> |
|-------	|-------	    |-------	        |-------	  |-------	|
| Black    	| King     	| 0x0001   	      | r      	  | 1     	|
| Black    	| Queen   	| 0x0010   	      | q      	  | 2      	|
| Black    	| Brook   	| 0x0011   	      | t      	  | 3      	|
| Black    	| Bishop   	| 0x0100   	      | a       	| 4      	|
| Black  	  | Knight  	| 0x0101   	      | c      	  | 5      	|
| Black    	| Pawn    	| 0x0110   	      | p      	  | 6      	|
| White   	| King   	  | 0x1001   	      | R      	  | 9      	|
| White   	| Queen   	| 0x1010        	| Q      	  | 10      |
| White   	| Brook   	| 0x1011        	| T      	  | 11     	|
| White   	| Bishop   	| 0x1100   	      | A      	  | 12     	|
| White  	  | Horse   	| 0x1101   	      | C      	  | 13     	|
| White   	| Pawn     	| 0x1110   	      | P      	  | 14     	|


### Class `Game`

Central coordinator maintaining the **entire game state**.

| Attribute   | Purpose                                                |
| ----------- | ------------------------------------------------------ |
| `board`     | 8×8 `numpy.ndarray` of `Cell` / `Piece` instances.     |
| `turn`      | `'w'` or `'b'` derived from FEN.                       |
| `castling`  | Castling rights string *("KQkq" etc.)*.                |
| `passant`   | En‑passant target square or `'-'`.                     |
| `halfmove`  | Half‑move clock for the 50‑move rule.                  |
| `step`      | Full move number.                                      |
| `pos_moves` | List of generated SAN‑like moves for the side to move. |

Key public methods:

```python
Game.show()          # Pretty console board
Game.fromFEN(fen)    # Load arbitrary FEN
Game.toFEN()         # Serialize current position → FEN
Game.possible_moves(color)  # Generate pawn moves mask‑wise
```

Under the hood the class relies on helper methods:

* `valid_pos()` — board bounds check.
* `enemy()` — quick color test between two coordinates.
* `mask()` — vectorised selection of squares containing own pieces (white/black).
* `posible_moves_ind()` — **per‑square** pawn move generator; appends SAN‑like strings to `self.pos_moves`.

> **Note** Only pawn moves are currently supported. Captures, promotions, castling, en‑passant execution, and check legality remain *TODOs*.

---

## API Reference

### `Game(board_fen: str = initFEN)` → `Game`

Creates a new game object seeded from **FEN** (defaults to `initFEN`).

#### Methods

| Signature                       | Description                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `fromFEN(fen) -> None`          | Populate `self.board` and meta‑fields from a FEN string.                      |
| `toFEN() -> str`                | Return current board state as FEN.                                            |
| `show() -> None`                | Print board and FEN to *stdout* (ranks top‑to‑bottom).                        |
| `possible_moves(color) -> None` | Populate `self.pos_moves` with pawn moves for the given side (`'w'` / `'b'`). |

### Utility Functions

None defined at module level; all helpers are private methods within the `Game` class for encapsulation.

---

## Illustrative Usage

Below is an end‑to‑end snippet exploring the API.

|   | a | b | c | d | e | f | g | h |
|-- |:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|*8*|64| 63| 62| 61| 60| 59| 58| 57|
|*7*|56| 55| 54| 53| 52| 51| 50| 49|
|*6*|48| 47| 46| 45| 44| 43| 42| 41|
|*5*|40| 39| 38| 37| 36| 35| 34| 33|
|*4*|32| 31| 30| 29| 28| 27| 26| 25|
|*3*|24| 23| 22| 21| 20| 19| 18| 17|
|*2*|16| 15| 14| 13| 12| 11| 10|  9|
|*1*|8 |  7|  6|  5|  4|  3|  2|  1|


```python
>>> from chess_core import Game
>>> g = Game()               # Standard chess start
>>> g.show()
8    r n b q k b n r
7    p p p p p p p p
6    . . . . . . . .
5    . . . . . . . .
4    . . . . . . . .
3    . . . . . . . .
2    P P P P P P P P
1    R N B Q K B N R

     a b c d e f g h

>>> g.possible_moves('w')
>>> print(g.pos_moves)
['Pa2a3', 'Pa2a4', 'Pb2b3', 'Pb2b4', 'Pc2c3', 'Pc2c4',
 'Pd2d3', 'Pd2d4', 'Pe2e3', 'Pe2e4', 'Pf2f3', 'Pf2f4',
 'Pg2g3', 'Pg2g4', 'Ph2h3', 'Ph2h4']
```

---

## Design Decisions & Trade‑offs

| Topic                            | Rationale                                                                                     | Alternatives                                          |
| -------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **NumPy board**                  | Uniform 8×8 array allows boolean masking and vectorised operations (e.g. per‑side filtering). | Pure Python list of lists; bitboards for performance. |
| **Piece codes 1–14**             | Compresses metadata (type + color) into a single int for ML/NN training.                      | Separate enums for type and color.                    |
| **`Cell` → `Piece` inheritance** | Minimises duplication—every piece *is‑a* cell with extra traits.                              | Composition (piece *has‑a* coordinate).               |
| **Limited move set**             | Keep MVP small; validate parsing/printing before tackling full legality.                      | Implement full rule set up front (longer dev cycle).  |

---

## Extensibility Roadmap

1. **Full move legality** — sliders, knight/king moves, promotions, en‑passant execution.
2. **Check / Checkmate detection** — integrate king‑safety tests.
3. **Perft & benchmarking** — validate node counts vs. known positions.
4. **Bitboard backend** — optional high‑performance layer using 64‑bit ints.
5. **UCI protocol adapter** — allow play against GUIs (e.g., Arena, CuteChess).
6. **Unit tests** — PyTest suite for move generation and FEN round‑trips.

---

## License

*SPDX‑Identifier: MIT* — Feel free to use, modify, and distribute under the terms of the MIT License.
