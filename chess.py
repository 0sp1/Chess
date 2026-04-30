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
    global animating, anim_piece, anim_start, anim_end, anim_progress

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

def get_random_move(player):
    all_moves = []
    for pos, (o, _) in pieces.items():
        if o == player:
            moves = get_valid_moves(pos)
            for m in moves:
                all_moves.append((pos, m))
    return random.choice(all_moves) if all_moves else None

def draw_highlights():
    if selected_piece:
        r, c = selected_piece
        x = MARGIN + c * SQUARE_SIZE
        y = MARGIN + r * SQUARE_SIZE
        pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)
        for move in valid_moves:
            mr, mc = move
            mx = MARGIN + mc * SQUARE_SIZE + SQUARE_SIZE // 2
            my = MARGIN + mr * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, ORANGE, (mx, my), 10)

    if last_move:
        for pos in last_move:
            r, c = pos
            x = MARGIN + c * SQUARE_SIZE
            y = MARGIN + r * SQUARE_SIZE
            pygame.draw.rect(screen, WHITE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

    if hint_move:
        s, e = hint_move
        for pos in [s, e]:
            r, c = pos
            x = MARGIN + c * SQUARE_SIZE
            y = MARGIN + r * SQUARE_SIZE
            pygame.draw.rect(screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

running=True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                paused = not paused

            if event.key == pygame.K_p:
                replay_mode = not replay_mode
                replay_index = 0
                replay_timer = pygame.time.get_ticks()

            if replay_mode:
                if event.key == pygame.K_RIGHT:
                    replay_index = min(len(history)-1, replay_index+1)
                if event.key == pygame.K_LEFT:
                    replay_index = max(0, replay_index-1)

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

            if event.key == pygame.K_z and not paused and not replay_mode:
                undo_move()

            if event.key == pygame.K_y and not paused and not replay_mode:
                redo_move()

        if event.type==pygame.MOUSEBUTTONDOWN and not replay_mode and not paused and not animating:
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

    if AI_ENABLED and not paused and not replay_mode and winner is None:
        if current_turn == "BLUE":
            pygame.time.delay(300)
            move = get_hint("BLUE") if SMART_AI else get_random_move("BLUE")
            if move:
                s, e = move
                apply_move(s, e)
            switch_turn()

    if not paused and not replay_mode and winner is None:
        elapsed = time.time() - turn_start_time
        if elapsed > TURN_LIMIT:
            move = get_random_move(current_turn)
            if move:
                s, e = move
                apply_move(s, e)
            switch_turn()

    if replay_mode:
        now = pygame.time.get_ticks()
        if now - replay_timer > REPLAY_DELAY:
            replay_timer = now
            if replay_index < len(history) - 1:
                replay_index += 1

    screen.fill(BACKGROUND)

    display_pieces = history[replay_index] if replay_mode else pieces

    for r in range(ROWS):
        for c in range(COLS):
            x = MARGIN + c * SQUARE_SIZE
            y = MARGIN + r * SQUARE_SIZE
            rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(screen, GREEN if (r+c)%2==0 else BLACK, rect)

            if (r, c) in display_pieces:
                if animating and (r, c) == anim_end:
                    continue

                center = (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2)
                o, k = display_pieces[(r, c)]
                color = RED if o == "RED" else BLUE
                pygame.draw.circle(screen, color, center, SQUARE_SIZE//3)

                if k:
                    pygame.draw.circle(screen, WHITE, center, 10)

    if animating:
        sr, sc = anim_start
        er, ec = anim_end

        sx = MARGIN + sc * SQUARE_SIZE + SQUARE_SIZE//2
        sy = MARGIN + sr * SQUARE_SIZE + SQUARE_SIZE//2
        ex = MARGIN + ec * SQUARE_SIZE + SQUARE_SIZE//2
        ey = MARGIN + er * SQUARE_SIZE + SQUARE_SIZE//2

        x = sx + (ex - sx) * anim_progress
        y = sy + (ey - sy) * anim_progress

        color = RED if anim_piece[0] == "RED" else BLUE
        pygame.draw.circle(screen, color, (int(x), int(y)), SQUARE_SIZE//3)

        if anim_piece[1]:
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), 10)

        anim_progress += ANIM_SPEED

        if anim_progress >= 1:
            animating = False

    if not replay_mode:
        draw_highlights()

    if replay_mode:
        txt = font.render(f"REPLAY {replay_index+1}/{len(history)}", True, WHITE)
        screen.blit(txt, (10, 10))
    else:
        remaining = max(0, int(TURN_LIMIT - (time.time() - turn_start_time)))
        timer_text = font.render(f"Time: {remaining}", True, ORANGE)
        turn_text = font.render(f"Turn: {current_turn}", True, WHITE)
        score_text = font.render(f"RED {red_score} - {blue_score} BLUE", True, WHITE)
        screen.blit(timer_text, (650, 10))
        screen.blit(turn_text, (10, 10))
        screen.blit(score_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
