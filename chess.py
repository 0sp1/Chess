import pygame
import copy

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = 75
MARGIN = 20

GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
BACKGROUND = (128, 0, 128)
HIGHLIGHT = (255, 255, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)

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

# ✅ NEW: history for undo
history = []

def reset_game():
    return {
        (0, 0): ("RED", False),
        (1, 1): ("RED", False),
        (6, 6): ("BLUE", False),
        (7, 7): ("BLUE", False)
    }

pieces = reset_game()

def get_valid_moves(pos):
    row, col = pos
    owner, king = pieces[pos]
    moves = []
    captures = []
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            if (r, c) not in pieces:
                moves.append((r, c))

        jr, jc = row + 2*dr, col + 2*dc
        mid = (row + dr, col + dc)

        if 0 <= jr < ROWS and 0 <= jc < COLS:
            if mid in pieces and pieces[mid][0] != owner and (jr, jc) not in pieces:
                captures.append((jr, jc))

    return captures if captures else moves

def get_all_captures(player):
    all_caps = []
    for pos, (owner, _) in pieces.items():
        if owner == player:
            moves = get_valid_moves(pos)
            for m in moves:
                if get_captured_piece(pos, m):
                    all_caps.append((pos, m))
    return all_caps

def get_captured_piece(start, end):
    if abs(start[0]-end[0]) == 2 or abs(start[1]-end[1]) == 2:
        return ((start[0]+end[0])//2, (start[1]+end[1])//2)
    return None

def promote(pos):
    row, col = pos
    owner, king = pieces[pos]
    if owner == "RED" and row == ROWS-1:
        pieces[pos] = (owner, True)
    if owner == "BLUE" and row == 0:
        pieces[pos] = (owner, True)

def check_winner():
    red_exists = any(o == "RED" for o, _ in pieces.values())
    blue_exists = any(o == "BLUE" for o, _ in pieces.values())
    if not red_exists:
        return "BLUE"
    if not blue_exists:
        return "RED"
    return None

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pieces = reset_game()
                current_turn = "RED"
                selected_piece = None
                valid_moves = []
                winner = None
                chain_capture = False
                move_count = 0
                history.clear()

            # ✅ UNDO FEATURE
            if event.key == pygame.K_u and history:
                pieces, current_turn, move_count, chain_capture = history.pop()
                selected_piece = None
                valid_moves = []
                winner = None

        if event.type == pygame.MOUSEBUTTONDOWN and not winner:
            mx, my = pygame.mouse.get_pos()
            col = (mx - MARGIN) // SQUARE_SIZE
            row = (my - MARGIN) // SQUARE_SIZE

            if 0 <= row < ROWS and 0 <= col < COLS:
                clicked = (row, col)
                forced = get_all_captures(current_turn)

                if not chain_capture:
                    if clicked in pieces and pieces[clicked][0] == current_turn:
                        moves = get_valid_moves(clicked)
                        if forced:
                            moves = [m for m in moves if get_captured_piece(clicked, m)]
                        if moves:
                            selected_piece = clicked
                            valid_moves = moves

                if selected_piece and clicked in valid_moves:
                    
                    # ✅ SAVE STATE BEFORE MOVE
                    history.append((
                        copy.deepcopy(pieces),
                        current_turn,
                        move_count,
                        chain_capture
                    ))

                    captured = get_captured_piece(selected_piece, clicked)

                    if captured:
                        pieces.pop(captured)

                    owner, king = pieces[selected_piece]
                    pieces[clicked] = (owner, king)
                    pieces.pop(selected_piece)

                    promote(clicked)

                    selected_piece = clicked
                    new_moves = get_valid_moves(clicked)
                    capture_moves = [m for m in new_moves if get_captured_piece(clicked, m)]

                    if captured and capture_moves:
                        valid_moves = capture_moves
                        chain_capture = True
                    else:
                        current_turn = "BLUE" if current_turn == "RED" else "RED"
                        selected_piece = None
                        valid_moves = []
                        chain_capture = False
                        move_count += 1

                    winner = check_winner()

    screen.fill(BACKGROUND)

    for row in range(ROWS):
        for col in range(COLS):
            color = GREEN if (row + col) % 2 == 0 else BLACK
            x = MARGIN + col * SQUARE_SIZE
            y = MARGIN + row * SQUARE_SIZE

            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            if selected_piece == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

            if (row, col) in valid_moves:
                pygame.draw.rect(screen, (0, 0, 255), (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

            if (row, col) in pieces:
                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                owner, king = pieces[(row, col)]
                color = RED if owner == "RED" else BLUE
                pygame.draw.circle(screen, color, center, SQUARE_SIZE // 3)
                if king:
                    pygame.draw.circle(screen, WHITE, center, SQUARE_SIZE // 6)

    turn_text = font.render(f"Turn: {current_turn}", True, WHITE)
    move_text = font.render(f"Moves: {move_count}", True, WHITE)
    undo_text = font.render("Press U to undo", True, WHITE)

    screen.blit(turn_text, (20, 5))
    screen.blit(move_text, (200, 5))
    screen.blit(undo_text, (400, 5))

    if winner:
        text = big_font.render(f"{winner} WINS! Press R", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
