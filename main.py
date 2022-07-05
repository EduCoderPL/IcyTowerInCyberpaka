import time
import pygame
from pygame.locals import *
import random

from constants import *

# KEEP GAME IN MAX 60 FPS
clock = pygame.time.Clock()
FPS = 60

# IMPROVE GAME SPEED DURING GAME:
TIME_TO_ACCELERATE = 30


# SCORE
score = 0

# OFFSET MOVEMENT
offsetX = 0
offsetY = 0
offsetVelocityY = 0

# IMAGES:
leftWallImage = pygame.image.load('Images/LeftWall.png')
rightWallImage = pygame.transform.flip(leftWallImage, True, False)
backImage = pygame.image.load('Images/BackWall.png')

pygame.init()
fontPlatform = pygame.font.SysFont('Arial', 14)
fontScore = pygame.font.SysFont('Arial', 48)
hurryUpText = fontScore.render("HURRY UP!!!", True, (200, 200, 0))
hurryUpTextPosY = -50


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.velX = 0
        self.velY = 0

        self.canJump = False
        self.jumping = False
        self.rotating = False

        self.image = pygame.image.load('Images/Hero.png')
        self.angle = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self):
        self.lastX = self.x
        self.lastY = self.y

        self.velY += 0.8

        # Dodanie siły oporu:
        self.velX *= 0.97
        self.velY *= 0.98

        self.x += self.velX
        self.y += self.velY

        # Sprawdzanie, czy gracz nie wyszedł poza ekran;
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
        self.check_collision(platformList)

        if self.rotating:
            self.angle += 10
        else:
            self.angle = 0

    def jump(self):
        player.velY = - (16 + 1.2 * abs(player.velX))
        player.canJump = False
        if player.velY < -25:
            player.rotating = True

    def draw(self):
        screen.blit(pygame.transform.rotate(self.image, self.angle), (self.x + offsetX, self.y + offsetY))


class Platform:
    image = pygame.image.load("Images/Platform.png")
    counter = 0

    def __init__(self, x, y):
        Platform.counter += 1
        self.number = Platform.counter
        self.x = x
        self.y = y
        self.image = pygame.image.load("Images/Platform.png")


        if self.number == 1 or self.number % 50 == 0:
            self.image = pygame.transform.scale(pygame.image.load("Images/Platform.png"),
                                                (RIGHT_LIMIT - LEFT_LIMIT, self.image.get_height()))
            self.x = LEFT_LIMIT

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = Rect(self.x, self.y, self.width, self.height / 10)


    def draw(self):

        screen.blit(self.image, (self.x + offsetX, self.y + offsetY))

        if self.number % 10 == 0:
            centerPos = (self.x + self.width / 2 + offsetX, self.y + self.height / 2 + offsetY)
            pygame.draw.rect(screen, (10, 10, 10), Rect(centerPos[0] - 10, centerPos[1] - 10, 10 * len(str(self.number)) + 20, 30))
            img1 = fontPlatform.render(str(self.number), True, (200, 200, 255))
            screen.blit(img1, centerPos)

    @staticmethod
    def make_another_platform():
        posX = random.randint(DISTANCE_FROM_WALL + LEFT_LIMIT, RIGHT_LIMIT - Platform.image.get_width() - DISTANCE_FROM_WALL)
        posY = PLAYER_START_POSITION_Y - 100 * Platform.counter
        platformList.append(Platform(posX, posY))

    @staticmethod
    def make_first_platforms():
        for i in range(11):
            Platform.make_another_platform()

    @staticmethod
    def manage_platforms():
        # Dodawanie platform
        if player.y < 1500 - 100 * Platform.counter:
            Platform.make_another_platform()

        # Usuwanie platform
        for platform in platformList:
            if platform.y + offsetY > SCREEN_HEIGHT:
                platformList.remove(platform)
                global score
                score += 10
                del platform


class OffsetBackground:
    @staticmethod
    def draw(x, y, image, offsetScale=1.0):
        screen.blit(image, (x, y + (offsetScale * offsetY) % image.get_height()))
        screen.blit(image, (x, y - image.get_height() + ((offsetScale * offsetY) % image.get_height())))


def player_input():
    keys = pygame.key.get_pressed()
    if keys[K_UP] and player.canJump:
        player.jump()
    if keys[K_LEFT]:
        player.velX -= 1
    if keys[K_RIGHT]:
        player.velX += 1


def game_logic():
    player.update()


def draw_game():
    screen.fill((0, 0, 30))

    OffsetBackground.draw(LEFT_LIMIT, 0, backImage, 0.5)

    for platform in platformList:
        platform.draw()

    player.draw()

    OffsetBackground.draw(0, 0, leftWallImage, 1.3)
    OffsetBackground.draw(RIGHT_LIMIT, 0, rightWallImage, 1.3)

    # RYSOWANIE INTERFEJSU
    img1 = fontScore.render(str(score), True, (200, 200, 0))
    screen.blit(img1, (20, 20))
    screen.blit(hurryUpText, (300, hurryUpTextPosY))

def manage_offset():
    global offsetY
    global lastAccelerate
    global offsetVelocityY
    global hurryUpTextPosY
    global run

    # Przewijanie się ekranu po pierwszym większym skoku;
    if player.y < 100 and offsetY < 200:
        offsetVelocityY = 1

    # Przyspieszanie przewijania ekranu co określnony czas
    if time.time() - lastAccelerate > TIME_TO_ACCELERATE and offsetVelocityY > 0:
        offsetVelocityY += 1
        lastAccelerate = time.time()
        hurryUpTextPosY = SCREEN_HEIGHT + 100

    offsetY += offsetVelocityY

    if player.y + offsetY < 150:
        offsetY += abs(player.y + offsetY - 150) / 20

    if player.y + offsetY > SCREEN_HEIGHT:
        run = False

    hurryUpTextPosY -= 1


player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y- 200)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Icy Tower, ale to projekt testowy z Pygame')

platformList = []
Platform.make_first_platforms()
lastAccelerate = time.time()


run = True
while run:

    player_input()
    game_logic()
    manage_offset()
    Platform.manage_platforms()
    draw_game()

    # To jest TURBOWAŻNE I NIE USUWAJ TEGO!!!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # To tworzy nową klatkę gry; :)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()

