import pygame

class Button:
    def __init__(self, text, width, height, pos, elevation, textSize):
        self.keyDown = False
        self.keyUp = False

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

    def draw(self, screen):

        self.topRect.y = self.originalYPosition - self.dynamicElevation
        self.textRect.center = self.topRect.center

        self.bottomRect.midtop = self.topRect.midtop
        self.bottomRect.height = self.topRect.height + self.dynamicElevation

        pygame.draw.rect(screen, self.bottomColor, self.bottomRect, border_radius=3)
        pygame.draw.rect(screen, self.topColor, self.topRect, border_radius=3)
        screen.blit(self.textSurf, self.textRect)
        self.check_click()

    def check_click(self):
        mousePos = pygame.mouse.get_pos()
        if self.topRect.collidepoint(mousePos):
            self.topColor = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamicElevation = 0
                self.keyDown = True
            else:
                self.dynamicElevation = self.elevation
                if self.keyUp:
                    self.keyUp = False
                if self.keyDown:
                    self.keyDown = False
                    self.keyUp = True
        else:
            self.dynamicElevation = self.elevation
            self.topColor = '#475F77'
