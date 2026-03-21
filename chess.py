import pygame

# pygame setup
WIDTH, HEIGHT = 800, 800
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

# Board settings
ROWS, COLS = 8, 8
SQUARE_SIZE = 75
MARGIN = 20

# Colors
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
BACKGROUND = (128, 0, 128)  # purple background

while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with background color
    screen.fill(BACKGROUND)

    # draw the board
    for row in range(ROWS):
        for col in range(COLS):
            color = GREEN if (row + col) % 2 == 0 else BLACK
            x = MARGIN + col * SQUARE_SIZE
            y = MARGIN + row * SQUARE_SIZE
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # update the display
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()
