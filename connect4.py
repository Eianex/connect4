import sys

# --- CONSTANTS --- #
ROWS = 6
COLS = 7
EMPTY = "·"
PLAYER_NAMES = ["Red", "Yellow"]
PLAYER_SYMBOLS = ["R", "Y"]


# --- GAME LOGIC --- #
class Connect4:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.board = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]
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
        """Try to drop a disc in column. If invalid/full returns None, else the row index."""
        if self.winner is not None:
            return None
        if not (0 <= col < self.cols) or self.board[0][col] != -1:
            return None
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
            rr, cc, last_r, last_c = r + dr, c + dc, r, c
            n = 0
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
            if 1 + f_count + b_count >= 4:
                return (b_r, b_c), (f_r, f_c)
        return None


# --- UI --- #


def render_board(game: Connect4) -> str:
    def cell_char(r: int, c: int) -> str:
        owner = game.board[r][c]
        return PLAYER_SYMBOLS[owner] if owner != -1 else EMPTY

    header = " " + " ".join(f"{i}" for i in range(1, COLS + 1))
    lines = [header]
    for r in range(ROWS):
        row = " ".join(cell_char(r, c) for c in range(COLS))
        lines.append(f" {row}")
    return "\n".join(lines)


def prompt_column() -> int | None:
    while True:
        raw = input(
            f"{PLAYER_NAMES[game.current]} ({PLAYER_SYMBOLS[game.current]}) — choose column [1-{COLS}] (or 'q' to quit): "
        ).strip()
        if raw.lower() in {"q", "quit", "exit"}:
            return None
        try:
            col1 = int(raw)
        except ValueError:
            print(f"Please enter a number from 1 to {COLS}, or 'q' to quit.\n")
            continue
        if not (1 <= col1 <= COLS):
            print(f"Column must be between 1 and {COLS}.\n")
            continue
        return col1 - 1


if __name__ == "__main__":
    game = Connect4()

    print("\nConnect 4 console. Get 4 in a row to win.\n")
    print(render_board(game), "\n", sep="")

    turns = 0
    try:
        while True:
            col0 = prompt_column()
            if col0 is None:
                print("Goodbye!")
                sys.exit(0)

            row = game.drop(col0)
            if row is None:
                print("That column is full or invalid. Try a different one.\n")
                continue

            turns += 1
            print(render_board(game), "\n", sep="")

            if game.winner is not None:
                print(f"{PLAYER_NAMES[game.winner]} wins in {turns} moves! 🎉")
                break
            if game.is_draw():
                print("It's a draw! Board is full.")
                break

    except KeyboardInterrupt:
        print("\nInterrupted. Bye!")
