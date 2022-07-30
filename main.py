import time
import pygame
from pygame.locals import *
from pygame import mixer
import random

from constants import *

import sys

# IMAGES:
leftWallImage = pygame.image.load('Images/LeftWall.png')
rightWallImage = pygame.transform.flip(leftWallImage, True, False)
backImage = pygame.image.load('Images/BackWall.png')

pygame.init()
fontPlatform = pygame.font.SysFont('Arial', 14)
fontScore = pygame.font.SysFont('Arial', 48)


class Drawable:

    def __init__(self, x, y, image):
        self.x, self.y = x, y
        self.image = pygame.image.load(image)
        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.angle = 0
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        Game.screen.blit(pygame.transform.rotate(self.image, self.angle),
                         (self.x + Game.offsetX, self.y + Game.offsetY))


class Player(Drawable):
    def __init__(self, x, y):
        super().__init__(x, y, 'Images/Panda.png')

        self.velX, self.velY = 0, 0
        self.canJump, self.rotating = False, False

        self.angle = 0
        self.lastX, self.lastY = self.x, self.y
        self.jumpSounds = (pygame.mixer.Sound("Audio/Light_Jump.wav"), pygame.mixer.Sound("Audio/Hard_Jump.wav"))

    def move(self):
        self.lastX, self.lastY = self.x, self.y

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
        self.canJump = False
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
            for i in range(3):
                Game.starList.append(ParticleStar(self.x, self.y, self.velX, self.velY))
        else:
            self.angle = 0

    def jump(self):
        self.velY = - (16 + 1.2 * abs(self.velX))
        self.canJump = False
        if self.velY < -25:
            self.rotating = True
            mixer.Sound.play(self.jumpSounds[1])
        else:
            mixer.Sound.play(self.jumpSounds[0])

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

        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self):

        super().draw()

        if self.number % 10 == 0:
            centerPos = (self.x + self.width / 2 + Game.offsetX, self.y + self.height / 2 + Game.offsetY)
            pygame.draw.rect(Game.screen, (10, 10, 10),
                             Rect(centerPos[0] - 10, centerPos[1] - 10, 10 * len(str(self.number)) + 20, 30))
            img1 = fontPlatform.render(str(self.number), True, (200, 200, 255))
            Game.screen.blit(img1, centerPos)


class ParticleStar(Drawable):
    def __init__(self, x, y, startVelX, startVelY):
        super().__init__(x, y, f'Images/Star_{random.randint(1, 3)}.png')

        self.velX, self.velY = startVelX + random.randint(-5, 5), startVelY + random.randint(-5, 5)

    def move(self):
        self.velY += GRAVITY / 5

        self.velX *= 0.95
        self.velY *= 0.94

        self.x += self.velX
        self.y += self.velY

        if self.y + Game.offsetY > SCREEN_HEIGHT:
            Game.starList.remove(self)
            del self

    def draw(self):
        super().draw()


class Button:
    def __init__(self, text, width, height, pos, elevation, textSize):
        self.pressed = False
        self.clicked = False

        self.elevation = elevation
        self.dynamicElevation = elevation
        self.originalYPosition = pos[1]

        self.topRect = pygame.Rect(pos, (width, height))
        self.topColor = "#475F77"

        self.bottomRect = pygame.Rect(pos, (width, height))
        self.bottomColor = "#354B5E"
        self.FONT = pygame.font.SysFont("comicsans", textSize)

        self.textSurf = self.FONT.render(f"  {text}  ", True, "#FFFFFF")
        self.textRect = self.textSurf.get_rect(center=self.topRect.center)

    def draw(self):
        self.topRect.y = self.originalYPosition - self.dynamicElevation
        self.textRect.center = self.topRect.center

        self.bottomRect.midtop = self.topRect.midtop
        self.bottomRect.height = self.topRect.height + self.dynamicElevation

        pygame.draw.rect(Game.screen, self.bottomColor, self.bottomRect, border_radius=3)
        pygame.draw.rect(Game.screen, self.topColor, self.topRect, border_radius=3)
        Game.screen.blit(self.textSurf, self.textRect)
        self.check_click()

    def check_click(self):
        mousePos = pygame.mouse.get_pos()
        if self.topRect.collidepoint(mousePos):
            self.topColor = '#D74B4B'
            if self.clicked:
                self.clicked = False
            if pygame.mouse.get_pressed()[0]:
                self.dynamicElevation = 0
                if not self.pressed:
                    self.clicked = True
                self.pressed = True
            elif self.pressed:
                self.pressed = False
            else:
                self.dynamicElevation = self.elevation
        else:

            self.topColor = "#475F77"


