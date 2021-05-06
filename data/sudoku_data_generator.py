from random import sample, choice
from itertools import islice
from copy import deepcopy


class Sudoku:
    """
    https://stackoverflow.com/questions/45471152/how-to-create-a-sudoku-puzzle-in-python

    """
    def __init__(self, difficulty):
        base = 3
        self.base = base
        self.side = base * base
        self.difficulty = difficulty
        self.clearance_rate = self.encode_difficulty()
        self.board = self.build_board()
        self.puzzle = self.build_puzzle()
        self.puzzle_flat = [n for row in self.puzzle for n in row]

    def encode_difficulty(self):
        difficulty = self.difficulty
        if difficulty == 1:
            clearance_rate = .25
        elif difficulty == 2:
            clearance_rate = .5
        elif difficulty == 3:
            clearance_rate = .75
        else:
            raise NotImplementedError('choose difficulty from [1,2,3]')

        return clearance_rate

    def build_board(self):
        base = self.base
        side = self.side

        # pattern for a baseline valid solution
        def pattern(r, c): return (base * (r % base) + r // base + c) % side

        # randomize rows, columns and numbers (of valid base pattern)
        def shuffle(s): return sample(s, len(s))

        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        return board

    def _clear_board(self):
        board = deepcopy(self.board)
        side = self.side

        squares = side * side
        empties = squares * self.difficulty//4
        for p in sample(range(squares), empties):
            board[p // side][p % side] = 0

        numSize = len(str(side))
        # for line in board: print("[" + "  ".join(f"{n or '.':{numSize}}" for n in line) + "]")
        return board

    @staticmethod
    def _solve(puzzle):
        board = puzzle
        size = len(board)
        block = int(size ** 0.5)
        # flatten board
        board = [n for row in board for n in row]

        def build_span(_size, _block):
            span_dict = {}
            for p in range(_size * _size):
                for n in range(_size + 1):
                    if n != 0:
                        tmp = (
                            p // _size,
                            _size + p % _size,
                            2 * _size + p % _size // _block + p // _size // _block * _block
                        )
                        set_tmp = set()
                        for g in tmp:
                            set_tmp.add((g, n))

                        span_dict[(n, p)] = set_tmp
                    else:
                        span_dict[(n, p)] = set()
            return span_dict

        span = build_span(size, block)
        empties = [i for i, n in enumerate(board) if n == 0]
        used = set().union(*(span[n, p] for p, n in enumerate(board) if n))
        empty = 0
        while empty >= 0 and empty < len(empties):
            pos = empties[empty]
            used -= span[board[pos], pos]
            board[pos] = next((n for n in range(board[pos] + 1, size + 1) if not span[n, pos] & used), 0)
            used |= span[board[pos], pos]
            empty += 1 if board[pos] else -1
            if empty == len(empties):
                solution = [board[r:r + size] for r in range(0, size * size, size)]
                yield solution
                empty -= 1

    def build_puzzle(self):
        """

        :return: puzzle with only 1 solution
        """

        solution = self.board
        # init puzzlewith 75% of the fields cleared from the solution
        puzzle = self._clear_board()
        while True:
            solved = [*islice(self._solve(puzzle), 2)]
            if len(solved) == 1: break
            diffPos = [(r, c) for r in range(9) for c in range(9)
                       if solved[0][r][c] != solved[1][r][c]]
            r, c = choice(diffPos)
            puzzle[r][c] = solution[r][c]

        return puzzle


    def _pretty_print(self, board):
        def expandLine(line):
            return line[0] + line[5:9].join([line[1:5] * (self.base - 1)] * self.base) + line[9:13]

        line0 = expandLine("╔═══╤═══╦═══╗")
        line1 = expandLine("║ . │ . ║ . ║")
        line2 = expandLine("╟───┼───╫───╢")
        line3 = expandLine("╠═══╪═══╬═══╣")
        line4 = expandLine("╚═══╧═══╩═══╝")

        symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        nums = [[""] + [symbol[n] for n in row] for row in board]
        print(line0)
        for r in range(1, self.side + 1):
            print("".join(n + s for n, s in zip(nums[r - 1], line1.split("."))))
            print([line2, line3, line4][(r % self.side == 0) + (r % self.base == 0)])

    def pretty_print_solution(self):
        self._pretty_print(self.board)

    def pretty_print_puzzle(self):
        self._pretty_print(self.puzzle)


if __name__ == '__main__':
    puz = Sudoku(3)
    puz.build_puzzle()
    puz.pretty_print_solution()
    print('ok')
    puz.pretty_print_puzzle()


