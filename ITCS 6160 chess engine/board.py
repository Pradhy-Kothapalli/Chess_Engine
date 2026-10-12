import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import chess
import chess_engine

BOARD_SIZE = 8
SQUARE_SIZE = 80

PIECES = {}

def load_images():
    pieces = [
        "wp","wn","wb","wr","wq","wk",
        "bp","bn","bb","br","bq","bk"
    ]
    for p in pieces:
        img = Image.open(f"pieces/{p}.png")
        img = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.LANCZOS)
        PIECES[p] = ImageTk.PhotoImage(img)

class ChessGUI:
    def __init__(self, master):
        self.master = master
        master.title("My Alpha-Beta Chess Engine")
        
        self.canvas = tk.Canvas(master, width=640, height=640)
        self.canvas.pack()

        self.board = chess.Board()
        self.selected_square = None
        self.highlight_moves = []

        self.draw_board()
        self.draw_pieces()

        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("square")
        colors = ["#f0d9b5", "#b58863"]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = c * SQUARE_SIZE
                y1 = r * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = colors[(r + c) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")

        for sq in self.highlight_moves:
            r = 7 - chess.square_rank(sq)
            c = chess.square_file(sq)
            x1 = c * SQUARE_SIZE
            y1 = r * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=4)

    def draw_pieces(self):
        self.canvas.delete("piece")
        for sq, piece in self.board.piece_map().items():
            r = 7 - chess.square_rank(sq)
            c = chess.square_file(sq)
            x = c * SQUARE_SIZE
            y = r * SQUARE_SIZE
            key = ("w" if piece.color else "b") + piece.symbol().lower()
            self.canvas.create_image(x, y, anchor="nw", image=PIECES[key], tags="piece")

    def ask_promotion(self):
        win = tk.Toplevel(self.master)
        win.title("Promote to")
        win.geometry("200x120")
        choice = tk.StringVar(value="q")

        def set_piece(p):
            choice.set(p)
            win.destroy()

        tk.Button(win, text="Queen",  command=lambda: set_piece("q")).pack(fill="x")
        tk.Button(win, text="Rook",   command=lambda: set_piece("r")).pack(fill="x")
        tk.Button(win, text="Bishop", command=lambda: set_piece("b")).pack(fill="x")
        tk.Button(win, text="Knight", command=lambda: set_piece("n")).pack(fill="x")

        win.wait_window()
        return choice.get()

    def on_click(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        square = chess.square(col, 7 - row)

        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlight_moves = [
                    m.to_square for m in self.board.legal_moves if m.from_square == square
                ]
            self.refresh()
            return

        from_sq = self.selected_square
        to_sq = square
        moving_piece = self.board.piece_at(from_sq)

        move = None

        if moving_piece and moving_piece.piece_type == chess.PAWN:
            rank = chess.square_rank(to_sq)
            if rank == 0 or rank == 7:
                promo = self.ask_promotion()
                if promo:
                    move = chess.Move(
                        from_sq,
                        to_sq,
                        promotion={
                            'q': chess.QUEEN,
                            'r': chess.ROOK,
                            'b': chess.BISHOP,
                            'n': chess.KNIGHT
                        }[promo]
                    )

        if move is None:
            move = chess.Move(from_sq, to_sq)

        if move in self.board.legal_moves:
            self.board.push(move)
            self.selected_square = None
            self.highlight_moves = []
            self.refresh()
            self.master.after(200, self.engine_move)
            return

        self.selected_square = None
        self.highlight_moves = []
        self.refresh()

    def engine_move(self):
        if self.board.is_game_over():
            messagebox.showinfo("Game Over", str(self.board.result()))
            return

        move = chess_engine.choose_best_move(self.board, max_depth=4)
        if move is None:
            messagebox.showinfo("Game Over", "No legal moves.")
            return

        self.board.push(move)
        self.refresh()

        if self.board.is_game_over():
            messagebox.showinfo("Game Over", str(self.board.result()))

    def refresh(self):
        self.draw_board()
        self.draw_pieces()

def main():
    root = tk.Tk()
    load_images()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
