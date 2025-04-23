#!/usr/bin/env python3
"""AI Makerspace Flappy Bird Game"""
import pygame
import sys
import random
import os

# Game settings
WIDTH = 400
HEIGHT = 600
FPS = 60
GRAVITY = 0.4
FLAP_STRENGTH = -8  # Reduced flap strength for gentler bounce
PIPE_SPEED = -2
PIPE_GAP = 180
PIPE_FREQUENCY = 2000  # milliseconds

# Colours (Canadian spelling)
BG_COLOUR = (20, 20, 20)
BIRD_COLOUR = (50, 200, 250)
PIPE_COLOUR = (0, 200, 100)
TEXT_COLOUR = (230, 230, 230)
 
# Enhanced graphics settings
BG_TOP = (135, 206, 235)       # Sky blue top for gradient
BG_BOTTOM = (255, 255, 255)    # White bottom for gradient
GROUND_COLOUR = (34, 139, 34)  # Forest green ground
GROUND_HEIGHT = 50             # Height of ground at bottom
PIPE_BORDER_COLOUR = (0, 150, 75)  # Border colour for pipes

HS_FILE = "highscore.txt"

def load_highscore():
    if not os.path.isfile(HS_FILE):
        return 0
    try:
        with open(HS_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HS_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.radius = 20

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        x, y, r = int(self.x), int(self.y), self.radius
        # Draw bird as a triangle pointing right
        points = [(x - r, y + r), (x - r, y - r), (x + r, y)]
        pygame.draw.polygon(surface, BIRD_COLOUR, points)
        # Draw eye
        eye_radius = r // 5
        eye_x = x + r // 2
        eye_y = y - r // 2
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), eye_radius)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, eye_y), eye_radius // 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        # Determine random gap position
        self.height = random.randint(50, HEIGHT - PIPE_GAP - 50)
        self.passed = False

    def update(self):
        self.x += PIPE_SPEED

    def off_screen(self):
        return self.x < -50

    def draw(self, surface):
        # Top pipe
        top_rect = pygame.Rect(self.x, 0, 50, self.height)
        # Bottom pipe
        bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, 50, HEIGHT - (self.height + PIPE_GAP))
        # Draw pipes with border for depth effect
        pygame.draw.rect(surface, PIPE_COLOUR, top_rect)
        pygame.draw.rect(surface, PIPE_BORDER_COLOUR, top_rect, width=3)
        pygame.draw.rect(surface, PIPE_COLOUR, bottom_rect)
        pygame.draw.rect(surface, PIPE_BORDER_COLOUR, bottom_rect, width=3)

    def collides_with(self, bird):
        bird_rect = bird.get_rect()
        top_rect = pygame.Rect(self.x, 0, 50, self.height)
        bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, 50, HEIGHT - (self.height + PIPE_GAP))
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

def draw_text(surface, text, size, x, y, centre=True, colour=None, bold=False):
    """Render text with optional colour, bold style, and a drop shadow for readability."""
    if colour is None:
        colour = TEXT_COLOUR
    # Create font (optional bold)
    font = pygame.font.SysFont(None, size, bold=bold)
    # Render text and shadow surfaces
    text_surf = font.render(text, True, colour)
    shadow_surf = font.render(text, True, (0, 0, 0))
    # Positioning
    text_rect = text_surf.get_rect()
    if centre:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    # Draw drop shadow
    shadow_rect = text_rect.copy()
    shadow_offset = 2
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    surface.blit(shadow_surf, shadow_rect)
    # Draw main text
    surface.blit(text_surf, text_rect)

def draw_gradient_background(surface):
    """Draw a vertical gradient background and ground."""
    for y in range(HEIGHT - GROUND_HEIGHT):
        ratio = y / (HEIGHT - GROUND_HEIGHT)
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    pygame.draw.rect(surface, GROUND_COLOUR, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

def show_menu(screen):
    draw_gradient_background(screen)
    # Title with AI Makerspace flair: bold, coloured, larger size
    draw_text(screen,
              "AI Makerspace Flappy Bird",
              48,
              WIDTH//2,
              HEIGHT//3,
              colour=BIRD_COLOUR,
              bold=True)
    # Instructions
    draw_text(screen, "Press SPACE to start", 24, WIDTH//2, HEIGHT//2)
    draw_text(screen, "Press ESC to quit", 18, WIDTH//2, HEIGHT//2 + 40)
    pygame.display.flip()

def show_game_over(screen, score, highscore):
    draw_gradient_background(screen)
    # Game Over title with AI Makerspace flair
    draw_text(screen,
              "Game Over",
              48,
              WIDTH//2,
              HEIGHT//3,
              colour=BIRD_COLOUR,
              bold=True)
    draw_text(screen, f"Score: {score}", 24, WIDTH//2, HEIGHT//2)
    draw_text(screen, f"High Score: {highscore}", 24, WIDTH//2, HEIGHT//2 + 40)
    draw_text(screen, "Press SPACE to play again", 20, WIDTH//2, HEIGHT//2 + 100)
    draw_text(screen, "Press ESC to quit", 20, WIDTH//2, HEIGHT//2 + 130)
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Makerspace Flappy Bird")
    clock = pygame.time.Clock()

    highscore = load_highscore()

    while True:
        # Menu loop
        in_menu = True
        while in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        in_menu = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            show_menu(screen)
            clock.tick(FPS)

        # Game variables
        bird = Bird(WIDTH // 4, HEIGHT // 2)
        pipes = []
        score = 0

        SPAWNPIPE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

        # Game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == SPAWNPIPE:
                    pipes.append(Pipe(WIDTH))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.flap()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Update
            bird.update()
            for pipe in pipes:
                pipe.update()
                if not pipe.passed and pipe.x + 50 < bird.x:
                    score += 1
                    pipe.passed = True
            pipes = [p for p in pipes if not p.off_screen()]

            # Check collisions
            if bird.y - bird.radius <= 0 or bird.y + bird.radius >= HEIGHT:
                running = False
            for pipe in pipes:
                if pipe.collides_with(bird):
                    running = False

            # Draw
            draw_gradient_background(screen)
            for pipe in pipes:
                pipe.draw(screen)
            bird.draw(screen)
            draw_text(screen, f"Score: {score}", 24, 10, 10, centre=False)
            pygame.display.flip()
            clock.tick(FPS)

        # Game over
        if score > highscore:
            highscore = score
            save_highscore(highscore)
        show_game_over(screen, score, highscore)

        # Wait for restart or quit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            clock.tick(FPS)

if __name__ == "__main__":
    main()