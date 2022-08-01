import sys
import time

from Button import Button

from Drawables import *


class Game:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Icy Tower, ale to projekt testowy z Pygame')

    def __init__(self):
        pygame.init()

        self.starList = []
        self.offsetX = self.offsetY = 0
        self.platformList = []
        self.playerImage = 'Images/Panda.png'
        self.player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y - 100, self.playerImage, self)
        self.lastAccelerate = time.time()

        self.make_first_platforms()
        self.hurryUpTextPosY = -50

        self.run = True

        self.offsetVelocityY = 0

        self.clock = pygame.time.Clock()

        # SCORE
        self.score = 0

        self.audioMixer = pygame.mixer
        self.audioMixer.init()
        self.audioMixer.music.set_volume(0.3)
        self.audioMixer.music.load('Audio/TestMusic.mp3')
        self.audioMixer.music.play(-1)

        # IMAGES:
        self.leftWallImage = pygame.image.load('Images/LeftWall.png')
        self.rightWallImage = pygame.transform.flip(self.leftWallImage, True, False)
        self.backImage = pygame.image.load('Images/BackWall.png')

        self.fontPlatform = pygame.font.SysFont('Arial', 14)
        self.fontScore = pygame.font.SysFont('Arial', 48)

        self.hurryUpText = self.fontScore.render("HURRY UP!!!", True, (200, 200, 0))

    def make_another_platform(self):
        posX = random.randint(DISTANCE_FROM_WALL + LEFT_LIMIT,
                              RIGHT_LIMIT - Platform.image.get_width() - DISTANCE_FROM_WALL)
        posY = PLAYER_START_POSITION_Y - 100 * Platform.counter
        self.platformList.append(Platform(posX, posY, self))

    def make_first_platforms(self):
        for i in range(11):
            self.make_another_platform()

    def manage_platforms(self):
        if self.player.y < 1500 - 100 * Platform.counter:
            self.make_another_platform()

        for platform in self.platformList:
            if platform.y + self.offsetY > SCREEN_HEIGHT:
                self.platformList.remove(platform)
                self.score += 10
                del platform

    def drawTiled(self, x, y, image, offsetScale=1.0):
        self.screen.blit(image, (x, y + (offsetScale * self.offsetY) % image.get_height()))
        self.screen.blit(image, (x, y - image.get_height() + ((offsetScale * self.offsetY) % image.get_height())))

    def start_game(self):
        self.player = Player(SCREEN_WIDTH / 2, PLAYER_START_POSITION_Y - 100, self.playerImage, self)
        self.lastAccelerate = time.time()
        self.offsetX = 0
        self.offsetY = 0
        self.platformList = []
        self.starList = []
        Platform.counter = 0
        self.make_first_platforms()
        self.hurryUpTextPosY = -50
        self.offsetVelocityY = 0

        self.score = 0
        self.run = True

    def game_loop(self):
        self.player_input()
        self.game_logic()
        self.draw_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                pygame.quit()
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
        self.drawTiled(LEFT_LIMIT, 0, self.backImage, 0.5)

        for platform in self.platformList:
            platform.draw(self)

        self.player.draw(self)

        for star in self.starList:
            star.draw(self)

        self.drawTiled(0, 0, self.leftWallImage, 1.3)
        self.drawTiled(RIGHT_LIMIT, 0, self.rightWallImage, 1.3)

        # RYSOWANIE INTERFEJSU
        img1 = self.fontScore.render(str(self.score), True, (200, 200, 0))
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

        self.offsetY += self.offsetVelocityY

        if self.player.y + self.offsetY < 150:
            self.offsetY += abs(self.player.y + self.offsetY - 150) / 20

        if self.player.y + self.offsetY > SCREEN_HEIGHT:
            self.run = False

        self.hurryUpTextPosY -= 1

    def play_game_scene(self):
        self.start_game()
        while self.run:
            self.game_loop()

    def play_menu_scene(self):
        Game.offsetY = 0
        self.player.angle = 0
        menuButtons = []

        menuButtons.append(Button("Start", 400, 80, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 200 + 40), 6, 32))
        menuButtons.append(Button("Options", 400, 80, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 200 + 150), 6, 32))
        menuButtons.append(Button("Quit", 400, 80, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 200 + 260), 6, 32))

        randomPosList = []
        for i in range(5):
            randomPos = (random.randint(50, SCREEN_WIDTH - 150), random.randint(150, SCREEN_HEIGHT - 50))
            randomPosList.append(randomPos)

        run = True
        while run:

            self.screen.fill((75, 192, 219))

            self.screen.blit(pygame.image.load('Images/BigPanda.png'), (50, 100))
            self.screen.blit(pygame.image.load('Images/BigPanda.png'), (SCREEN_WIDTH - 300, 100))

            self.screen.blit(pygame.image.load('Images/Cyberpaka Big.png'), (50, 300))
            self.screen.blit(pygame.image.load('Images/Cyberpaka Big.png'), (SCREEN_WIDTH - 300, 300))

            self.screen.blit(pygame.transform.rotozoom(pygame.image.load('Images/IcyTowerText.png'), 3, 1.), (200, 30))
            self.screen.blit(pygame.image.load('Images/cyberpakaText.png'), (250, 110))

            for button in menuButtons:
                button.draw(self.screen)

            if menuButtons[0].keyUp:
                self.play_game_scene()
            if menuButtons[1].keyUp:
                self.play_options_scene()
            if menuButtons[2].keyUp:
                pygame.quit()
                sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.clock.tick(FPS)
            pygame.display.update()

    def play_options_scene(self):
        menuButtons = []
        menuButtons.append(Button("Pandeusz", 500, 60, (SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 300 + 40), 6, 32))
        menuButtons.append(Button("Stickman", 500, 60, (SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 300 + 120), 6, 32))
        menuButtons.append(
            Button("CyberPakuś", 500, 60, (SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 300 + 200), 6, 32))
        menuButtons.append(Button("Back", 500, 60, (SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 300 + 280), 6, 32))

        while True:

            self.screen.fill((random.randint(0, 10), 0, 0))

            for button in menuButtons:
                button.draw(self.screen)

            self.player.x, self.player.y = SCREEN_WIDTH - 200, 100
            self.player.image = pygame.transform.rotozoom(pygame.image.load(self.playerImage), 0, 2.)
            self.player.draw(self)

            if menuButtons[0].keyUp:
                self.playerImage = "Images/Panda.png"
            if menuButtons[1].keyUp:
                self.playerImage = "Images/Stickman.png"
            if menuButtons[2].keyUp:
                self.playerImage = "Images/Cyberpakuś.png"
            if menuButtons[3].keyUp:
                self.play_menu_scene()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(FPS)
            pygame.display.update()
