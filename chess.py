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
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- SOUND LOADING ---
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

move_sound = load_sound("move.wav")
capture_sound = load_sound("capture.wav")
win_sound = load_sound("win.wav")

selected_piece = None
valid_moves = []
current_turn = "RED"
winner = None
history = []
history_index = 0

red_score = 0
blue_score = 0

turn_start_time = time.time()
TURN_LIMIT = 10

hint_move = None
paused = False

# --- NEW FEATURE ---
move_log = []

def reset_game():
    return {(0,0):("RED",False),(1,1):("RED",False),(6,6):("BLUE",False),(7,7):("BLUE",False)}

pieces = reset_game()
history = [copy.deepcopy(pieces)]

# --- MOVE LOG DRAW ---
def draw_move_log():
    x_offset = 600
    y_offset = 120

    title = font.render("Moves:", True, WHITE)
    screen.blit(title, (x_offset, y_offset - 30))

    for i, (s, e) in enumerate(move_log[-10:]):
        symbol = "x" if abs(s[0]-e[0]) == 2 or abs(s[1]-e[1]) == 2 else "->"
        text = font.render(f"{s} {symbol} {e}", True, WHITE)
        screen.blit(text, (x_offset, y_offset + i * 25))

def get_valid_moves(pos):
    moves = []
    r, c = pos
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0<=nr<ROWS and 0<=nc<COLS and (nr,nc) not in pieces:
            moves.append((nr,nc))
    return moves

def get_captured_piece(s,e):
    if abs(s[0]-e[0])==2 or abs(s[1]-e[1])==2:
        return ((s[0]+e[0])//2,(s[1]+e[1])//2)

def apply_move(s,e):
    global pieces, history, history_index, move_log, red_score, blue_score

    c = get_captured_piece(s,e)

    if c and c in pieces:
        if pieces[c][0]=="RED": blue_score+=1
        else: red_score+=1
        pieces.pop(c)

        if capture_sound:
            capture_sound.play()
    else:
        if move_sound:
            move_sound.play()

    pieces[e] = pieces[s]
    pieces.pop(s)

    # --- MOVE LOG ---
    move_log.append((s,e))
    if len(move_log) > 20:
        move_log.pop(0)

    history.append(copy.deepcopy(pieces))
    history_index += 1

def undo_move():
    global history_index, pieces
    if history_index > 0:
        history_index -= 1
        pieces = copy.deepcopy(history[history_index])
        if move_log:
            move_log.pop()

def draw_board():
    screen.fill(BACKGROUND)

    for r in range(ROWS):
        for c in range(COLS):
            color = GREEN if (r+c)%2==0 else BLACK
            pygame.draw.rect(screen, color,
                (MARGIN + c*SQUARE_SIZE, MARGIN + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            if (r,c) in pieces:
                p_color = RED if pieces[(r,c)][0]=="RED" else BLUE
                pygame.draw.circle(screen, p_color,
                    (MARGIN + c*SQUARE_SIZE + SQUARE_SIZE//2,
                     MARGIN + r*SQUARE_SIZE + SQUARE_SIZE//2), 20)

    draw_move_log()

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_z:
                undo_move()

        if event.type==pygame.MOUSEBUTTONDOWN:
            mx,my=pygame.mouse.get_pos()
            col=(mx-MARGIN)//SQUARE_SIZE
            row=(my-MARGIN)//SQUARE_SIZE

            if (row,col) in pieces:
                selected_piece=(row,col)
            elif selected_piece:
                apply_move(selected_piece,(row,col))
                selected_piece=None

    draw_board()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
