import pygame, copy, random, time, pickle

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = 75
MARGIN = 20

GREEN = (0,128,0)
BLACK = (0,0,0)
BACKGROUND = (128,0,128)
HIGHLIGHT = (255,255,0)
RED = (200,0,0)
BLUE = (0,0,200)
WHITE = (255,255,255)
ORANGE = (255,165,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

selected_piece = None
valid_moves = []
current_turn = "RED"
winner = None
chain_capture = False
move_count = 0
history = []
history_index = 0
AI_ENABLED = True
SMART_AI = True
last_move = None
red_score = 0
blue_score = 0
turn_start_time = time.time()
TURN_LIMIT = 10
hint_move = None
paused = False

# NEW: move log
move_log = []

replay_mode = False
replay_index = 0
replay_timer = 0
REPLAY_DELAY = 500

animating = False
anim_piece = None
anim_start = None
anim_end = None
anim_progress = 0
ANIM_SPEED = 0.2

def reset_game():
    return {(0,0):("RED",False),(1,1):("RED",False),(6,6):("BLUE",False),(7,7):("BLUE",False)}

pieces = reset_game()
history = [copy.deepcopy(pieces)]
history_index = 0

def save_game():
    data = {
        "pieces": pieces,
        "history": history,
        "history_index": history_index,
        "current_turn": current_turn,
        "red_score": red_score,
        "blue_score": blue_score
    }
    with open("savegame.pkl", "wb") as f:
        pickle.dump(data, f)

def load_game():
    global pieces, history, history_index, current_turn, red_score, blue_score
    try:
        with open("savegame.pkl", "rb") as f:
            data = pickle.load(f)
            pieces = data["pieces"]
            history = data["history"]
            history_index = data["history_index"]
            current_turn = data["current_turn"]
            red_score = data["red_score"]
            blue_score = data["blue_score"]
    except:
        pass

def undo_move():
    global history_index, pieces, current_turn, turn_start_time, hint_move, move_log
    if history_index > 0:
        history_index -= 1
        pieces = copy.deepcopy(history[history_index])
        switch_turn()
        turn_start_time = time.time()
        hint_move = None

        if move_log:
            move_log.pop()

def redo_move():
    global history_index, pieces, current_turn, turn_start_time, hint_move, move_log
    if history_index < len(history) - 1:
        history_index += 1
        pieces = copy.deepcopy(history[history_index])
        switch_turn()
        turn_start_time = time.time()
        hint_move = None

        # rebuild move log
        move_log.clear()
        for i in range(1, history_index + 1):
            prev = history[i-1]
            curr = history[i]

            start = None
            end = None

            for pos in curr:
                if pos not in prev:
                    end = pos
            for pos in prev:
                if pos not in curr:
                    start = pos

            if start and end:
                move_log.append((start, end))

def player_has_capture(player):
    for pos, (o, _) in pieces.items():
        if o == player:
            moves = get_valid_moves_basic(pos)
            for m in moves[1]:
                return True
    return False

def get_valid_moves_basic(pos):
    row, col = pos
    owner, is_king = pieces[pos]
    moves, captures = [], []

    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    if is_king:
        directions += [(-1,-1),(-1,1),(1,-1),(1,1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        if 0 <= r < ROWS and 0 <= c < COLS and (r,c) not in pieces:
            moves.append((r,c))

        jr, jc = row + 2*dr, col + 2*dc
        mid = (row + dr, col + dc)

        if 0 <= jr < ROWS and 0 <= jc < COLS:
            if mid in pieces and pieces[mid][0] != owner and (jr,jc) not in pieces:
                captures.append((jr,jc))

    return moves, captures

def get_valid_moves(pos):
    moves, captures = get_valid_moves_basic(pos)
    owner = pieces[pos][0]
    if player_has_capture(owner):
        return captures
    return captures if captures else moves

def get_captured_piece(s,e):
    if abs(s[0]-e[0])==2 or abs(s[1]-e[1])==2:
        return ((s[0]+e[0])//2,(s[1]+e[1])//2)

def promote(pos):
    r,_ = pos
    o,k = pieces[pos]
    if (o=="RED" and r==ROWS-1) or (o=="BLUE" and r==0):
        pieces[pos]=(o,True)

def apply_move(s,e):
    global red_score,blue_score,last_move,hint_move,history,history_index
    global animating, anim_piece, anim_start, anim_end, anim_progress, move_log

    animating = True
    anim_piece = pieces[s]
    anim_start = s
    anim_end = e
    anim_progress = 0

    c = get_captured_piece(s,e)
    if c:
        if pieces[c][0]=="RED": blue_score+=1
        else: red_score+=1
        pieces.pop(c)

    o,k = pieces[s]
    pieces[e]=(o,k)
    pieces.pop(s)
    promote(e)

    last_move=(s,e)
    hint_move=None

    # NEW: log move
    move_log.append((s, e))
    if len(move_log) > 20:
        move_log.pop(0)

    history = history[:history_index+1]
    history.append(copy.deepcopy(pieces))
    history_index += 1

    return c

def switch_turn():
    global current_turn,selected_piece,valid_moves,chain_capture,move_count,turn_start_time,hint_move
    current_turn="BLUE" if current_turn=="RED" else "RED"
    selected_piece=None
    valid_moves=[]
    chain_capture=False
    move_count+=1
    turn_start_time=time.time()
    hint_move=None

def draw_move_log():
    x_offset = 600
    y_offset = 120

    title = font.render("Moves:", True, WHITE)
    screen.blit(title, (x_offset, y_offset - 30))

    for i, (s, e) in enumerate(move_log[-10:]):
        symbol = "x" if abs(s[0]-e[0]) == 2 or abs(s[1]-e[1]) == 2 else "->"
        text = font.render(f"{s} {symbol} {e}", True, WHITE)
        screen.blit(text, (x_offset, y_offset + i * 25))
