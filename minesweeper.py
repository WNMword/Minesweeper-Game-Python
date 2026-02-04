import random
import tkinter as tk
from tkinter import messagebox, simpledialog


MODES = {
    "Beginner (9x9, 10 mines)": (9, 9, 10),
    "Intermediate (16x16, 40 mines)": (16, 16, 40),
    "Expert (30x16, 99 mines)": (30, 16, 99),
}


class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.resizable(True, True)
        self.minsize(400, 400)

        self.status_frame = tk.Frame(self)
        self.status_frame.pack(pady=(10, 5))

        self.mines_label = tk.Label(self.status_frame, text="Mines: 0")
        self.mines_label.pack(side=tk.LEFT, padx=10)

        self.timer_label = tk.Label(self.status_frame, text="Time: 0")
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(
            self.status_frame, text="Reset", command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.mode_var = tk.StringVar(value=list(MODES.keys())[0])
        self.mode_menu = tk.OptionMenu(
            self.status_frame, self.mode_var, *MODES.keys(), "Custom...",
            command=self.change_mode,
        )
        self.mode_menu.pack(side=tk.LEFT)

        self.board_frame = tk.Frame(self)
        self.board_frame.pack(padx=10, pady=(0, 10), expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.board_frame, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.handle_left_click)
        self.canvas.bind("<Button-3>", self.handle_right_click)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.rows = 0
        self.cols = 0
        self.mines = 0
        self.mine_positions = set()
        self.revealed = set()
        self.flags = set()
        self.game_over = False
        self.timer_running = False
        self.elapsed = 0
        self.timer_id = None
        self.cell_size = 30
        self.trigger_mine = None

        self.change_mode(self.mode_var.get())

    def change_mode(self, selection):
        if selection == "Custom...":
            rows = simpledialog.askinteger(
                "Custom Mode", "Rows (5-30):", minvalue=5, maxvalue=30
            )
            if rows is None:
                self.mode_var.set(list(MODES.keys())[0])
                selection = self.mode_var.get()
                rows, cols, mines = MODES[selection]
            else:
                cols = simpledialog.askinteger(
                    "Custom Mode", "Columns (5-30):", minvalue=5, maxvalue=30
                )
                if cols is None:
                    self.mode_var.set(list(MODES.keys())[0])
                    selection = self.mode_var.get()
                    rows, cols, mines = MODES[selection]
                else:
                    max_mines = rows * cols - 1
                    mines = simpledialog.askinteger(
                        "Custom Mode",
                        f"Mines (1-{max_mines}):",
                        minvalue=1,
                        maxvalue=max_mines,
                    )
                    if mines is None:
                        self.mode_var.set(list(MODES.keys())[0])
                        selection = self.mode_var.get()
                        rows, cols, mines = MODES[selection]
                    else:
                        self.mode_var.set(f"Custom ({rows}x{cols}, {mines} mines)")
        else:
            rows, cols, mines = MODES[selection]
        self.rows, self.cols, self.mines = rows, cols, mines
        self.reset_game()

    def reset_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.elapsed = 0
        self.timer_running = False
        self.timer_label.config(text="Time: 0")

        self.mine_positions = set()
        self.revealed = set()
        self.flags = set()
        self.game_over = False
        self.trigger_mine = None
        self.mines_label.config(text=f"Mines: {self.mines}")
        self.cell_size = 30

        self.place_mines()
        self.draw_board()

    def place_mines(self):
        self.mine_positions = set()
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running and not self.game_over:
            self.elapsed += 1
            self.timer_label.config(text=f"Time: {self.elapsed}")
            self.timer_id = self.after(1000, self.update_timer)

    def on_canvas_resize(self, event):
        if self.rows == 0 or self.cols == 0:
            return
        size = min(event.width / self.cols, event.height / self.rows)
        self.cell_size = max(18, int(size))
        self.draw_board()

    def handle_left_click(self, event):
        cell = self.get_cell_from_xy(event.x, event.y)
        if cell:
            self.reveal_cell(*cell)

    def handle_right_click(self, event):
        cell = self.get_cell_from_xy(event.x, event.y)
        if cell:
            self.toggle_flag(*cell)

    def get_cell_from_xy(self, x, y):
        if self.cell_size <= 0:
            return None
        row = int(y // self.cell_size)
        col = int(x // self.cell_size)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None

    def toggle_flag(self, row, col):
        if self.game_over or (row, col) in self.revealed:
            return
        self.start_timer()
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        else:
            self.flags.add((row, col))
        remaining = self.mines - len(self.flags)
        self.mines_label.config(text=f"Mines: {remaining}")
        self.draw_board()
        self.check_win()

    def reveal_cell(self, row, col):
        if self.game_over or (row, col) in self.flags or (row, col) in self.revealed:
            return
        self.start_timer()
        if (row, col) in self.mine_positions:
            self.game_over = True
            self.trigger_mine = (row, col)
            self.draw_board()
            messagebox.showerror("Game Over", "Boom! You hit a mine.")
            return

        self.flood_reveal(row, col)
        self.draw_board()
        self.check_win()

    def flood_reveal(self, row, col):
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) in self.revealed:
                continue
            self.revealed.add((r, c))
            adjacent = self.count_adjacent_mines(r, c)
            if adjacent == 0:
                for nr, nc in self.get_neighbors(r, c):
                    if (nr, nc) not in self.revealed and (nr, nc) not in self.flags:
                        stack.append((nr, nc))

    def count_adjacent_mines(self, row, col):
        return sum((nr, nc) in self.mine_positions for nr, nc in self.get_neighbors(row, col))

    def get_neighbors(self, row, col):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def draw_board(self):
        self.canvas.delete("all")
        if self.rows == 0 or self.cols == 0:
            return
        font_size = max(10, int(self.cell_size * 0.45))
        font = ("Arial", font_size, "bold")

        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (r, c) in self.revealed:
                    fill_color = "#e0e0e0"
                else:
                    fill_color = "#f5f5f5"

                if self.game_over and (r, c) in self.mine_positions:
                    if (r, c) == self.trigger_mine:
                        fill_color = "#ff6b6b"
                    else:
                        fill_color = "#d9d9d9"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline="#8c8c8c"
                )

                if (r, c) in self.revealed:
                    adjacent = self.count_adjacent_mines(r, c)
                    if adjacent > 0:
                        self.canvas.create_text(
                            (x1 + x2) / 2,
                            (y1 + y2) / 2,
                            text=str(adjacent),
                            font=font,
                            fill="#2f4f4f",
                        )
                elif (r, c) in self.flags:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text="🚩",
                        font=font,
                    )
                elif self.game_over and (r, c) in self.mine_positions:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text="💣",
                        font=font,
                    )

    def check_win(self):
        if self.game_over:
            return
        total_cells = self.rows * self.cols
        if len(self.revealed) == total_cells - self.mines:
            self.game_over = True
            self.timer_running = False
            self.draw_board()
            messagebox.showinfo("You Win!", "Congratulations, you cleared the board!")


if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()
