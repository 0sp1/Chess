import pygame

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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

selected_piece = None
valid_moves = []
current_turn = "RED"
winner = None
chain_capture = False  # NEW

def reset_game():
    return {
        (0, 0): "RED",
        (1, 1): "RED",
        (6, 6): "BLUE",
        (7, 7): "BLUE"
    }

pieces = reset_game()

def get_valid_moves(pos):
    row, col = pos
    moves = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        # Normal move
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            if (r, c) not in pieces:
                moves.append((r, c))

        # Jump move (capture)
        jr, jc = row + 2 * dr, col + 2 * dc
        mid = (row + dr, col + dc)

        if 0 <= jr < ROWS and 0 <= jc < COLS:
            if mid in pieces and pieces[mid] != current_turn:
                if (jr, jc) not in pieces:
                    moves.append((jr, jc))

    return moves

def get_captured_piece(start, end):
    # If jump, return the jumped piece
    if abs(start[0] - end[0]) == 2 or abs(start[1] - end[1]) == 2:
        return ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
    return None

def check_winner():
    red_exists = any(owner == "RED" for owner in pieces.values())
    blue_exists = any(owner == "BLUE" for owner in pieces.values())

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

        if event.type == pygame.MOUSEBUTTONDOWN and not winner:
            mx, my = pygame.mouse.get_pos()

            col = (mx - MARGIN) // SQUARE_SIZE
            row = (my - MARGIN) // SQUARE_SIZE

            if 0 <= row < ROWS and 0 <= col < COLS:
                clicked = (row, col)

                # Select piece
                if not chain_capture:
                    if clicked in pieces and pieces[clicked] == current_turn:
                        selected_piece = clicked
                        valid_moves = get_valid_moves(clicked)

                # Move
                if selected_piece and clicked in valid_moves:
                    captured = get_captured_piece(selected_piece, clicked)

                    if captured:
                        pieces.pop(captured)

                    pieces[clicked] = current_turn
                    pieces.pop(selected_piece)

                    # Check for chain capture
                    selected_piece = clicked
                    new_moves = get_valid_moves(clicked)

                    # Only allow further captures
                    capture_moves = [
                        m for m in new_moves
                        if get_captured_piece(clicked, m)
                    ]

                    if captured and capture_moves:
                        valid_moves = capture_moves
                        chain_capture = True
                    else:
                        current_turn = "BLUE" if current_turn == "RED" else "RED"
                        selected_piece = None
                        valid_moves = []
                        chain_capture = False

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
                color = RED if pieces[(row, col)] == "RED" else BLUE
                pygame.draw.circle(screen, color, center, SQUARE_SIZE // 3)

    if winner:
        text = font.render(f"{winner} WINS! Press R to restart", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
