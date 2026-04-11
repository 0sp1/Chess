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
big_font = pygame.font.SysFont(None, 48)

selected_piece = None
valid_moves = []
current_turn = "RED"
winner = None
chain_capture = False
move_count = 0
history = []
AI_ENABLED = True
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
    return {(0,0):("RED",False),(1,1):("RED",False),(6,6):("BLUE",False),(7,7):("BLUE",False)}

pieces = reset_game()

def get_valid_moves(pos):
    row,col = pos
    owner,_ = pieces[pos]
    moves,captures = [],[]
    for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        r,c = row+dr,col+dc
        if 0<=r<ROWS and 0<=c<COLS and (r,c) not in pieces:
            moves.append((r,c))
        jr,jc = row+2*dr,col+2*dc
        mid = (row+dr,col+dc)
        if 0<=jr<ROWS and 0<=jc<COLS:
            if mid in pieces and pieces[mid][0]!=owner and (jr,jc) not in pieces:
                captures.append((jr,jc))
    return captures if captures else moves

def get_all_captures(player):
    out=[]
    for pos,(o,_) in pieces.items():
        if o==player:
            for m in get_valid_moves(pos):
                if get_captured_piece(pos,m):
                    out.append((pos,m))
    return out

def get_captured_piece(s,e):
    if abs(s[0]-e[0])==2 or abs(s[1]-e[1])==2:
        return ((s[0]+e[0])//2,(s[1]+e[1])//2)

def promote(pos):
    r,_ = pos
    o,k = pieces[pos]
    if (o=="RED" and r==ROWS-1) or (o=="BLUE" and r==0):
        pieces[pos]=(o,True)

def check_winner():
    r = any(o=="RED" for o,_ in pieces.values())
    b = any(o=="BLUE" for o,_ in pieces.values())
    if not r: return "BLUE"
    if not b: return "RED"

def apply_move(s,e):
    global red_score,blue_score,last_move,hint_move
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

def ai_move():
    global winner
    forced = get_all_captures("BLUE")
    moves=[]
    for p,(o,_) in pieces.items():
        if o=="BLUE":
            m=get_valid_moves(p)
            if forced: m=[x for x in m if get_captured_piece(p,x)]
            for x in m: moves.append((p,x))
    if not moves: return
    moves = [m for m in moves if get_captured_piece(*m)] or moves
    s,e = random.choice(moves)
    history.append((copy.deepcopy(pieces),current_turn,move_count,chain_capture,red_score,blue_score))
    c = apply_move(s,e)
    nxt = get_valid_moves(e)
    caps = [m for m in nxt if get_captured_piece(e,m)]
    if c and caps: ai_move()
    else: switch_turn()
    winner = check_winner()

def get_hint(player):
    forced = get_all_captures(player)
    moves=[]
    for p,(o,_) in pieces.items():
        if o==player:
            m=get_valid_moves(p)
            if forced: m=[x for x in m if get_captured_piece(p,x)]
            for x in m: moves.append((p,x))
    if not moves: return
    moves = [m for m in moves if get_captured_piece(*m)] or moves
    return random.choice(moves)

def save_game():
    with open("save.dat","wb") as f:
        pickle.dump((pieces,current_turn,red_score,blue_score,move_count),f)

def load_game():
    global pieces,current_turn,red_score,blue_score,move_count
    try:
        with open("save.dat","rb") as f:
            pieces,current_turn,red_score,blue_score,move_count = pickle.load(f)
    except: pass

running=True

while running:
    if not paused and not winner and not replay_mode and time.time()-turn_start_time>TURN_LIMIT:
        switch_turn()

    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_p: paused=not paused
            if event.key==pygame.K_t:
                replay_mode = not replay_mode
                replay_index = 0
            if paused or replay_mode: continue

            if event.key==pygame.K_r:
                pieces=reset_game()
                current_turn="RED"
                history.clear()
                move_count=0
                red_score=blue_score=0
                winner=None

            if event.key==pygame.K_u and history:
                pieces,current_turn,move_count,chain_capture,red_score,blue_score = history.pop()

            if event.key==pygame.K_a: AI_ENABLED=not AI_ENABLED
            if event.key==pygame.K_h: hint_move=get_hint(current_turn)
            if event.key==pygame.K_s: save_game()
            if event.key==pygame.K_l: load_game()

        if event.type==pygame.MOUSEBUTTONDOWN and not winner and not paused and not replay_mode:
            if AI_ENABLED and current_turn=="BLUE": continue
            mx,my=pygame.mouse.get_pos()
            col=(mx-MARGIN)//SQUARE_SIZE
            row=(my-MARGIN)//SQUARE_SIZE
            if 0<=row<ROWS and 0<=col<COLS:
                clicked=(row,col)
                forced=get_all_captures(current_turn)
                if not chain_capture:
                    if clicked in pieces and pieces[clicked][0]==current_turn:
                        moves=get_valid_moves(clicked)
                        if forced: moves=[m for m in moves if get_captured_piece(clicked,m)]
                        if moves:
                            selected_piece=clicked
                            valid_moves=moves
                if selected_piece and clicked in valid_moves:
                    history.append((copy.deepcopy(pieces),current_turn,move_count,chain_capture,red_score,blue_score))
                    c=apply_move(selected_piece,clicked)
                    selected_piece=clicked
                    nxt=get_valid_moves(clicked)
                    caps=[m for m in nxt if get_captured_piece(clicked,m)]
                    if c and caps:
                        valid_moves=caps
                        chain_capture=True
                    else:
                        switch_turn()
                    winner=check_winner()

    if AI_ENABLED and current_turn=="BLUE" and not winner and not paused and not replay_mode:
        pygame.time.delay(300)
        ai_move()

    if replay_mode and history:
        replay_index = (replay_index + 1) % len(history)
        pieces = copy.deepcopy(history[replay_index][0])
        pygame.time.delay(300)

    screen.fill(BACKGROUND)

    for r in range(ROWS):
        for c in range(COLS):
            x=MARGIN+c*SQUARE_SIZE
            y=MARGIN+r*SQUARE_SIZE
            pygame.draw.rect(screen, GREEN if (r+c)%2==0 else BLACK, (x,y,SQUARE_SIZE,SQUARE_SIZE))

            if hint_move and (r,c) in hint_move:
                pygame.draw.rect(screen, ORANGE, (x,y,SQUARE_SIZE,SQUARE_SIZE),4)
            elif last_move and ((r,c)==last_move[0] or (r,c)==last_move[1]):
                pygame.draw.rect(screen, HIGHLIGHT, (x,y,SQUARE_SIZE,SQUARE_SIZE),4)
            elif selected_piece==(r,c):
                pygame.draw.rect(screen, HIGHLIGHT, (x,y,SQUARE_SIZE,SQUARE_SIZE),4)
            elif (r,c) in valid_moves:
                pygame.draw.rect(screen, BLUE, (x,y,SQUARE_SIZE,SQUARE_SIZE),4)

            if (r,c) in pieces:
                center=(x+SQUARE_SIZE//2,y+SQUARE_SIZE//2)
                o,k=pieces[(r,c)]
                pygame.draw.circle(screen, RED if o=="RED" else BLUE, center, SQUARE_SIZE//3)
                if k: pygame.draw.circle(screen, WHITE, center, SQUARE_SIZE//6)

    screen.blit(font.render(f"Turn: {current_turn}", True, WHITE), (20,5))
    screen.blit(font.render(f"Moves: {move_count}", True, WHITE), (200,5))
    screen.blit(font.render(f"{red_score}:{blue_score}", True, WHITE), (400,5))
    screen.blit(font.render(f"AI: {'ON' if AI_ENABLED else 'OFF'}", True, WHITE), (650,5))

    if paused:
        screen.blit(big_font.render("PAUSED", True, WHITE), (300,350))
    if replay_mode:
        screen.blit(big_font.render("REPLAY", True, WHITE), (300,300))
    if winner:
        screen.blit(big_font.render(f"{winner} WINS", True, WHITE), (250,10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
