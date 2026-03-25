import pygame

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = 75
MARGIN = 20

GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
BACKGROUND = (128, 0, 128)
HIGHLIGHT = (255, 255, 0)
PIECE_COLOR = (200, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

selected_square = None
selected_piece = None
valid_moves = []

pieces = {(0, 0): True, (1, 1): True}

def get_valid_moves(pos):
    row, col = pos
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            if (r, c) not in pieces:
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
                clicked_square = (row, col)

                if clicked_square in pieces:
                    selected_piece = clicked_square
                    selected_square = clicked_square
                    valid_moves = get_valid_moves(clicked_square)
                else:
                    if selected_piece and clicked_square in valid_moves:
                        pieces.pop(selected_piece)
                        pieces[clicked_square] = True
                        selected_piece = None
                        valid_moves = []
                    selected_square = clicked_square

    screen.fill(BACKGROUND)

    for row in range(ROWS):
        for col in range(COLS):
            color = GREEN if (row + col) % 2 == 0 else BLACK
            x = MARGIN + col * SQUARE_SIZE
            y = MARGIN + row * SQUARE_SIZE

            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            if selected_square == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

            if (row, col) in valid_moves:
                pygame.draw.rect(screen, (0, 0, 255), (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

            if (row, col) in pieces:
                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                pygame.draw.circle(screen, PIECE_COLOR, center, SQUARE_SIZE // 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
