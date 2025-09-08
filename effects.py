# effects.py
import pygame, random

class Particula(pygame.sprite.Sprite):
    def __init__(self, x, y, cor=(200,200,200), direcao=(0, -2)):
        super().__init__()
        self.image = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, cor, (2,2), 2)
        self.rect = self.image.get_rect(center=(x,y))
        self.vel = [direcao[0] + random.uniform(-1.8,1.8), direcao[1] + random.uniform(-2,-0.5)]
        self.timer = 28

    def update(self):
        self.rect.x += int(self.vel[0])
        self.rect.y += int(self.vel[1])
        self.vel[1] += 0.4
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
