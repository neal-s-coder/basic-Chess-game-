import re
from typing import List, Tuple, Optional
import random

class ChessPiece:
    def __init__(self, color: str, symbol: str):
        self.color = color
        self.symbol = symbol
        self.has_moved = False

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        return True

class Pawn(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'P')
        self.en_passant_vulnerable = False

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        start_row, start_col = start
        end_row, end_col = end
        direction = 1 if self.color == 'white' else -1
        
        if start_col == end_col and board.board[end_row][end_col] is None:
            if end_row == start_row + direction:
                return True
            if not self.has_moved and end_row == start_row + 2 * direction:
                return board.board[start_row + direction][start_col] is None
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if board.board[end_row][end_col] is not None:
                return board.board[end_row][end_col].color != self.color
            # En passant
            if board.en_passant_target == (end_row - direction, end_col):
                return True
        return False

class Rook(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'R')

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        return board.is_clear_path(start, end) and (start[0] == end[0] or start[1] == end[1])

class Knight(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'N')

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        row_diff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class Bishop(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'B')

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        return board.is_clear_path(start, end) and abs(start[0] - end[0]) == abs(start[1] - end[1])

class Queen(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'Q')

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        return board.is_clear_path(start, end) and (
            start[0] == end[0] or start[1] == end[1] or abs(start[0] - end[0]) == abs(start[1] - end[1])
        )

class King(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'K')

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: 'ChessBoard') -> bool:
        row_diff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])
        
        # Normal move
        if max(row_diff, col_diff) == 1:
            return True
        
        # Castling
        if not self.has_moved and row_diff == 0 and col_diff == 2:
            rook_col = 0 if end[1] < start[1] else 7
            rook = board.board[start[0]][rook_col]
            if isinstance(rook, Rook) and not rook.has_moved:
                return board.is_clear_path(start, (start[0], rook_col)) and not board.is_king_in_check(self.color)
        
        return False

class ChessBoard:
    def __init__(self):
        self.board: List[List[Optional[ChessPiece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_player = 'white'
        self.move_history: List[str] = []
        self.en_passant_target: Optional[Tuple[int, int]] = None

    def setup_board(self):
        for col in range(8):
            self.board[1][col] = Pawn('white')
            self.board[6][col] = Pawn('black')

        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(piece_order):
            self.board[0][col] = piece_class('white')
            self.board[7][col] = piece_class('black')

    def display(self):
        print("\n  a b c d e f g h")
        for row in range(7, -1, -1):
            print(f"{row + 1} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    print(f"{piece.color[0].upper()}{piece.symbol}", end=" ")
                else:
                    print(".", end=" ")
            print(f" {row + 1}")
        print("  a b c d e f g h\n")

    def is_clear_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        row_step = 0 if start[0] == end[0] else (1 if start[0] < end[0] else -1)
        col_step = 0 if start[1] == end[1] else (1 if start[1] < end[1] else -1)
        row, col = start
        while (row, col) != end:
            row += row_step
            col += col_step
            if (row, col) != end and self.board[row][col] is not None:
                return False
        return True

    def is_king_in_check(self, color: str) -> bool:
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if piece.is_valid_move((row, col), king_pos, self):
                        return True
        return False

    def is_checkmate(self, color: str) -> bool:
        if not self.is_king_in_check(color):
            return False

        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.is_valid_move((start_row, start_col), (end_row, end_col)):
                                return False
        return True

    def is_stalemate(self, color: str) -> bool:
        if self.is_king_in_check(color):
            return False

        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.is_valid_move((start_row, start_col), (end_row, end_col)):
                                return False
        return True

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        piece = self.board[start[0]][start[1]]
        if piece is None or piece.color != self.current_player:
            return False

        if not piece.is_valid_move(start, end, self):
            return False

        # Make the move temporarily
        captured_piece = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None

        # Check if the move puts the current player in check
        in_check = self.is_king_in_check(self.current_player)

        # Undo the move
        self.board[start[0]][start[1]] = piece
        self.board[end[0]][end[1]] = captured_piece

        return not in_check

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        if not self.is_valid_move(start, end):
            return False

        piece = self.board[start[0]][start[1]]
        captured_piece = self.board[end[0]][end[1]]

        # Handle en passant capture
        if isinstance(piece, Pawn) and end == self.en_passant_target:
            captured_piece = self.board[start[0]][end[1]]
            self.board[start[0]][end[1]] = None

        # Move the piece
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None
        piece.has_moved = True

        # Handle pawn promotion
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            self.board[end[0]][end[1]] = Queen(piece.color)

        # Handle castling
        if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
            rook_start_col = 0 if end[1] < start[1] else 7
            rook_end_col = 3 if end[1] < start[1] else 5
            rook = self.board[start[0]][rook_start_col]
            self.board[start[0]][rook_end_col] = rook
            self.board[start[0]][rook_start_col] = None
            rook.has_moved = True

        # Set en passant target
        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(start[0] - end[0]) == 2:
            self.en_passant_target = (end[0] - 1 if piece.color == 'white' else end[0] + 1, end[1])

        # Record the move
        move_notation = f"{piece.symbol}{chr(start[1] + 97)}{start[0] + 1}{chr(end[1] + 97)}{end[0] + 1}"
        if captured_piece:
            move_notation += f"x{captured_piece.symbol}"
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            move_notation += "=Q"  # Pawn promotion to Queen
        self.move_history.append(move_notation)

        # Switch players
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        return True

class SimpleAI:
    def __init__(self, color: str):
        self.color = color

    def choose_move(self, board: ChessBoard) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        valid_moves = []
        for start_row in range(8):
            for start_col in range(8):
                piece = board.board[start_row][start_col]
                if piece and piece.color == self.color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if board.is_valid_move((start_row, start_col), (end_row, end_col)):
                                valid_moves.append(((start_row, start_col), (end_row, end_col)))
        return random.choice(valid_moves) if valid_moves else None

def play_chess(use_ai: bool = False):
    board = ChessBoard()
    ai = SimpleAI('black') if use_ai else None

    while True:
        board.display()
        print(f"\n{board.current_player.capitalize()}'s turn")

        if board.is_checkmate(board.current_player):
            print(f"Checkmate! {board.current_player.capitalize()} loses.")
            break
        elif board.is_stalemate(board.current_player):
            print("Stalemate! The game is a draw.")
            break

        if board.is_king_in_check(board.current_player):
            print(f"{board.current_player.capitalize()} is in check!")

        if use_ai and board.current_player == 'black':
            ai_move = ai.choose_move(board)
            if ai_move:
                start, end = ai_move
                board.move_piece(start, end)
                print(f"AI move: {board.move_history[-1]}")
            else:
                print("AI couldn't find a valid move. Game over.")
                break
        else:
            move = input("Enter your move (e.g., 'e2 e4') or 'quit' to end: ")

            if move.lower() == 'quit':
                break

            if not re.match(r'^[a-h][1-8] [a-h][1-8]$', move):
                print("Invalid input. Please use the format 'e2 e4'.")
                continue

            start, end = move.split()
            start = (int(start[1]) - 1, ord(start[0]) - ord('a'))
            end = (int(end[1]) - 1, ord(end[0]) - ord('a'))

            if board.move_piece(start, end):
                print(f"Move made: {board.move_history[-1]}")
            else:
                print("Invalid move. Try again.")

    print("Game over.")
    print("Move history:")
    for i, move in enumerate(board.move_history, 1):
        print(f"{i}. {move}")

if __name__ == "__main__":
    use_ai = input("Do you want to play against AI? (y/n): ").lower() == 'y'
    play_chess(use_ai)