import tkinter as tk
from tkinter import messagebox
import copy
import math

# ---------------------------
# Constants and Global Config
# ---------------------------
CELL_SIZE = 60          # Size of a single cell in pixels.
BOARD_PADDING = 5       # Padding between small boards.
SMALL_BOARD_SIZE = 3    # 3x3 small boards.
GLOBAL_BOARD_SIZE = 3   # 3x3 grid of small boards.

# Players
HUMAN = 'X'
AI = 'O'

# AI search parameter: increasing depth makes the AI stronger.
SEARCH_DEPTH = 5

# Dark mode colors and fonts (Material inspired)
BG_COLOR = "#121212"              # Main window background.
CANVAS_BG = "#1e1e1e"             # Canvas background.
HIGHLIGHT_COLOR = "#2a82da"       # Highlight for legal moves.
INACTIVE_COLOR = "#262626"        # Background for finished small boards.
TEXT_COLOR = "#eeeeee"            # Generic text color.
X_COLOR = "#ff5252"               # Color for X.
O_COLOR = "#40c4ff"               # Color for O.
DRAW_COLOR = "#9e9e9e"            # Color for drawn board text.
STATUS_FONT = ("Helvetica", 14, "bold")
MOVE_FONT = ("Arial", 24, "bold")
WIN_FONT = ("Arial", 48, "bold")  # Font for big winning mark.
SPLASH_FONT = ("Helvetica", 36, "bold")

# Animation parameters
PULSE_STEPS = 10        # Number of pulses steps for win animation.
PULSE_DELAY = 70        # Delay (ms) between steps in win animation.
SPLASH_DURATION = 2000  # Splash screen duration in ms.

# ---------------------------
# Helper Functions for CSP & Game Logic
# ---------------------------
def check_win(board):
    """Check win condition for a 3x3 board."""
    lines = []
    # Rows and columns.
    for i in range(3):
        lines.append(board[i])
        lines.append([board[r][i] for r in range(3)])
    # Diagonals.
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2-i] for i in range(3)])
    
    for line in lines:
        if line[0] is not None and all(cell == line[0] for cell in line):
            return line[0]
    return None

def board_full(board):
    return all(cell is not None for row in board for cell in row)

def global_winner(global_state):
    """Determine winner on the global board based on the small boards."""
    global_board = [[global_state[gr][gc]['winner'] for gc in range(3)] for gr in range(3)]
    return check_win(global_board)

def available_moves(state, active_board):
    """
    Return all valid moves as (G_r, G_c, L_r, L_c).
    Only cells in small boards not yet finished are allowed.
    """
    moves = []
    if active_board is not None:
        gr, gc = active_board
        if state[gr][gc]['winner'] is None:
            board = state[gr][gc]['cells']
            if not board_full(board):
                for lr in range(3):
                    for lc in range(3):
                        if board[lr][lc] is None:
                            moves.append((gr, gc, lr, lc))
                if moves:
                    return moves  # Forced moves in the active board.
    
    # Otherwise, allow any empty cell in unfinished boards.
    for gr in range(3):
        for gc in range(3):
            if state[gr][gc]['winner'] is None:
                board = state[gr][gc]['cells']
                for lr in range(3):
                    for lc in range(3):
                        if board[lr][lc] is None:
                            moves.append((gr, gc, lr, lc))
    return moves

def apply_move(state, move, player):
    """
    Apply a move to the board state.
    move: (G_r, G_c, L_r, L_c)
    Returns a tuple (new_state, next_active_board).
    """
    new_state = copy.deepcopy(state)
    gr, gc, lr, lc = move
    new_state[gr][gc]['cells'][lr][lc] = player

    board = new_state[gr][gc]['cells']
    winner = check_win(board)
    if winner:
        new_state[gr][gc]['winner'] = winner
    elif board_full(board):
        new_state[gr][gc]['winner'] = 'D'  # D for draw

    next_board = (lr, lc)
    if new_state[next_board[0]][next_board[1]]['winner'] is not None:
        next_board = None
    return new_state, next_board

def forward_check(state, move, player):
    gr, gc, lr, lc = move
    return state[gr][gc]['cells'][lr][lc] is None

def ac3(state):
    # For our case, we assume arc consistency is maintained by available_moves.
    return True

def evaluate_state(state):
    """
    Evaluate state for the minimax algorithm.
    Returns a large positive value if AI is winning, negative if HUMAN is winning.
    """
    gw = global_winner(state)
    if gw == AI:
        return 1000
    elif gw == HUMAN:
        return -1000

    score = 0
    # Simple heuristic: count the advantage of each small board.
    for gr in range(3):
        for gc in range(3):
            if state[gr][gc]['winner'] is None:
                board = state[gr][gc]['cells']
                for row in board:
                    score += row.count(AI) - row.count(HUMAN)
    return score

def game_over(state):
    return global_winner(state) is not None or len(available_moves(state, None)) == 0

