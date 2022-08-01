import random

import pygame
from pygame.locals import *
from constants import *

fontPlatform = pygame.font.SysFont('Arial', 14)

class Drawable:

    def __init__(self, x, y, imageLocation):
        self.x, self.y = x, y
        self.image = pygame.image.load(imageLocation)
        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.angle = 0
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self, game):
        imageToBlit = pygame.transform.rotate(self.image, self.angle)
        game.screen.blit(imageToBlit, (self.x + game.offsetX, self.y + game.offsetY))


class Player(Drawable):
    def __init__(self, x, y, imageLocation="Images/Panda.png", game=None):
        super().__init__(x, y, imageLocation)
        self.game = game
        self.velX = self.velY = self.angle = 0
        self.canJump, self.rotating = False, False

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
        self.check_collision(self.game.platformList)

        if self.rotating:
            self.angle += 10
            for i in range(3):
                self.game.starList.append(ParticleStar(self.x, self.y, self.velX, self.velY, self.game))
        else:
            self.angle = 0

    def jump(self):
        self.velY = - (16 + 1.2 * abs(self.velX))
        self.canJump = False
        if self.velY < -25:
            self.rotating = True
            self.game.audioMixer.Sound.play(self.jumpSounds[1])
        else:
            self.game.audioMixer.Sound.play(self.jumpSounds[0])

    def draw(self, game):
        super().draw(game)


class Platform(Drawable):
    image = pygame.image.load("Images/Platform.png")
    counter = 0

    def __init__(self, x, y, game=None):

        Platform.counter += 1
        self.number = Platform.counter

        super().__init__(x, y, "Images/Platform.png")
        self.game = game
        if self.number == 1 or self.number % 50 == 0:
            self.image = pygame.transform.scale(pygame.image.load("Images/Platform.png"),
                                                (RIGHT_LIMIT - LEFT_LIMIT, self.image.get_height()))
            self.x = LEFT_LIMIT

        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self, game):

        super().draw(game)

        if self.number % 10 == 0:
            centerPos = (self.x + self.width / 2 + self.game.offsetX, self.y + self.height / 2 + self.game.offsetY)
            pygame.draw.rect(self.game.screen, (10, 10, 10),
                             Rect(centerPos[0] - 10, centerPos[1] - 10, 10 * len(str(self.number)) + 20, 30))
            img1 = fontPlatform.render(str(self.number), True, (200, 200, 255))
            self.game.screen.blit(img1, centerPos)


class ParticleStar(Drawable):
    def __init__(self, x, y, startVelX, startVelY, game):
        super().__init__(x, y, f'Images/Star_{random.randint(1, 3)}.png')
        self.game = game
        self.velX, self.velY = startVelX + random.randint(-3, 5), startVelY + random.randint(-3, 5)

    def move(self):
        self.velY += GRAVITY / 4

        self.velX *= 0.95
        self.velY *= 0.98

        self.x += self.velX
        self.y += self.velY

        if self.y + self.game.offsetY > SCREEN_HEIGHT:
            self.game.starList.remove(self)
            del self

    def draw(self, game):
        super().draw(game)
