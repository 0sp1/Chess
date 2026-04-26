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

replay_mode = False
replay_index = 0

def reset_game():
    return {(0,0):("RED",False),(1,1):("RED",False),(6,6):( "BLUE",False),(7,7):( "BLUE",False)}

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
    global history_index, pieces, current_turn, turn_start_time, hint_move
    if history_index > 0:
        history_index -= 1
        pieces = copy.deepcopy(history[history_index])
        switch_turn()
        turn_start_time = time.time()
        hint_move = None

def redo_move():
    global history_index, pieces, current_turn, turn_start_time, hint_move
    if history_index < len(history) - 1:
        history_index += 1
        pieces = copy.deepcopy(history[history_index])
        switch_turn()
        turn_start_time = time.time()
        hint_move = None

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

def check_winner():
    r = any(o=="RED" for o,_ in pieces.values())
    b = any(o=="BLUE" for o,_ in pieces.values())
    if not r: return "BLUE"
    if not b: return "RED"

def evaluate_board(temp_pieces):
    score = 0
    for (r,c),(o,k) in temp_pieces.items():
        val = 3 if k else 1
        if o == "BLUE":
            score += val
        else:
            score -= val
    return score

def simulate_move(temp_pieces, s, e):
    temp = copy.deepcopy(temp_pieces)

    if abs(s[0]-e[0]) == 2 or abs(s[1]-e[1]) == 2:
        c = ((s[0]+e[0])//2, (s[1]+e[1])//2)
        if c in temp:
            temp.pop(c)

    o,k = temp[s]
    temp[e] = (o,k)
    temp.pop(s)

    if (o=="BLUE" and e[0]==0) or (o=="RED" and e[0]==7):
        temp[e] = (o,True)

    return temp

def get_moves_for_board(temp_pieces, player):
    moves = []
    for p,(o,_) in temp_pieces.items():
        if o == player:
            global pieces
            old = pieces
            pieces = temp_pieces
            m = get_valid_moves(p)
            pieces = old
            for move in m:
                moves.append((p, move))
    return moves

def minimax(temp_pieces, depth, maximizing):
    if depth == 0:
        return evaluate_board(temp_pieces)

    player = "BLUE" if maximizing else "RED"
    moves = get_moves_for_board(temp_pieces, player)

    if not moves:
        return evaluate_board(temp_pieces)

    if maximizing:
        best = -9999
        for s,e in moves:
            new_board = simulate_move(temp_pieces, s, e)
            best = max(best, minimax(new_board, depth-1, False))
        return best
    else:
        best = 9999
        for s,e in moves:
            new_board = simulate_move(temp_pieces, s, e)
            best = min(best, minimax(new_board, depth-1, True))
        return best

def get_hint(player):
    best_score = -9999 if player == "BLUE" else 9999
    best_move = None

    for p,(o,_) in pieces.items():
        if o == player:
            moves = get_valid_moves(p)
            for move in moves:
                temp = simulate_move(pieces, p, move)
                score = minimax(temp, 2, player == "RED")

                if player == "BLUE":
                    if score > best_score:
                        best_score = score
                        best_move = (p, move)
                else:
                    if score < best_score:
                        best_score = score
                        best_move = (p, move)

    return best_move

running=True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                paused = not paused

            if paused:
                if event.key == pygame.K_s:
                    save_game()
                if event.key == pygame.K_l:
                    load_game()
                if event.key == pygame.K_r:
                    pieces = reset_game()
                    history = [copy.deepcopy(pieces)]
                    history_index = 0
                    current_turn = "RED"
                    red_score = 0
                    blue_score = 0

            if event.key==pygame.K_h and not replay_mode and not paused:
                hint_move = get_hint(current_turn)

            if event.key==pygame.K_r and not paused:
                replay_mode = not replay_mode

            if event.key == pygame.K_z and not paused:
                undo_move()

            if event.key == pygame.K_y and not paused:
                redo_move()

        if event.type==pygame.MOUSEBUTTONDOWN and not replay_mode and not paused:
            mx,my=pygame.mouse.get_pos()
            col=(mx-MARGIN)//SQUARE_SIZE
            row=(my-MARGIN)//SQUARE_SIZE
            if 0<=row<ROWS and 0<=col<COLS:
                clicked=(row,col)
                if clicked in pieces and pieces[clicked][0]==current_turn:
                    selected_piece=clicked
                    valid_moves=get_valid_moves(clicked)
                elif selected_piece and clicked in valid_moves:
                    captured = apply_move(selected_piece,clicked)

                    if captured:
                        selected_piece = clicked
                        next_moves = get_valid_moves(clicked)
                        chain_moves = [m for m in next_moves if get_captured_piece(clicked, m)]
                        if chain_moves:
                            valid_moves = chain_moves
                            continue

                    switch_turn()
                    winner=check_winner()

    if not replay_mode and not winner and not paused:
        elapsed = time.time() - turn_start_time
        remaining = max(0, TURN_LIMIT - elapsed)

        if remaining <= 0:
            auto_move = get_hint(current_turn)

            if auto_move:
                s, e = auto_move
                captured = apply_move(s, e)

                while captured:
                    next_moves = get_valid_moves(e)
                    chain_moves = [m for m in next_moves if get_captured_piece(e, m)]
                    if not chain_moves:
                        break
                    e2 = chain_moves[0]
                    captured = apply_move(e, e2)
                    e = e2

            switch_turn()
            winner = check_winner()

    screen.fill(BACKGROUND)

    for r in range(ROWS):
        for c in range(COLS):
            x = MARGIN + c * SQUARE_SIZE
            y = MARGIN + r * SQUARE_SIZE
            rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(screen, GREEN if (r+c)%2==0 else BLACK, rect)

            if selected_piece == (r, c):
                pygame.draw.rect(screen, HIGHLIGHT, rect, 4)

            if (r, c) in valid_moves:
                pygame.draw.circle(screen, ORANGE,
                                   (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), 10)

            if last_move:
                start, end = last_move
                if (r, c) == start or (r, c) == end:
                    pygame.draw.rect(screen, (0,255,255), rect, 3)

            if hint_move:
                _, hint_end = hint_move
                if (r, c) == hint_end:
                    pygame.draw.circle(screen, (0,255,0),
                                       (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), 12, 2)

            if (r, c) in pieces:
                center = (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2)
                o, k = pieces[(r, c)]
                color = RED if o == "RED" else BLUE
                pygame.draw.circle(screen, color, center, SQUARE_SIZE//3)

                if k:
                    pygame.draw.circle(screen, WHITE, center, 10)

    elapsed = time.time() - turn_start_time
    remaining = max(0, int(TURN_LIMIT - elapsed))
    timer_text = font.render(f"Time: {remaining}s", True, WHITE)
    screen.blit(timer_text, (650, 10))

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - 60, HEIGHT//2 - 100))

        instructions = [
            "ESC - Resume",
            "S - Save Game",
            "L - Load Game",
            "R - Restart"
        ]

        for i, line in enumerate(instructions):
            txt = font.render(line, True, WHITE)
            screen.blit(txt, (WIDTH//2 - 100, HEIGHT//2 - 20 + i*40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
