# Python Chess Engine

A chess engine built in Python using **alpha-beta pruning, negamax search, iterative deepening, quiescence search, transposition-table caching, and heuristic move ordering**.

The project includes both a **Tkinter GUI** and a **command-line interface**.

## Features

- Alpha-beta pruning with negamax search
- Iterative deepening
- Quiescence search
- Transposition table
- Killer-move and history heuristics
- Custom evaluation function using material, piece-square tables, pawn structure, mobility, and king safety
- Tkinter graphical interface
- Legal-move highlighting
- Pawn promotion
- Human-vs-engine gameplay

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt`:

```text
python-chess==1.999
Pillow==12.3.0
```

## Run the GUI

Launch the graphical version with:

```powershell
python board.py
```

### How to Play

The GUI currently has the human player as **White** and the engine as Black.

1. Click one of your pieces.
2. Legal destination squares will be highlighted.
3. Click a highlighted square to make your move.
4. The engine will automatically calculate and play its response.
5. If a pawn reaches the final rank, choose a promotion piece from the popup window.

The `pieces/` directory must remain in the project folder because the GUI loads the chess-piece images from it.

## Run the CLI

Launch the command-line version with:

```powershell
python chess_engine.py
```

The CLI currently accepts **UCI notation**, for example:

```text
e7e5
g8f6
d7d5
```

The command-line engine can be configured to play either White or Black using the `engine_plays_white` argument.

## How the Engine Works

The engine evaluates positions using material values, piece-square tables, pawn structure, mobility, bishop-pair bonuses, passed pawns, and king safety.

Move selection uses alpha-beta pruning with negamax search. Search performance is improved through iterative deepening, quiescence search, move ordering, transposition-table caching, killer moves, and history heuristics.

## Current Limitations

- GUI currently supports the human player as White only
- No board rotation for Black yet
- Search depth is fixed in the GUI
- CLI currently requires UCI notation
- Playing strength has not been formally benchmarked

## Planned Improvements

- Add White/Black selection to the GUI
- Rotate the board automatically
- Add configurable difficulty/search depth
- Support standard algebraic notation in the CLI
- Improve evaluation and search performance
- Benchmark the engine against known engine ratings

## Status

**Active Development**