class Game:
    offsetX = 0
    offsetY = 0

    platformList = []
    starList = []
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Icy Tower, ale to projekt testowy z Pygame')

    pygame.mixer.init()
    mixer.music.set_volume(0.3)
    mixer.music.load('Audio/TestMusic.mp3')

    mixer.music.play(-1)

    def __init__(self):
        self.player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y - 100)
        self.lastAccelerate = time.time()

        self.make_first_platforms()
        self.hurryUpTextPosY = -50

        self.run = True
        self.hurryUpText = fontScore.render("HURRY UP!!!", True, (200, 200, 0))
        self.offsetVelocityY = 0

        self.clock = pygame.time.Clock()

        # SCORE
        self.score = 0

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
                self.score += 10
                del platform

    def drawTiled(self, x, y, image, offsetScale=1.0):
        self.screen.blit(image, (x, y + (offsetScale * Game.offsetY) % image.get_height()))
        self.screen.blit(image, (x, y - image.get_height() + ((offsetScale * Game.offsetY) % image.get_height())))

    def start_game(self):
        self.player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y - 100)
        self.lastAccelerate = time.time()
        Game.offsetX = 0
        Game.offsetY = 0
        Game.platformList = []
        Platform.counter = 0
        self.make_first_platforms()
        self.hurryUpTextPosY = -50

        self.offsetVelocityY = 0

        # SCORE
        self.score = 0
        self.run = True


        Game.starList = []

    def game_loop(self):
        self.player_input()
        self.game_logic()
        self.draw_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                sys.exit()

        pygame.display.update()
        self.clock.tick(FPS)

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
        for star in self.starList:
            star.move()

    def draw_game(self):
        self.screen.fill((0, 0, 30))
        self.drawTiled(LEFT_LIMIT, 0, backImage, 0.5)

        for platform in self.platformList:
            platform.draw()

        self.player.draw()

        for star in self.starList:
            star.draw()

        self.drawTiled(0, 0, leftWallImage, 1.3)
        self.drawTiled(RIGHT_LIMIT, 0, rightWallImage, 1.3)

        # RYSOWANIE INTERFEJSU
        img1 = fontScore.render(str(self.score), True, (200, 200, 0))
        self.screen.blit(img1, (20, 20))

        self.screen.blit(self.hurryUpText, (300, self.hurryUpTextPosY))

    def manage_offset(self):
        # Start Scroll Screen after first bigger jump
        if self.player.y < 100 and self.offsetY < 200:
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

    def main(self):
        self.start_game()
        while self.run:
            self.game_loop()
        self.menu()

    def menu(self):
        menuButtons = []
        menuButtons.append(Button("Start", 500, 100, (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 300 + 40), 6, 32))
        menuButtons.append(Button("Options", 500, 100, (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 300 + 150), 6, 32))
        menuButtons.append(Button("Quit", 500, 100, (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 300 + 260), 6, 32))

        randomPosList = []
        for i in range(5):
            randomPos = (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50))
            randomPosList.append(randomPos)

        while True:

            self.screen.fill((random.randint(0, 10), 0, 0))

            for i in range(5):
                self.screen.blit(pygame.image.load('Images/BigPanda.png'), randomPosList[i])

            for button in menuButtons:
                button.draw()



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if menuButtons[0].clicked:
                self.main()
            if menuButtons[1].clicked:
                pass
            if menuButtons[2].clicked:
                pygame.quit()

            self.clock.tick(FPS)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()

    game.menu()
