import chess
import math
import time
# The value of each piece (in centipawns)
# The knight is equal to bishops in most positions but bishops are still slightly more valuable at higher levels
PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   0, 
}
# Trying to represent how good a piece is on each square of an empty board(Knights are best in the center, Kings are safest when castled etc.)
PAWN_TABLE = [ 
      0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 30, 30, 20, 10, 10,
      5,  5, 10, 25, 25, 10,  5,  5,
      0,  0,  0, 20, 20,  0,  0,  0,
      5, -5,-10,  0,  0,-10, -5,  5,
      5, 10, 10,-20,-20, 10, 10,  5,
      0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  5, 10, 10,  5,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5, 10,  5,  5, 10,  5,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5, 10,  5,  5, 10,  5,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 10, 30,  0,  0, 10, 30, 20,
]

#This maps each piece type to its corresponding piece-square table.Part of evaluation when trying to find the best move
PSQT = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}
# Some general heuristic bonuses(Good to have double bishops, rooks on open files, bad to have doubled or isolated pawns, etc.)
BISHOP_PAIR_BONUS = 30
ROOK_OPEN_FILE_BONUS = 25
PASSED_PAWN_BONUS = [0, 5, 10, 20, 40, 70, 120, 200]
ISOLATED_PAWN_PENALTY = 15
DOUBLED_PAWN_PENALTY = 12
MOBILITY_FACTOR = 1 # Each legal move
CASTLING_BONUS = 50

# Checks if a pawn is a passes pawn
def is_passed(board, sq, color):
    file = chess.square_file(sq) # Gets the file of the pawn 
    rank = chess.square_rank(sq)
    enemy = not color # If the player is playing white, then the enemy is playing black

    # For a pawn to be considered passed, it cannot be captured or blocked by another pawn.
    # This loop iterates over the file of the pawn and the 2 files before and after to check for opponent pawns
    for df in [-1, 0, 1]:
        f = file + df
        if 0 <= f <= 7:
            for r in range(rank + 1, 8):
                if chess.square(f, r) in board.pieces(chess.PAWN, enemy):
                    return False
    return True

# This is the main evaluation function
def evaluate(board):
    # First, find if it is checkmate or stalemate or if there is insufficient material
    if board.is_checkmate():
        return -999999 if board.turn == chess.WHITE else 999999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0 # Initialize the eval score(currently equal)


    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    wkf = chess.square_file(wk)
    wkr = chess.square_rank(wk)
    bkf = chess.square_file(bk)
    bkr = chess.square_rank(bk)
    # If the king is either on the b file or the g file then the king is likely castled 
    # so we either add(for white) or subtract(for black) the castling bonus
    if wkr == 0 and (wkf == 6 or wkf == 2):
        score += CASTLING_BONUS
    if bkr == 7 and (bkf == 6 or bkf == 2):
        score -= CASTLING_BONUS

    # This adds/subtracts the material advantage and/or positional bonuses(Heuristic) for both sides
    for piece_type, value in PIECE_VALUES.items():
        for sq in board.pieces(piece_type, chess.WHITE):
            score += value
            score += PSQT[piece_type][sq]
        for sq in board.pieces(piece_type, chess.BLACK):
            score -= value
            score -= PSQT[piece_type][chess.square_mirror(sq)]
    # Bishop pair bonus
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += BISHOP_PAIR_BONUS
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= BISHOP_PAIR_BONUS

    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    files_white = [0] * 8
    files_black = [0] * 8

    for sq in white_pawns:
        files_white[chess.square_file(sq)] += 1
    for sq in black_pawns:
        files_black[chess.square_file(sq)] += 1
    # Double pawn penalty
    for count in files_white:
        if count > 1:
            score -= DOUBLED_PAWN_PENALTY * (count - 1)
    for count in files_black:
        if count > 1:
            score += DOUBLED_PAWN_PENALTY * (count - 1)
    # Isolated pawn penalty
    for file in range(8):
        if files_white[file] > 0:
            if (file == 0 or files_white[file-1] == 0) and \
               (file == 7 or files_white[file+1] == 0):
                score -= ISOLATED_PAWN_PENALTY
        if files_black[file] > 0:
            if (file == 0 or files_black[file-1] == 0) and \
               (file == 7 or files_black[file+1] == 0):
                score += ISOLATED_PAWN_PENALTY
    # Passed pawn bonus
    for sq in white_pawns:
        if is_passed(board, sq, chess.WHITE):
            rank = chess.square_rank(sq)
            score += PASSED_PAWN_BONUS[rank]
    for sq in black_pawns:
        if is_passed(board, sq, chess.BLACK):
            rank = 7 - chess.square_rank(sq)
            score -= PASSED_PAWN_BONUS[rank]

    score += len(list(board.legal_moves)) * MOBILITY_FACTOR * (1 if board.turn else -1)

    # The engine scores from white's prespective so if it is black to move, the we return the negation of the score
    return score if board.turn == chess.WHITE else -score

INF = 10**9 # Very large number to set to infinity during alpha beta pruning
TT = {} # This is a transposition table so we don't need to check the same position that may occur by playing a different move order
KILLER = [[None, None] for _ in range(100)] # This is the beta cutoff (the best move) so everything else is irrelevant(Dont need to see how good it is)
HISTORY = {} # Giving priority to moves that may be good in many positions

