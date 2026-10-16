import unittest

from game import Board, InvalidMove, parse_position


class BoardTests(unittest.TestCase):
    def test_initial_board_is_empty(self):
        board = Board()
        self.assertTrue(board.is_full() is False)
        self.assertIsNone(board.winner())

    def test_place_mark(self):
        board = Board()
        board.place(0, 0, "X")
        self.assertEqual(board.cells[0][0], "X")

    def test_rejects_out_of_range_position(self):
        board = Board()
        with self.assertRaises(InvalidMove):
            board.place(3, 0, "X")
        with self.assertRaises(InvalidMove):
            board.place(0, -1, "O")

    def test_rejects_occupied_position(self):
        board = Board()
        board.place(1, 1, "X")
        with self.assertRaises(InvalidMove):
            board.place(1, 1, "O")

    def test_row_win(self):
        board = Board()
        for col in range(3):
            board.place(2, col, "X")
        self.assertEqual(board.winner(), "X")

    def test_column_win(self):
        board = Board()
        for row in range(3):
            board.place(row, 1, "O")
        self.assertEqual(board.winner(), "O")

    def test_diagonal_win(self):
        board = Board()
        for index in range(3):
            board.place(index, index, "X")
        self.assertEqual(board.winner(), "X")

    def test_draw(self):
        layout = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"],
        ]
        board = Board()
        board.cells = [row[:] for row in layout]
        self.assertTrue(board.is_full())
        self.assertIsNone(board.winner())

    def test_parse_position(self):
        self.assertEqual(parse_position("0 2"), (0, 2))
        self.assertEqual(parse_position("1,2"), (1, 2))
        with self.assertRaises(InvalidMove):
            parse_position("3 0")


if __name__ == "__main__":
    unittest.main()
