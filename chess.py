import pygame

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = 75
MARGIN = 20

GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
BACKGROUND = (128, 0, 128)
HIGHLIGHT = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

selected_square = None

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
                selected_square = (row, col)

    screen.fill(BACKGROUND)

    for row in range(ROWS):
        for col in range(COLS):
            color = GREEN if (row + col) % 2 == 0 else BLACK
            x = MARGIN + col * SQUARE_SIZE
            y = MARGIN + row * SQUARE_SIZE

            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            if selected_square == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
