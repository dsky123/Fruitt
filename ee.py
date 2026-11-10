import math
import random
import sys
import pygame

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()

# ---------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Setup Window (Supports RESIZABLE and FULLSCREEN toggle)
is_fullscreen = False
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("NEON STRIKER PRO - Fullscreen & Enhanced Audio")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Segoe UI", 36, bold=True)
font_medium = pygame.font.SysFont("Segoe UI", 24, bold=True)
font_small = pygame.font.SysFont("Segoe UI", 16)


# ---------------------------------------------------------
# SYNTHESIZED SOUND ENGINE (No external files needed)
# ---------------------------------------------------------
def create_sound(freq_start, freq_end, duration_ms, wave_type="sine", volume=0.5):
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
        elif wave_type == "noise":
            val = random.randint(0, 255)
        buf.append(val)
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    sound.set_volume(volume)
    return sound


sound_laser = create_sound(850, 300, 60, "sine", 0.4)
sound_explosion = create_sound(180, 40, 350, "square", 0.6)
sound_hurt = create_sound(120, 30, 250, "square", 0.5)


# ---------------------------------------------------------
# STARFIELD & PARALLAX BACKGROUND
# ---------------------------------------------------------
class Star:

    def __init__(self, layer):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.layer = layer
        if layer == 1:
            self.speed = 0.5
            self.size = 1
            self.brightness = 100
        elif layer == 2:
            self.speed = 1.5
            self.size = 2
            self.brightness = 180
        else:
            self.speed = 3.0
            self.size = 3
            self.brightness = 255

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


# ---------------------------------------------------------
# PARTICLE SYSTEM
# ---------------------------------------------------------
class Particle:

    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.uniform(2, 6)
        self.color = color
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.07)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.radius = max(0, self.radius - 0.15)

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.radius * 4), int(self.radius * 4)), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                (*self.color, alpha),
                (int(self.radius * 2), int(self.radius * 2)),
                int(self.radius),
            )
            surface.blit(s, (int(self.x - self.radius * 2), int(self.y - self.radius * 2)))


