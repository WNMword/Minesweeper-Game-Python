# Minesweeper Game (Python)

A complete Minesweeper game with multiple modes (Beginner, Intermediate, Expert, and Custom). The game runs in a desktop window and supports left-click to reveal, right-click to place flags, a timer, and win/lose dialogs.

## Features
- Multiple modes: Beginner, Intermediate, Expert, Custom
- Left-click to reveal, right-click to flag
- Timer and remaining mine counter
- Win/lose detection

## Run Locally
```bash
python minesweeper.py
```

> Requires Python 3 with Tkinter (included with most Python installations).

## Package as an EXE (Windows)
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller --onefile --windowed minesweeper.py
   ```
3. The EXE will be available in the `dist` folder.

## Controls
- Left click: reveal a cell
- Right click: toggle a flag
- Reset: start a new game