# How good is a move so I can search it first
def move_order(board, move, depth):
    score = 0
    # First check for en_passant (Very rare but a forcing move)
    if board.is_en_passant(move):
        score += 10000 + PIECE_VALUES[chess.PAWN] * 10
    # Next, we need to look for captures(also very forcing)
    elif board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        v = PIECE_VALUES.get(victim.piece_type, 0) if victim else 0 # the piece being captured
        a = PIECE_VALUES.get(attacker.piece_type, 1) if attacker else 1 # the piece that is capturing
        score += 10000 + v * 10 - a # Most valuable victim - least valuable attacker(MVV–LVA heuristic)

    # promotion gets the highest priority, then checks, then castles, then killer move and the backup and then the "historically" good move
    if move.promotion:
        score += 8000
    if board.gives_check(move):
        score += 5000
    if board.is_castling(move):
        score += 9000
    if move == KILLER[depth][0]:
        score += 9000
    if move == KILLER[depth][1]:
        score += 8000
    score += HISTORY.get((board.turn, move.from_square, move.to_square), 0)
    return score


# Typically, since alpha beta pruning has a search limit, we might reach a position where the very next move hangs material(Or simple tactics)
# the goal of quiescence is to try to limit these mistakes by looking at forced moves even after the depth limit is reached
def quiescence(board, alpha, beta):
    stand_pat = evaluate(board)
    # if the current eval is too good for beta to allow, just return beta(no need to look more)
    if stand_pat >= beta:
        return beta
    # If the current eval is higher than alpha, then raise alpha since we have a new best score for the current player
    if stand_pat > alpha:
        alpha = stand_pat
    # Only check for captures(or enpassant)
    for move in board.legal_moves:
        if not (board.is_capture(move) or board.is_en_passant(move)):
            continue
        board.push(move) # make the capture
        score = -quiescence(board, -beta, -alpha) # swap alpha and beta and negate the returned score since it is now the opponents turn
        board.pop() # backtrack
        #If the capture is already too good for the opponent to allow thenr return beta
        if score >= beta:
            return beta
        # If we find a better continuation than current alpha, then update alpha, and store this as best seen so far
        if score > alpha:
            alpha = score
    return alpha



def alphabeta(board, depth, alpha, beta):
    key = (board._transposition_key(), depth) # create a Zobrist hash(typically used for chess and go)
    # If we already evaluated this position before, then used the cached result, dont need to reevaluate the same position
    if key in TT:
        return TT[key] #T Table hit

    # Once the base case is reached, use quiescence and make sure there is nothing being missed on the move right after.
    if depth == 0:
        return quiescence(board, alpha, beta), None

    best_score = -INF # Initial best score so far
    best_move = None

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_order(board, m, depth), reverse=True) #sort the board by move order

    for move in moves:
        board.push(move)
        # Recursively search the position after the move.
        # Use negamax, invert alpha and beta for opponent's perspective.
        score, _ = alphabeta(board, depth - 1, -beta, -alpha)
        # Negate score because we switched perspectives
        score = -score
        # Undo the move to restore original board state
        board.pop()
        # If this move gives a better score than anything seen so far, update best_score and best_move
        if score > best_score:
            best_score = score
            best_move = move
        # If this move improves alpha (best score for current player), then update alpha
        if score > alpha:
            alpha = score
            KILLER[depth][1] = KILLER[depth][0]
            KILLER[depth][0] = move
            #Update history heuristic: Moves that frequently improve alpha(moves that are good in multiple positions) get a higher history score. 
            # depth*depth rewards deep-node cutoffs more strongly.
            HISTORY[(board.turn, move.from_square, move.to_square)] = \
                HISTORY.get((board.turn, move.from_square, move.to_square), 0) + depth * depth

        if alpha >= beta:
            break

    TT[key] = (best_score, best_move) #cache this positions result in the transposition table
    return best_score, best_move

def choose_best_move(board, max_depth=4):
    best_move = None
    # Use IDS to call alpha-beta at every depth
    for d in range(1, max_depth + 1):
        score, move = alphabeta(board, d, -INF, INF)
        # If a legal move was returned by alpha-beta, update best_move
        # Higher depths overwrite shallower results, which stabilizes the move choice
        if move:
            best_move = move
    return best_move


def play_vs_engine(depth=4, engine_plays_white=True):
    board = chess.Board()

    print("Starting game:")
    print(board)

    while not board.is_game_over():
        engine_turn = (board.turn == chess.WHITE) == engine_plays_white

        if engine_turn:
            print("\nEngine thinking...")
            move = choose_best_move(board, max_depth=depth)
            print("Engine plays:", move)
            board.push(move)
        else:
            print("\nYour move:")
            print(board)
            user_move = input("Enter move (uci): ").strip()
            try:
                mv = chess.Move.from_uci(user_move)
                if mv in board.legal_moves:
                    board.push(mv)
                else:
                    print("Illegal! Try again.")
            except:
                print("Invalid.")

    print("\nGame over:", board.result())


if __name__ == "__main__":
    play_vs_engine(depth=4, engine_plays_white=True)