# ---------------------------
# Minimax with Alpha-Beta Pruning
# ---------------------------
def minimax(state, active_board, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_over(state):
        return evaluate_state(state), None
    
    moves = available_moves(state, active_board)
    best_move = None
    
    if maximizing_player:
        max_eval = -math.inf
        for move in moves:
            if not forward_check(state, move, AI):
                continue
            new_state, next_board = apply_move(state, move, AI)
            if not ac3(new_state):
                continue
            eval_score, _ = minimax(new_state, next_board, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in moves:
            if not forward_check(state, move, HUMAN):
                continue
            new_state, next_board = apply_move(state, move, HUMAN)
            if not ac3(new_state):
                continue
            eval_score, _ = minimax(new_state, next_board, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

# ---------------------------
# Enhanced Dark Mode GUI with Animations and Material Design
# ---------------------------
class UltimateTTTGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultimate Tic-Tac-Toe")
        self.master.configure(bg=BG_COLOR)
        self.move_count = 0
        self.animating = False  # Flag to disable user interaction during animations

        # Splash screen
        self.splash_frame = tk.Frame(self.master, bg=BG_COLOR)
        self.splash_frame.pack(expand=True, fill=tk.BOTH)
        self.splash_label = tk.Label(self.splash_frame, text="", font=SPLASH_FONT, fg=HIGHLIGHT_COLOR, bg=BG_COLOR)
        self.splash_label.pack(expand=True)
        self.splash_text = "Ultimate Tic-Tac-Toe"
        self.splash_index = 0

        # Start splash animation
        self.animate_splash()

    def animate_splash(self):
        # Animate the title by revealing one letter at a time.
        if self.splash_index <= len(self.splash_text):
            self.splash_label.config(text=self.splash_text[:self.splash_index])
            self.splash_index += 1
            self.master.after(150, self.animate_splash)
        else:
            # After the splash, wait a moment then start the main UI.
            self.master.after(SPLASH_DURATION, self.start_main_ui)

    def start_main_ui(self):
        # Destroy the splash frame and build the main UI.
        self.splash_frame.destroy()
        self.build_ui()
        self.init_game_state()
        self.active_board = None  # Free move initially.
        self.turn = HUMAN         # Human starts.
        self.update_status()
        self.draw_board()

    def build_ui(self):
        # Build status panel with buttons.
        self.status_frame = tk.Frame(self.master, bg=BG_COLOR)
        self.status_frame.pack(pady=10)
        self.status_label = tk.Label(self.status_frame, text="Welcome to Ultimate Tic-Tac-Toe!", 
                                     font=STATUS_FONT, fg=TEXT_COLOR, bg=BG_COLOR)
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.restart_button = tk.Button(self.status_frame, text="Restart", font=STATUS_FONT, 
                                        command=self.restart_game, bg="#333333", fg=TEXT_COLOR, relief=tk.FLAT, padx=10, pady=5)
        self.restart_button.pack(side=tk.LEFT, padx=5)
        self.quit_button = tk.Button(self.status_frame, text="Quit", font=STATUS_FONT, 
                                     command=self.master.quit, bg="#333333", fg=TEXT_COLOR, relief=tk.FLAT, padx=10, pady=5)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # Create the canvas.
        canvas_width = CELL_SIZE * SMALL_BOARD_SIZE * GLOBAL_BOARD_SIZE + BOARD_PADDING * 4
        canvas_height = CELL_SIZE * SMALL_BOARD_SIZE * GLOBAL_BOARD_SIZE + BOARD_PADDING * 4
        self.canvas = tk.Canvas(self.master, width=canvas_width, height=canvas_height, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

    def init_game_state(self):
        """Initialize the game state as a 3x3 grid of small boards."""
        self.state = []
        for _ in range(3):
            row = []
            for _ in range(3):
                board = {
                    'cells': [[None for _ in range(3)] for _ in range(3)],
                    'winner': None
                }
                row.append(board)
            self.state.append(row)

    def draw_board(self):
        self.canvas.delete("all")
        # Iterate over each small board.
        for gr in range(3):
            for gc in range(3):
                offset_x = gc * (CELL_SIZE * SMALL_BOARD_SIZE + BOARD_PADDING)
                offset_y = gr * (CELL_SIZE * SMALL_BOARD_SIZE + BOARD_PADDING)
                
                board_status = self.state[gr][gc]['winner']
                if board_status is not None:
                    # Draw a filled rectangle for finished board.
                    self.canvas.create_rectangle(offset_x, offset_y, offset_x + CELL_SIZE*3, offset_y + CELL_SIZE*3,
                                                 fill=INACTIVE_COLOR, outline="black", width=2)
                    # Determine the mark and color.
                    if board_status in (HUMAN, AI):
                        mark = board_status
                        mark_color = X_COLOR if mark == HUMAN else O_COLOR
                    else:
                        mark = "D"
                        mark_color = DRAW_COLOR
                    # Start win animation for this block.
                    self.animate_win_block(offset_x, offset_y, mark, mark_color, step=0)
                else:
                    # Normal cells.
                    for lr in range(3):
                        for lc in range(3):
                            x1 = offset_x + lc * CELL_SIZE
                            y1 = offset_y + lr * CELL_SIZE
                            x2 = x1 + CELL_SIZE
                            y2 = y1 + CELL_SIZE
                            tag = f"cell_{gr}_{gc}_{lr}_{lc}"

                            if (self.active_board is None or (self.active_board == (gr, gc))) and \
                               self.state[gr][gc]['cells'][lr][lc] is None:
                                fill_color = HIGHLIGHT_COLOR
                            else:
                                fill_color = CANVAS_BG
                            
                            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#444444", width=1, tags=tag)
                            
                            mark = self.state[gr][gc]['cells'][lr][lc]
                            if mark:
                                mark_color = X_COLOR if mark == HUMAN else O_COLOR
                                self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=mark, font=MOVE_FONT, fill=mark_color)
                
                self.canvas.create_rectangle(offset_x, offset_y,
                                             offset_x + CELL_SIZE * SMALL_BOARD_SIZE,
                                             offset_y + CELL_SIZE * SMALL_BOARD_SIZE,
                                             outline="#777777", width=2)
        margin = BOARD_PADDING // 2
        self.canvas.create_rectangle(margin, margin,
                                     self.canvas.winfo_width()-margin,
                                     self.canvas.winfo_height()-margin, outline="#bbbbbb", width=4)

    def animate_win_block(self, offset_x, offset_y, mark, mark_color, step):
        """Animate the winning block: a pulsing effect for the big mark."""
        # Calculate a scale factor (pulsing between 1.0 and 1.2).
        factor = 1.0 + 0.2 * math.sin((step / PULSE_STEPS) * math.pi)
        width = CELL_SIZE * SMALL_BOARD_SIZE
        height = CELL_SIZE * SMALL_BOARD_SIZE
        center_x = offset_x + width // 2
        center_y = offset_y + height // 2
        # Clear and redraw this block with scaled text.
        self.canvas.create_rectangle(offset_x, offset_y, offset_x + width, offset_y + height,
                                     fill=INACTIVE_COLOR, outline="black", width=2)
        self.canvas.create_text(center_x, center_y, text=mark, font=(WIN_FONT[0], int(WIN_FONT[1]*factor), WIN_FONT[2]),
                                fill=mark_color, tags="win_anim")
        if step < PULSE_STEPS:
            self.master.after(PULSE_DELAY, self.animate_win_block, offset_x, offset_y, mark, mark_color, step+1)
        else:
            # Final static drawing for the block.
            self.canvas.delete("win_anim")
            self.canvas.create_rectangle(offset_x, offset_y, offset_x + width, offset_y + height,
                                         fill=INACTIVE_COLOR, outline="black", width=2)
            self.canvas.create_text(center_x, center_y, text=mark, font=WIN_FONT, fill=mark_color)

    def update_status(self):
        """Update the status label with move count and current turn."""
        status_text = f"Moves: {self.move_count}    "
        if self.turn == HUMAN:
            status_text += "Your Turn (X)"
        else:
            status_text += "AI's Turn (O)"
        self.status_label.config(text=status_text)

    def on_click(self, event):
        if self.animating:
            return  # ignore clicks during animations
        x, y = event.x, event.y
        for gr in range(3):
            for gc in range(3):
                offset_x = gc * (CELL_SIZE * SMALL_BOARD_SIZE + BOARD_PADDING)
                offset_y = gr * (CELL_SIZE * SMALL_BOARD_SIZE + BOARD_PADDING)
                for lr in range(3):
                    for lc in range(3):
                        x1 = offset_x + lc * CELL_SIZE
                        y1 = offset_y + lr * CELL_SIZE
                        x2 = x1 + CELL_SIZE
                        y2 = y1 + CELL_SIZE
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            move = (gr, gc, lr, lc)
                            if move in available_moves(self.state, self.active_board):
                                self.make_move(move, HUMAN)
                            else:
                                messagebox.showinfo("Illegal Move", "That move is not allowed!")
                            return

    def make_move(self, move, player):
        if self.animating:
            return
        self.state, self.active_board = apply_move(self.state, move, player)
        self.move_count += 1
        self.turn = AI if player == HUMAN else HUMAN
        self.draw_board()
        self.update_status()

        winner = global_winner(self.state)
        if winner:
            self.status_label.config(text=f"Game Over: {winner} wins!")
            messagebox.showinfo("Game Over", f"Player {winner} wins the game!")
            return
        
        if len(available_moves(self.state, self.active_board)) == 0:
            self.status_label.config(text="Game Over: Draw!")
            messagebox.showinfo("Game Over", "It's a draw!")
            return

        if player == HUMAN:
            self.master.after(500, self.ai_move)

    def ai_move(self):
        _, move = minimax(self.state, self.active_board, SEARCH_DEPTH, -math.inf, math.inf, True)
        if move is None:
            self.status_label.config(text="Game Over: Draw!")
            messagebox.showinfo("Game Over", "It's a draw!")
            return
        self.make_move(move, AI)

    def restart_game(self):
        """Reset the game state and GUI."""
        self.move_count = 0
        self.turn = HUMAN
        self.active_board = None
        self.init_game_state()
        self.draw_board()
        self.update_status()

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateTTTGUI(root)
    root.mainloop()