# ---------------------------------------------------------
# GAME CLASSES
# ---------------------------------------------------------
class Player:

    def __init__(self):
        self.width = 50
        self.height = 45
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 90
        self.speed = 6.5
        self.health = 3
        self.max_health = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed

        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
        self.y = max(SCREEN_HEIGHT // 2, min(SCREEN_HEIGHT - self.height // 2, self.y))

    def draw(self, surface):
        # Exhaust flame
        flame_height = random.randint(10, 22)
        pygame.draw.polygon(
            surface,
            (255, 120, 0),
            [(self.x - 8, self.y + 20), (self.x + 8, self.y + 20), (self.x, self.y + 20 + flame_height)],
        )
        pygame.draw.polygon(
            surface,
            (255, 255, 100),
            [(self.x - 4, self.y + 20), (self.x + 4, self.y + 20), (self.x, self.y + 20 + flame_height // 2)],
        )

        # Hull body
        points = [
            (self.x, self.y - 24),
            (self.x - 24, self.y + 20),
            (self.x - 8, self.y + 12),
            (self.x, self.y + 16),
            (self.x + 8, self.y + 12),
            (self.x + 24, self.y + 20),
        ]
        pygame.draw.polygon(surface, (30, 40, 60), points)
        pygame.draw.polygon(surface, (0, 240, 255), points, 2)
        pygame.draw.ellipse(surface, (100, 220, 255), (self.x - 5, self.y - 6, 10, 16))


class Bullet:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 14

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.line(surface, (150, 255, 200), (self.x, self.y), (self.x, self.y + 16), 3)
        pygame.draw.line(surface, (255, 255, 255), (self.x, self.y + 4), (self.x, self.y + 10), 1)


class Enemy:

    def __init__(self):
        self.width = 44
        self.height = 40
        self.x = random.randint(40, SCREEN_WIDTH - 40)
        self.y = random.randint(-160, -40)
        self.speed = random.uniform(2.2, 4.8)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        points = [
            (self.x, self.y + 20),
            (self.x - 22, self.y - 15),
            (self.x - 8, self.y - 8),
            (self.x, self.y - 20),
            (self.x + 8, self.y - 8),
            (self.x + 22, self.y - 15),
        ]
        pygame.draw.polygon(surface, (50, 20, 30), points)
        pygame.draw.polygon(surface, (255, 50, 100), points, 2)
        pygame.draw.circle(surface, (255, 150, 0), (int(self.x), int(self.y - 4)), 3)


# ---------------------------------------------------------
# GAME ENGINE
# ---------------------------------------------------------
class ProSpaceShooter:

    def __init__(self):
        self.high_score = 0
        self.stars = [Star(random.choice([1, 2, 3])) for _ in range(120)]
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.shoot_cooldown = 0
        self.screen_shake = 0

    def trigger_shake(self, intensity):
        self.screen_shake = intensity

    def spawn_explosion(self, x, y, color, count=25):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed_mult=1.2))

    def handle_input(self, event):
        global is_fullscreen, screen
        if event.type == pygame.KEYDOWN:
            # Toggle Fullscreen with 'F' key
            if event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

            if game.game_over and event.key == pygame.K_SPACE:
                self.reset_game()

    def update(self):
        for star in self.stars:
            star.update()

        keys = pygame.key.get_pressed()
        if not self.game_over:
            self.player.move(keys)
            if keys[pygame.K_SPACE]:
                if self.shoot_cooldown == 0:
                    sound_laser.play()
                    self.bullets.append(Bullet(self.player.x, self.player.y - 20))
                    self.shoot_cooldown = 10

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.game_over:
            return

        if self.screen_shake > 0:
            self.screen_shake -= 1

        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        for b in self.bullets[:]:
            b.update()
            if b.y < 0:
                self.bullets.remove(b)

        self.spawn_timer += 1
        spawn_interval = max(18, 45 - (self.score // 40))
        if self.spawn_timer >= spawn_interval:
            self.enemies.append(Enemy())
            self.spawn_timer = 0

        for e in self.enemies[:]:
            e.update()
            if e.y > SCREEN_HEIGHT + 50:
                self.enemies.remove(e)
                continue

            player_rect = pygame.Rect(
                self.player.x - self.player.width // 2,
                self.player.y - self.player.height // 2,
                self.player.width,
                self.player.height,
            )
            enemy_rect = pygame.Rect(e.x - e.width // 2, e.y - e.height // 2, e.width, e.height)

            if player_rect.colliderect(enemy_rect):
                sound_hurt.play()
                self.trigger_shake(12)
                self.spawn_explosion(e.x, e.y, (255, 50, 100), 35)
                self.enemies.remove(e)
                self.player.health -= 1
                if self.player.health <= 0:
                    sound_explosion.play()
                    self.trigger_shake(25)
                    self.spawn_explosion(self.player.x, self.player.y, (0, 240, 255), 60)
                    self.game_over = True
                continue

            for b in self.bullets[:]:
                bullet_rect = pygame.Rect(b.x - 2, b.y, 4, 16)
                if bullet_rect.colliderect(enemy_rect):
                    sound_explosion.play()
                    self.trigger_shake(6)
                    self.spawn_explosion(e.x, e.y, (255, 180, 50), 20)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e in self.enemies:
                        self.enemies.remove(e)
                    self.score += 10
                    if self.score > self.high_score:
                        self.high_score = self.score
                    break

    def draw(self, surface):
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_surface.fill((8, 10, 16))

        for star in self.stars:
            star.draw(render_surface)
        for p in self.particles:
            p.draw(render_surface)
        for b in self.bullets:
            b.draw(render_surface)
        for e in self.enemies:
            e.draw(render_surface)

        self.player.draw(render_surface)

        score_text = font_medium.render(f"SCORE: {self.score}", True, (240, 244, 255))
        high_text = font_medium.render(f"HIGH: {self.high_score}", True, (255, 215, 0))
        health_text = font_medium.render(f"SHIELD: {'█ ' * self.player.health}", True, (0, 255, 200))
        fs_hint = font_small.render("[Press F to Toggle Fullscreen]", True, (120, 140, 170))

        render_surface.blit(score_text, (25, 20))
        render_surface.blit(high_text, (SCREEN_WIDTH - high_text.get_width() - 25, 20))
        render_surface.blit(health_text, (25, 55))
        render_surface.blit(fs_hint, (SCREEN_WIDTH // 2 - fs_hint.get_width() // 2, 20))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 2, 8, 230))
            render_surface.blit(overlay, (0, 0))

            go_title = font_large.render("SYSTEM FAILURE // DESTROYED", True, (255, 60, 90))
            final_score = font_medium.render(f"Final Score: {self.score}", True, (220, 230, 250))
            restart_text = font_small.render("Press [ SPACE ] to Reinitialize Mission", True, (140, 160, 190))

            render_surface.blit(go_title, (SCREEN_WIDTH // 2 - go_title.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            render_surface.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
            render_surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        # Scale and blit to actual screen (supports fullscreen scaling)
        scaled_surface = pygame.transform.smoothscale(render_surface, surface.get_size())
        surface.blit(scaled_surface, (shake_x, shake_y))


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def main():
    global game
    game = ProSpaceShooter()
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