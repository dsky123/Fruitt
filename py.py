import math 
import random
import sys
import pygame

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()

# ---------------------------------------------------------
# GLOBAL CONFIGURATION & CONSTANTS
# ---------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GRID_SIZE = 25

GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

FPS = 60
BASE_SPEED = 1000  # Moves per second

# Colors (Cyberpunk / Modern Neon Palette)
COLOR_BG = (15, 17, 26)
COLOR_GRID = (25, 30, 45)
COLOR_UI_PANEL = (22, 27, 40)
COLOR_TEXT = (240, 244, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_PURPLE = (147, 51, 234)

COLOR_SNAKE_HEAD = (0, 255, 204)
COLOR_SNAKE_BODY = (0, 200, 160)
COLOR_SNAKE_TAIL = (0, 120, 100)

COLOR_FOOD_NORMAL = (255, 50, 100)
COLOR_FOOD_SPECIAL = (255, 200, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEON SERPENT HD - 2D Modern Snake")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("Segoe UI", 48, bold=True)
font_large = pygame.font.SysFont("Segoe UI", 36, bold=True)
font_medium = pygame.font.SysFont("Segoe UI", 24, bold=True)
font_small = pygame.font.SysFont("Segoe UI", 16)


# ---------------------------------------------------------
# SYNTHESIZED SOUND EFFECTS (No external files needed)
# ---------------------------------------------------------
def create_sound(freq_start, freq_end, duration_ms, wave_type="sine"):
    sample_rate = 44100
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (i / n_samples)
        if wave_type == "sine":
            val = int(127 + 127 * math.sin(2 * math.pi * freq * t))
        elif wave_type == "square":
            val = 255 if math.sin(2 * math.pi * freq * t) > 0 else 0
        buf.append(val)
    return pygame.mixer.Sound(buffer=bytes(buf))


sound_eat = create_sound(400, 800, 80, "sine")
sound_special = create_sound(600, 1200, 150, "sine")
sound_gameover = create_sound(300, 80, 400, "square")


# ---------------------------------------------------------
# PARTICLE SYSTEM FOR VISUAL EFFECTS
# ---------------------------------------------------------
class Particle:

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.radius = random.uniform(3, 6)
        self.color = color
        self.life = 1.0  # 1.0 to 0.0
        self.decay = random.uniform(0.03, 0.07)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.radius = max(0, self.radius - 0.1)

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface(
                (int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA
            )
            pygame.draw.circle(
                s,
                (*self.color, alpha),
                (int(self.radius), int(self.radius)),
                int(self.radius),
            )
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


# ---------------------------------------------------------
# GAME ENGINE CLASS
# ---------------------------------------------------------
class SnakeGame:

    def __init__(self):
        self.high_score = 0
        self.reset_game()

    def reset_game(self):
        self.snake = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2),
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT

        self.score = 0
        self.game_over = False
        self.paused = False

        self.food = None
        self.special_food = None
        self.special_food_timer = 0

        self.particles = []
        self.move_counter = 0

        self.spawn_food()

    def spawn_food(self):
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in self.snake:
                self.food = pos
                break

    def spawn_special_food(self):
        if not self.special_food and random.random() < 0.3:
            while True:
                pos = (
                    random.randint(0, GRID_WIDTH - 1),
                    random.randint(0, GRID_HEIGHT - 1),
                )
                if pos not in self.snake and pos != self.food:
                    self.special_food = pos
                    self.special_food_timer = 300  # 5 seconds at 60 FPS
                    break

    def create_explosion(self, grid_pos, color, count=25):
        px = grid_pos[0] * GRID_SIZE + GRID_SIZE // 2
        py = grid_pos[1] * GRID_SIZE + GRID_SIZE // 2
        for _ in range(count):
            self.particles.append(Particle(px, py, color))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                    self.reset_game()
                return

            if event.key == pygame.K_p:
                self.paused = not self.paused

            if not self.paused:
                if (
                    event.key in (pygame.K_UP, pygame.K_w)
                    and self.direction != DOWN
                ):
                    self.next_direction = UP
                elif (
                    event.key in (pygame.K_DOWN, pygame.K_s)
                    and self.direction != UP
                ):
                    self.next_direction = DOWN
                elif (
                    event.key in (pygame.K_LEFT, pygame.K_a)
                    and self.direction != RIGHT
                ):
                    self.next_direction = LEFT
                elif (
                    event.key in (pygame.K_RIGHT, pygame.K_d)
                    and self.direction != LEFT
                ):
                    self.next_direction = RIGHT

    def update(self):
        if self.game_over or self.paused:
            return

        # Particle Updates
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        # Special Food Timer
        if self.special_food:
            self.special_food_timer -= 1
            if self.special_food_timer <= 0:
                self.special_food = None

        # Movement Speed Control
        self.move_counter += 1
        speed_interval = max(
            2, int(FPS / (BASE_SPEED + (self.score // 50)))
        )  # Speeds up with score

        if self.move_counter < speed_interval:
            return
        self.move_counter = 0

        # Apply direction
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Collision with Boundaries
        if not (
            0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT
        ):
            self.trigger_game_over()
            return

        # Collision with Self
        if new_head in self.snake:
            self.trigger_game_over()
            return

        # Move Snake
        self.snake.insert(0, new_head)

        # Eating Normal Food
        if new_head == self.food:
            sound_eat.play()
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
            self.create_explosion(self.food, COLOR_FOOD_NORMAL)
            self.spawn_food()
            self.spawn_special_food()

        # Eating Special Food
        elif self.special_food and new_head == self.special_food:
            sound_special.play()
            self.score += 30
            if self.score > self.high_score:
                self.high_score = self.score
            self.create_explosion(self.special_food, COLOR_FOOD_SPECIAL, 40)
            self.special_food = None

        else:
            self.snake.pop()

    def trigger_game_over(self):
        sound_gameover.play()
        self.create_explosion(self.snake[0], COLOR_SNAKE_HEAD, 50)
        self.game_over = True

    def draw_grid(self, surface):
        surface.fill(COLOR_BG)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(
                surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT), 1
            )
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(
                surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1
            )

    def draw_snake(self, surface):
        length = len(self.snake)
        for idx, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                x * GRID_SIZE + 1,
                y * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2,
            )

            # Gradient Color Interpolation
            t = idx / max(1, length - 1)
            r = int(
                COLOR_SNAKE_HEAD[0] * (1 - t) + COLOR_SNAKE_TAIL[0] * t
            )
            g = int(
                COLOR_SNAKE_HEAD[1] * (1 - t) + COLOR_SNAKE_TAIL[1] * t
            )
            b = int(
                COLOR_SNAKE_HEAD[2] * (1 - t) + COLOR_SNAKE_TAIL[2] * t
            )
            segment_color = (r, g, b)

            # Head Styling
            if idx == 0:
                pygame.draw.rect(
                    surface, COLOR_SNAKE_HEAD, rect, border_radius=7
                )
                # Eyes
                eye_radius = 3
                center_x = x * GRID_SIZE + GRID_SIZE // 2
                center_y = y * GRID_SIZE + GRID_SIZE // 2

                if self.direction == RIGHT:
                    e1 = (center_x + 4, center_y - 4)
                    e2 = (center_x + 4, center_y + 4)
                elif self.direction == LEFT:
                    e1 = (center_x - 4, center_y - 4)
                    e2 = (center_x - 4, center_y + 4)
                elif self.direction == UP:
                    e1 = (center_x - 4, center_y - 4)
                    e2 = (center_x + 4, center_y - 4)
                else:
                    e1 = (center_x - 4, center_y + 4)
                    e2 = (center_x + 4, center_y + 4)

                pygame.draw.circle(surface, (10, 10, 15), e1, eye_radius)
                pygame.draw.circle(surface, (10, 10, 15), e2, eye_radius)
            else:
                pygame.draw.rect(surface, segment_color, rect, border_radius=4)

    def draw_food(self, surface):
        # Pulse Animation
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 2

        # Normal Food
        fx, fy = self.food
        cx = fx * GRID_SIZE + GRID_SIZE // 2
        cy = fy * GRID_SIZE + GRID_SIZE // 2
        r = (GRID_SIZE // 2 - 3) + int(pulse)
        pygame.draw.circle(surface, COLOR_FOOD_NORMAL, (cx, cy), max(2, r))
        pygame.draw.circle(
            surface, (255, 180, 200), (cx, cy), max(1, r - 3)
        )  # Inner Glow

        # Special Food
        if self.special_food:
            sx, sy = self.special_food
            scx = sx * GRID_SIZE + GRID_SIZE // 2
            scy = sy * GRID_SIZE + GRID_SIZE // 2
            sr = (GRID_SIZE // 2 - 2) + int(pulse * 1.5)

            # Pulsing Diamond Shape
            points = [
                (scx, scy - sr),
                (scx + sr, scy),
                (scx, scy + sr),
                (scx - sr, scy),
            ]
            pygame.draw.polygon(surface, COLOR_FOOD_SPECIAL, points)

            # Timer Ring
            angle = (self.special_food_timer / 300) * 360
            if angle > 0:
                arc_rect = pygame.Rect(
                    sx * GRID_SIZE, sy * GRID_SIZE, GRID_SIZE, GRID_SIZE
                )
                pygame.draw.arc(
                    surface,
                    COLOR_GOLD,
                    arc_rect,
                    0,
                    math.radians(angle),
                    2,
                )

    def draw_ui(self, surface):
        # Top HUD Panel
        panel = pygame.Surface((SCREEN_WIDTH, 45), pygame.SRCALPHA)
        panel.fill((*COLOR_UI_PANEL, 220))
        surface.blit(panel, (0, 0))

        score_text = font_medium.render(
            f"SCORE: {self.score}", True, COLOR_TEXT
        )
        high_text = font_medium.render(
            f"HIGH SCORE: {self.high_score}", True, COLOR_GOLD
        )
        surface.blit(score_text, (20, 8))
        surface.blit(high_text, (SCREEN_WIDTH - high_text.get_width() - 20, 8))

        # Pause Overlay
        if self.paused and not self.game_over:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((10, 12, 18, 180))
            surface.blit(overlay, (0, 0))
            p_text = font_large.render("GAME PAUSED", True, COLOR_TEXT)
            surface.blit(
                p_text,
                (
                    SCREEN_WIDTH // 2 - p_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 20,
                ),
            )

        # Game Over Screen
        if self.game_over:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((15, 5, 10, 210))
            surface.blit(overlay, (0, 0))

            go_title = font_title.render("GAME OVER", True, (255, 60, 80))
            final_score = font_medium.render(
                f"Final Score: {self.score}", True, COLOR_TEXT
            )
            restart_text = font_small.render(
                "Press [ SPACE ] or [ R ] to Play Again", True, (180, 190, 210)
            )

            surface.blit(
                go_title,
                (
                    SCREEN_WIDTH // 2 - go_title.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 80,
                ),
            )
            surface.blit(
                final_score,
                (
                    SCREEN_WIDTH // 2 - final_score.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 10,
                ),
            )
            surface.blit(
                restart_text,
                (
                    SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 50,
                ),
            )

    def draw(self, surface):
        self.draw_grid(surface)
        self.draw_food(surface)
        self.draw_snake(surface)

        for p in self.particles:
            p.draw(surface)

        self.draw_ui(surface)


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def main():
    game = SnakeGame()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_input(event)

        game.update()
        game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()