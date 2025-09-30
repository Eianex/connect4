import tkinter as tk

# --- CONFIG --- #
ROWS = 6
COLS = 7
CELL = 80
PADDING = 12
BOARD_BG = "#1d3557"
EMPTY_COLOR = "#f1faee"
PLAYER_NAMES = ["Red", "Yellow"]
PLAYER_COLORS = ["#e63946", "#ffd166"]
FONT = ("Helvetica", 14, "bold")
WIN_LINE_COLOR = "#06d6a0"
WIN_LINE_WIDTH = 8


# --- GAME LOGIC --- #
class Connect4:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS

        # The game board: -1 = empty, 0 = player 0, 1 = player 1
        self.board = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]
        # Whose turn it is (0 = Red, 1 = Yellow)
        self.current = 0

        self.winner = None
        self.move_count = 0
        self.win_line = None

    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = -1
        self.current = 0
        self.winner = None
        self.move_count = 0
        self.win_line = None

    def drop(self, col: int):
        """Try to drop a disc in column. If invalid returns the row index or None."""
        if self.winner is not None:
            return None
        if not (0 <= col < self.cols) or self.board[0][col] != -1:
            return None
        # Find lowest empty slot
        row = self.rows - 1
        while row >= 0 and self.board[row][col] != -1:
            row -= 1
        self.board[row][col] = self.current
        self.move_count += 1

        win_span = self._winning_span(row, col)
        if win_span:
            self.winner = self.current
            self.win_line = win_span
        else:
            self.current = 1 - self.current
        return row

    def is_draw(self) -> bool:
        return self.winner is None and self.move_count == self.rows * self.cols

    def _winning_span(self, r: int, c: int):
        """If the move creates a win, return ((r0,c0),(r1,c1)) endpoints; else None."""
        player = self.board[r][c]
        if player == -1:
            return None

        def count_and_last(dr: int, dc: int):
            rr, cc, n = r + dr, c + dc, 0
            last_r, last_c = r, c
            while (
                0 <= rr < self.rows
                and 0 <= cc < self.cols
                and self.board[rr][cc] == player
            ):
                n += 1
                last_r, last_c = rr, cc
                rr += dr
                cc += dc
            return n, last_r, last_c

        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            f_count, f_r, f_c = count_and_last(dr, dc)
            b_count, b_r, b_c = count_and_last(-dr, -dc)
            total = 1 + f_count + b_count
            if total >= 4:
                # Endpoints: b_r, b_c back endpoint; f_r, f_c front endpoint
                start = (b_r, b_c)
                end = (f_r, f_c)
                return start, end
        return None


# --- UI --- #
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4")
        self.resizable(False, False)

        self.game = Connect4()
        self.hover_col = None

        self.status = tk.Label(self, font=FONT)
        self.status.pack(padx=10, pady=(10, 0), anchor="w")

        self.canvas = tk.Canvas(
            self,
            width=COLS * CELL,
            height=ROWS * CELL,
            bg=BOARD_BG,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(padx=10, pady=10)

        controls = tk.Frame(self)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(controls, text="New Game", command=self.new_game).pack(side="left")

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)

        self.redraw()
        self.update_status()

    def on_click(self, event):
        if self.game.winner is not None or self.game.is_draw():
            return
        col = event.x // CELL
        if self.game.drop(col) is not None:
            self.redraw()
            self.update_status()

    def on_motion(self, event):
        col = event.x // CELL
        new_hover = col if 0 <= col < COLS else None
        if new_hover != self.hover_col:
            self.hover_col = new_hover
            self.redraw()

    def redraw(self):
        self.canvas.delete("all")

        # Hover highlight (only when game active)
        if (
            self.hover_col is not None
            and self.game.winner is None
            and not self.game.is_draw()
        ):
            x0 = self.hover_col * CELL
            self.canvas.create_rectangle(
                x0,
                0,
                x0 + CELL,
                ROWS * CELL,
                fill="#2E386D",
                outline="",
            )

        # Discs
        for r in range(ROWS):
            for c in range(COLS):
                x0 = c * CELL + PADDING
                y0 = r * CELL + PADDING
                x1 = (c + 1) * CELL - PADDING
                y1 = (r + 1) * CELL - PADDING
                owner = self.game.board[r][c]
                fill = PLAYER_COLORS[owner] if owner != -1 else EMPTY_COLOR
                self.canvas.create_oval(x0, y0, x1, y1, fill=fill, outline="#111")

        # Winning line overlay
        if self.game.win_line:
            (r0, c0), (r1, c1) = self.game.win_line
            x0 = c0 * CELL + CELL // 2
            y0 = r0 * CELL + CELL // 2
            x1 = c1 * CELL + CELL // 2
            y1 = r1 * CELL + CELL // 2
            self.canvas.create_line(
                x0,
                y0,
                x1,
                y1,
                fill=WIN_LINE_COLOR,
                width=WIN_LINE_WIDTH,
                capstyle=tk.ROUND,
            )

    def update_status(self):
        if self.game.winner is not None:
            self.status.config(
                text=f"{PLAYER_NAMES[self.game.winner]} wins! Click 'New Game' to play again."
            )
        elif self.game.is_draw():
            self.status.config(text="It's a draw. Click 'New Game' to play again.")
        else:
            self.status.config(
                text=f"{PLAYER_NAMES[self.game.current]}'s move: click a column."
            )

    def new_game(self):
        self.game.reset()
        self.hover_col = None
        self.redraw()
        self.update_status()


if __name__ == "__main__":
    App().mainloop()
