"""Pure game rules for Tic-Tac-Toe."""

from __future__ import annotations

from typing import Optional, Sequence


class InvalidMove(ValueError):
    """Raised when a move is outside the board or targets an occupied cell."""


class GameOver(RuntimeError):
    """Raised when a move is attempted after the game has ended."""


class Board:
    def __init__(self) -> None:
        self.cells = [[" " for _ in range(3)] for _ in range(3)]

    def validate_move(self, row: int, col: int) -> None:
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise InvalidMove("linha e coluna devem estar entre 0 e 2.")
        if self.cells[row][col] != " ":
            raise InvalidMove("essa posição já está ocupada.")

    def place(self, row: int, col: int, mark: str) -> None:
        if mark not in {"X", "O"}:
            raise ValueError("o símbolo deve ser X ou O.")
        self.validate_move(row, col)
        self.cells[row][col] = mark

    def winner(self) -> Optional[str]:
        lines = []
        lines.extend(self.cells)
        lines.extend([[self.cells[row][col] for row in range(3)] for col in range(3)])
        lines.append([self.cells[i][i] for i in range(3)])
        lines.append([self.cells[i][2 - i] for i in range(3)])

        for line in lines:
            if line[0] != " " and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def is_full(self) -> bool:
        return all(cell != " " for row in self.cells for cell in row)


def parse_position(raw: str) -> tuple[int, int]:
    """Parse 'row col' or 'row,col', enforcing integer coordinates."""
    cleaned = raw.replace(",", " ").split()
    if len(cleaned) != 2:
        raise InvalidMove("informe dois números: linha e coluna (ex.: 1 2).")
    try:
        row, col = int(cleaned[0]), int(cleaned[1])
    except ValueError as exc:
        raise InvalidMove("linha e coluna devem ser números inteiros.") from exc
    if not (0 <= row <= 2 and 0 <= col <= 2):
        raise InvalidMove("linha e coluna devem estar entre 0 e 2.")
    return row, col


def format_board(cells: Sequence[Sequence[str]]) -> str:
    """Return a readable 3x3 board, including coordinate labels."""
    rows = ["    0   1   2", "  +---+---+---+"]
    for index, row in enumerate(cells):
        values = [cell if cell != " " else " " for cell in row]
        rows.append(f"{index} | {values[0]} | {values[1]} | {values[2]} |")
        rows.append("  +---+---+---+")
    return "\n".join(rows)
