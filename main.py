import time
import pygame
from pygame.locals import *
import random


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load('Images/Hero.png')
        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.velX = 0
        self.velY = 0
        self.canJump = False

    def move(self):
        self.velY += 0.5

        # Dodanie siły oporu:
        self.velX *= 0.98
        self.velY *= 0.98

        self.x += self.velX
        self.y += self.velY

        # Sprawdzanie, czy gracz nie wyszedł poza ekran;
        if self.x < LEFT_LIMIT:
            self.x = LEFT_LIMIT
            self.velX *= -1

        if self.x > RIGHT_LIMIT - self.image.get_width():
            self.x = RIGHT_LIMIT - self.image.get_width()
            self.velX *= -1

        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def draw(self):
        screen.blit(self.image, (self.x + offsetX, self.y + offsetY))


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

        self.Rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height() / 10)

    def draw(self):

        screen.blit(self.image, (self.x + offsetX, self.y + offsetY))

        if self.number % 10 == 0:
            img1 = fontPlatform.render(str(self.number), True, (200, 200, 255))
            screen.blit(img1,
                        (self.x + self.image.get_width() / 2 + offsetX, self.y + self.image.get_height() / 2 + offsetY))


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

LEFT_LIMIT = 100
RIGHT_LIMIT = SCREEN_WIDTH - 100

player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

# Rozpoczyna działanie PyGame
pygame.init()



def keyboard_steering():
    keys = pygame.key.get_pressed()
    if keys[K_UP] and player.canJump:
        player.velY = - (10 + 0.7 * abs(player.velX))
        player.canJump = False
    if keys[K_LEFT]:
        player.velX -= 1
    if keys[K_RIGHT]:
        player.velX += 1

def player_movement():
    player.move()

def draw_game():
    screen.fill((0, 0, 30))

    screen.blit(backImage, (LEFT_LIMIT, (0.5 * offsetY) % backImage.get_height()))
    screen.blit(backImage, (LEFT_LIMIT, -backImage.get_height() + ((0.5 * offsetY) % backImage.get_height())))

    player.draw()

    for platform in platformList:
        platform.draw()

    screen.blit(leftWallImage, (0, (1.3 * offsetY) % leftWallImage.get_height()))
    screen.blit(leftWallImage, (RIGHT_LIMIT, (1.3 * offsetY) % leftWallImage.get_height()))

    screen.blit(leftWallImage, (0, -leftWallImage.get_height() + ((1.3 * offsetY) % leftWallImage.get_height())))
    screen.blit(leftWallImage,
                (RIGHT_LIMIT, -leftWallImage.get_height() + ((1.3 * offsetY) % leftWallImage.get_height())))

    img1 = fontScore.render(str(score), True, (200, 200, 0))
    screen.blit(img1, (20, 20))
    screen.blit(hurryUpText, (300, hurryUpTextPosY))




fontPlatform = pygame.font.SysFont('Arial', 12)
fontScore = pygame.font.SysFont('Arial', 48)

score = 0

# Dzięki tym dwóm linijkom mamy stałe 60 klatek na sekundę;
clock = pygame.time.Clock()
fps = 60

timeToAccelerate = 30
lastAccelerate = time.time()

# Parametry okna zapisane do zmiennych:



screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Gierka')



platformList = []

for i in range(10):
    posX = random.randint(10 + LEFT_LIMIT, RIGHT_LIMIT - Platform.image.get_width() - 10)
    posY = (SCREEN_HEIGHT - 100) - 100 * Platform.counter
    platformList.append(Platform(posX, posY))

offsetX = 0
offsetY = 0

offsetVelocityY = 0

leftWallImage = pygame.image.load('Images/LeftWall.png')
backImage = pygame.image.load('Images/BackWall.png')

hurryUpText = fontScore.render("HURRY UP!!!", True, (200, 200, 0))
hurryUpTextPosY = -50

run = True
while run:

    # Zegar gry
    clock.tick(fps)
    keyboard_steering()
    player_movement()



    # Kolizje platformy i gracza

    for platform in platformList:
        if player.rect.colliderect(platform.Rect) and player.velY > 0:
            player.y = platform.y - player.image.get_height()
            player.velY = 0
            player.velX *= 0.95
            canJump = True

    # Przewijanie się ekranu po pierwszym większym skoku;
    if player.y < 100 and offsetY < 200:
        offsetVelocityY = 1

    # Przyspieszanie przewijania ekranu co określnony czas
    if time.time() - lastAccelerate > timeToAccelerate and offsetVelocityY > 0:
        offsetVelocityY += 1
        lastAccelerate = time.time()
        hurryUpTextPosY = SCREEN_HEIGHT + 100


    offsetY += offsetVelocityY

    if player.y + offsetY < 250:
        offsetY += abs(player.y + offsetY - 250) / 30

    if player.y + offsetY > SCREEN_HEIGHT:
        run = False


    # Dodawanie platform
    if player.y < 1200 - 100 * Platform.counter:
        posX = random.randint(10 + LEFT_LIMIT, RIGHT_LIMIT - Platform.image.get_width() - 10)
        posY = 500 - 100 * Platform.counter
        platformList.append(Platform(posX, posY))

    # Usuwanie platform
    for platform in platformList:
        if platform.y + offsetY > SCREEN_HEIGHT:
            platformList.remove(platform)
            score += 10


    hurryUpTextPosY -= 1



    # Rysowane obiektów na ekranie
    draw_game()

    # To jest TURBOWAŻNE I NIE USUWAJ TEGO!!!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # To tworzy nową klatkę gry; :)
    pygame.display.update()

pygame.quit()
