import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class ChessPiece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.setup_board()

    def setup_board(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = ChessPiece('white', 'pawn')
            self.board[6][col] = ChessPiece('black', 'pawn')

        # Set up other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col, piece_type in enumerate(piece_order):
            self.board[0][col] = ChessPiece('white', piece_type)
            self.board[7][col] = ChessPiece('black', piece_type)

    def is_valid_move(self, start, end):
        # This is a basic move validation. In a real chess game, you'd need more complex rules.
        piece = self.board[start[0]][start[1]]
        if piece is None or piece.color != self.current_player:
            return False
        if self.board[end[0]][end[1]] is not None and self.board[end[0]][end[1]].color == self.current_player:
            return False
        # Add more specific rules for each piece type here
        return True

    def move_piece(self, start, end):
        if self.is_valid_move(start, end):
            piece = self.board[start[0]][start[1]]
            self.board[end[0]][end[1]] = piece
            self.board[start[0]][start[1]] = None
            self.current_player = 'black' if self.current_player == 'white' else 'white'
            return True
        return False

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game")
        self.chess_board = ChessBoard()
        self.selected_piece = None
        self.setup_board()
        self.create_info_frame()

    def setup_board(self):
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.images = {}  # Store images to prevent garbage collection

        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                button = tk.Button(self.board_frame, bg=color, width=5, height=2,
                                   command=lambda r=row, c=col: self.on_square_click(r, c))
                button.grid(row=7-row, column=col)  # Invert row to correct board orientation
                self.buttons[row][col] = button

        self.load_pieces()
        self.update_board()

    def create_info_frame(self):
        self.info_frame = tk.Frame(self.master)
        self.info_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.turn_label = tk.Label(self.info_frame, text="Current turn: White")
        self.turn_label.pack()

        self.reset_button = tk.Button(self.info_frame, text="Reset Game", command=self.reset_game)
        self.reset_button.pack()

    def load_pieces(self):
        piece_images = {
            'white_pawn': 'wp.png', 'white_rook': 'wr.png', 'white_knight': 'wn.png',
            'white_bishop': 'wb.png', 'white_queen': 'wq.png', 'white_king': 'wk.png',
            'black_pawn': 'bp.png', 'black_rook': 'br.png', 'black_knight': 'bn.png',
            'black_bishop': 'bb.png', 'black_queen': 'bq.png', 'black_king': 'bk.png'
        }

        for piece, filename in piece_images.items():
            try:
                image = Image.open(f"chess_pieces/{filename}")
                image = image.resize((40, 40), Image.LANCZOS)
                self.images[piece] = ImageTk.PhotoImage(image)
            except FileNotFoundError:
                print(f"Warning: Image file {filename} not found.")
                self.images[piece] = None

    def update_board(self):
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.board[row][col]
                if piece:
                    image_key = f"{piece.color}_{piece.piece_type}"
                    self.buttons[row][col].config(image=self.images[image_key])
                else:
                    self.buttons[row][col].config(image="")
        self.turn_label.config(text=f"Current turn: {self.chess_board.current_player.capitalize()}")

    def on_square_click(self, row, col):
        if self.selected_piece is None:
            if self.chess_board.board[row][col] is not None:
                if self.chess_board.board[row][col].color == self.chess_board.current_player:
                    self.selected_piece = (row, col)
                    self.buttons[row][col].config(relief=tk.SUNKEN)
        else:
            start_row, start_col = self.selected_piece
            self.buttons[start_row][start_col].config(relief=tk.RAISED)
            if (row, col) != self.selected_piece:
                if self.chess_board.move_piece(self.selected_piece, (row, col)):
                    self.update_board()
                    if self.check_game_over():
                        self.show_game_over()
                else:
                    messagebox.showwarning("Invalid Move", "That move is not allowed.")
            self.selected_piece = None

    def check_game_over(self):
        # This is a placeholder. In a real chess game, you'd need to implement
        # checkmate and stalemate detection.
        return False

    def show_game_over(self):
        winner = "Black" if self.chess_board.current_player == "white" else "White"
        messagebox.showinfo("Game Over", f"{winner} wins!")

    def reset_game(self):
        self.chess_board = ChessBoard()
        self.selected_piece = None
        self.update_board()

def main():
    root = tk.Tk()
    chess_gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    