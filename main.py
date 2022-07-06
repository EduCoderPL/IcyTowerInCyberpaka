import time
import pygame
from pygame.locals import *
import random

from constants import *

import sys

# KEEP GAME IN MAX 60 FPS
clock = pygame.time.Clock()
FPS = 60

# IMPROVE GAME SPEED DURING GAME:
TIME_TO_ACCELERATE = 30

# SCORE
score = 0

# OFFSET MOVEMENT

# IMAGES:
leftWallImage = pygame.image.load('Images/LeftWall.png')
rightWallImage = pygame.transform.flip(leftWallImage, True, False)
backImage = pygame.image.load('Images/BackWall.png')

pygame.init()
fontPlatform = pygame.font.SysFont('Arial', 14)
fontScore = pygame.font.SysFont('Arial', 48)


click = False


class Drawable:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.angle = 0
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        Game.screen.blit(pygame.transform.rotate(self.image, self.angle),
                         (self.x + Game.offsetX, self.y + Game.offsetY))


class Player(Drawable):
    def __init__(self, x, y):
        super().__init__(x, y, 'Images/Hero.png')

        self.velX = 0
        self.velY = 0

        self.canJump = False
        self.jumping = False
        self.rotating = False

        self.angle = 0
        self.lastX = self.x
        self.lastY = self.y

    def move(self):
        self.lastX = self.x
        self.lastY = self.y

        self.velY += GRAVITY

        self.velX *= 0.97
        self.velY *= 0.98

        self.x += self.velX
        self.y += self.velY

        if self.x < LEFT_LIMIT:
            self.x = LEFT_LIMIT
            self.velX *= -1

        if self.x > RIGHT_LIMIT - self.width:
            self.x = RIGHT_LIMIT - self.width
            self.velX *= -1

    def check_collision(self, listOfPlatforms):
        self.rect = Rect(self.x, self.y, self.width, self.height)
        toPlatformCollisionRect = Rect(self.lastX, self.lastY + self.height, self.width, abs(self.lastY - self.y))
        for platform in listOfPlatforms:
            if toPlatformCollisionRect.colliderect(platform.rect) and self.velY > 0:
                self.y = platform.y - self.height + 1
                self.velY = 0
                self.velX *= 0.95
                self.canJump = True
                self.rotating = False

    def update(self):
        self.move()
        self.check_collision(Game.platformList)

        if self.rotating:
            self.angle += 10
        else:
            self.angle = 0

    def jump(self):
        self.velY = - (16 + 1.2 * abs(self.velX))
        self.canJump = False
        if self.velY < -25:
            self.rotating = True

    def draw(self):
        super().draw()


class Platform(Drawable):
    image = pygame.image.load("Images/Platform.png")
    counter = 0

    def __init__(self, x, y):
        Platform.counter += 1
        self.number = Platform.counter

        super().__init__(x, y, "Images/Platform.png")

        if self.number == 1 or self.number % 50 == 0:
            self.image = pygame.transform.scale(pygame.image.load("Images/Platform.png"),
                                                (RIGHT_LIMIT - LEFT_LIMIT, self.image.get_height()))
            self.x = LEFT_LIMIT

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = Rect(self.x, self.y, self.width, self.height / 10)

    def draw(self):

        super().draw()

        if self.number % 10 == 0:
            centerPos = (self.x + self.width / 2 + Game.offsetX, self.y + self.height / 2 + Game.offsetY)
            pygame.draw.rect(Game.screen, (10, 10, 10),
                             Rect(centerPos[0] - 10, centerPos[1] - 10, 10 * len(str(self.number)) + 20, 30))
            img1 = fontPlatform.render(str(self.number), True, (200, 200, 255))
            Game.screen.blit(img1, centerPos)


class Game:
    offsetX = 0
    offsetY = 0

    platformList = []
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Icy Tower, ale to projekt testowy z Pygame')

    def __init__(self):
        self.player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y - 200)
        self.lastAccelerate = time.time()

        self.make_first_platforms()
        self.hurryUpTextPosY = -50

        self.run = True
        self.hurryUpText = fontScore.render("HURRY UP!!!", True, (200, 200, 0))
        self.offsetVelocityY = 0

    def make_another_platform(self):
        posX = random.randint(DISTANCE_FROM_WALL + LEFT_LIMIT,
                              RIGHT_LIMIT - Platform.image.get_width() - DISTANCE_FROM_WALL)
        posY = PLAYER_START_POSITION_Y - 100 * Platform.counter
        self.platformList.append(Platform(posX, posY))

    def make_first_platforms(self):
        for i in range(11):
            self.make_another_platform()

    def manage_platforms(self):
        # Dodawanie platform
        if self.player.y < 1500 - 100 * Platform.counter:
            self.make_another_platform()

        # Usuwanie platform
        for platform in self.platformList:
            if platform.y + Game.offsetY > SCREEN_HEIGHT:
                self.platformList.remove(platform)
                global score
                score += 10
                del platform

    def drawTiled(self, x, y, image, offsetScale=1.0):
        self.screen.blit(image, (x, y + (offsetScale * Game.offsetY) % image.get_height()))
        self.screen.blit(image, (x, y - image.get_height() + ((offsetScale * Game.offsetY) % image.get_height())))

    def loop(self):
        self.player_input()
        self.game_logic()
        self.draw_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                sys.exit()

        pygame.display.update()
        clock.tick(FPS)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP] and self.player.canJump:
            self.player.jump()
        if keys[K_LEFT]:
            self.player.velX -= 1
        if keys[K_RIGHT]:
            self.player.velX += 1

    def game_logic(self):
        self.player.update()
        self.manage_offset()
        self.manage_platforms()

    def draw_game(self):
        self.screen.fill((0, 0, 30))
        self.drawTiled(LEFT_LIMIT, 0, backImage, 0.5)

        for platform in self.platformList:
            platform.draw()

        self.player.draw()
        self.drawTiled(0, 0, leftWallImage, 1.3)
        self.drawTiled(RIGHT_LIMIT, 0, rightWallImage, 1.3)

        # RYSOWANIE INTERFEJSU
        img1 = fontScore.render(str(score), True, (200, 200, 0))
        self.screen.blit(img1, (20, 20))

        self.screen.blit(self.hurryUpText, (300, self.hurryUpTextPosY))

    def manage_offset(self):
        # Przewijanie się ekranu po pierwszym większym skoku;
        if self.player.y < 100 and self.offsetY < 200:
            print("Rozpoczęcie przewijania się ekranu")
            self.offsetVelocityY = 1

        # Przyspieszanie przewijania ekranu co określnony czas
        if time.time() - self.lastAccelerate > TIME_TO_ACCELERATE and self.offsetVelocityY > 0:
            self.offsetVelocityY += 1
            self.lastAccelerate = time.time()
            self.hurryUpTextPosY = SCREEN_HEIGHT + 100

        Game.offsetY += self.offsetVelocityY

        if self.player.y + Game.offsetY < 150:
            Game.offsetY += abs(self.player.y + Game.offsetY - 150) / 20

        if self.player.y + Game.offsetY > SCREEN_HEIGHT:
            self.run = False

        self.hurryUpTextPosY -= 1


if __name__ == "__main__":
    game = Game()

    while game.run:
        game.loop()
    pygame.quit()
