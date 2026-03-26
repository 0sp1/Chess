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

selected_piece = None
valid_moves = []
current_turn = "RED"

# Store pieces with owner
pieces = {
    (0, 0): "RED",
    (1, 1): "RED",
    (6, 6): "BLUE",
    (7, 7): "BLUE"
}

def get_valid_moves(pos):
    row, col = pos
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            # allow move if empty OR enemy piece (capture)
            if (r, c) not in pieces or pieces[(r, c)] != current_turn:
                moves.append((r, c))

    return moves

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            col = (mx - MARGIN) // SQUARE_SIZE
            row = (my - MARGIN) // SQUARE_SIZE

            if 0 <= row < ROWS and 0 <= col < COLS:
                clicked = (row, col)

                # Select your own piece
                if clicked in pieces and pieces[clicked] == current_turn:
                    selected_piece = clicked
                    valid_moves = get_valid_moves(clicked)

                else:
                    if selected_piece and clicked in valid_moves:
                        # Capture if enemy exists
                        if clicked in pieces:
                            pieces.pop(clicked)

                        # Move piece
                        pieces[clicked] = current_turn
                        pieces.pop(selected_piece)

                        # Switch turn
                        current_turn = "BLUE" if current_turn == "RED" else "RED"

                        selected_piece = None
                        valid_moves = []

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
