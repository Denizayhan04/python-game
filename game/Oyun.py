import pgzrun
import random
from pgzhelper import *

WIDTH = 800
HEIGHT = 600
skyblue = (0, 192, 255)
green = (0, 200, 0)
BG_IMAGE = "background"
MIN_ENEMY_DISTANCE = 300

sound_muted = False
score = 0
game_state = "menu"
game_over = False


jump_sound = sounds.jump
lose_sound = sounds.lose



class Player:
    def __init__(self):
        self.actor = Actor("run1")
        self.actor.x = 100
        self.actor.y = 450
        self.actor.images = ["run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8"]
        self.velocity = 0
        self.gravity = 1

    def update(self):
        self.actor.animate()

        if keyboard.up and self.actor.y == 450:
            self.velocity = -20
            if not sound_muted and jump_sound:
                jump_sound.play()

        if self.actor.y > 450:
            self.velocity = 0
            self.actor.y = 450

        if keyboard.down and self.actor.y != 450:
            self.velocity = 100

        self.actor.y += self.velocity
        self.velocity += self.gravity

    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, images, y_range=(300, 400), name="enemy"):
        self.actor = Actor(images[0])
        self.actor.images = images
        self.actor.fps = 20
        self.actor.x = random.randint(1000, 1500)
        self.actor.y = random.randint(*y_range)
        self.actor.passed = False
        self.y_range = y_range
        self.name = name

    def update(self, speed, other_enemy_x=None):
        self.actor.animate()
        self.actor.x -= speed

        if self.actor.x < -50:
            while True:
                self.actor.x = random.randint(1000, 1500)
                self.actor.y = random.randint(*self.y_range)
                if other_enemy_x is None or abs(self.actor.x - other_enemy_x) >= MIN_ENEMY_DISTANCE:
                    break
            self.actor.passed = False

    def draw(self):
        self.actor.draw()

    def reset(self, other_enemy_x=None):
        while True:
            self.actor.x = random.randint(1000, 1500)
            self.actor.y = random.randint(*self.y_range)
            if other_enemy_x is None or abs(self.actor.x - other_enemy_x) >= MIN_ENEMY_DISTANCE:
                break
        self.actor.passed = False

class Game:
    def __init__(self):
        self.player = Player()
        self.enemy1 = Enemy(["enemy", "enemy_1", "enemy_2", "enemy_3"])
        self.enemy2 = Enemy(["snake", "snake_walk"], y_range=(500, 500), name="snake")
        self.score = 0
        self.enemy_speed = 5
        self.over = False

    def update(self):
        global game_state, game_over, score

        self.player.update()
        self.enemy1.update(self.enemy_speed, self.enemy2.actor.x)
        self.enemy2.update(self.enemy_speed, self.enemy1.actor.x)

        if not self.enemy1.actor.passed and self.player.actor.x > self.enemy1.actor.x:
            self.score += 1
            self.enemy1.actor.passed = True

        if not self.enemy2.actor.passed and self.player.actor.x > self.enemy2.actor.x:
            self.score += 1
            self.enemy2.actor.passed = True

        if self.score % 10 == 0 and self.score != 0:
            self.enemy_speed += 0.5

        if (self.player.actor.colliderect(self.enemy1.actor) or self.player.actor.colliderect(self.enemy2.actor)) and not self.over:
            self.over = True
            game_over = True
            game_state = "game_over"
            if not sound_muted and lose_sound:
                lose_sound.play()
            music.stop()

    def draw(self):
        screen.blit(BG_IMAGE, (0, 0))
        screen.draw.filled_rect(Rect(0, 500, 800, 100), green)
        self.enemy1.draw()
        self.enemy2.draw()
        self.player.draw()
        screen.draw.text(f"Score: {self.score}", topleft=(10, 10), fontsize=40, color="white")

        if self.over:
            screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 40), fontsize=80, color="red")
            screen.draw.text("Press SPACE to restart", center=(WIDTH / 2, HEIGHT / 2 + 40), fontsize=40, color="white")

    def restart(self):
        global sound_muted
        self.score = 0
        self.enemy_speed = 5
        self.over = False
        self.player.actor.y = 450
        self.player.velocity = 0
        self.enemy1.reset()
        self.enemy2.reset(self.enemy1.actor.x)
        if not sound_muted:
            music.play("background_music")

game = Game()

def update():
    if game_state == "playing":
        game.update()

def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        game.draw()
    elif game_state == "game_over":
        draw_game_over()

def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("RUNNING GAME", center=(WIDTH / 2, HEIGHT / 2 - 100), fontsize=60, color="white")

    start_button = Rect(WIDTH / 2 - 100, HEIGHT / 2, 200, 50)
    mute_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 60, 200, 50)
    quit_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 120, 200, 50)

    screen.draw.filled_rect(start_button, skyblue)
    screen.draw.filled_rect(mute_button, skyblue)
    screen.draw.filled_rect(quit_button, skyblue)

    screen.draw.text("Start Game", center=start_button.center, fontsize=40, color="white")
    mute_text = "Unmute" if sound_muted else "Mute"
    screen.draw.text(mute_text, center=mute_button.center, fontsize=40, color="white")
    screen.draw.text("Quit", center=quit_button.center, fontsize=40, color="white")

def draw_game_over():
    screen.fill((0, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 40), fontsize=80, color="red")
    screen.draw.text(f"Score: {game.score}", center=(WIDTH / 2, HEIGHT / 2 + 20), fontsize=40, color="white")
    screen.draw.text("Press SPACE to restart", center=(WIDTH / 2, HEIGHT / 2 + 80), fontsize=40, color="white")

def on_mouse_down(pos):
    global game_state, sound_muted, game_over

    start_button = Rect(WIDTH / 2 - 100, HEIGHT / 2, 200, 50)
    mute_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 60, 200, 50)
    quit_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 120, 200, 50)

    if start_button.collidepoint(pos):
        game_state = "playing"
        game_over = False
        game.restart()
    elif mute_button.collidepoint(pos):
        sound_muted = not sound_muted
    elif quit_button.collidepoint(pos):
        exit()

def on_key_down(key):
    global game_state, game_over
    if key == keys.SPACE:
        if game_state in ["menu", "game_over"]:
            game_state = "playing"
            game_over = False
            game.restart()

pgzrun.go()
