# boss.py
import pygame, random, math
from projectile import Projetil

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [pygame.Surface((80,80), pygame.SRCALPHA)]
        pygame.draw.circle(self.frames[0], (120,0,200), (40,40), 40)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x,y))
        self.mask = pygame.mask.from_surface(self.image)
        self.vida = 40
        self.min_x = x-200
        self.max_x = x+200
        self.dir = 1
        self.float_phase = 0
        self.shoot_cd = 90

    def update(self, projeteis, todos):
        self.float_phase += 0.05
        self.rect.y += int(2 * math.sin(self.float_phase))
        if random.random() < 0.02:
            self.dir *= -1
        self.rect.x += self.dir * 2
        self.rect.x = max(self.min_x, min(self.rect.x, self.max_x))
        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            proj = Projetil(self.rect.centerx, self.rect.centery, self.dir)
            projeteis.add(proj); todos.add(proj)
            self.shoot_cd = random.randint(60,120)

    def levar_dano(self, qtd=1):
        self.vida -= qtd
        if self.vida <= 0:
            self.kill()

    def desenhar_barra(self, tela):
        bar_w, bar_h = 200, 16
        x, y = 20, 20
        pygame.draw.rect(tela, (0,0,0), (x-2,y-2,bar_w+4,bar_h+4))
        pygame.draw.rect(tela, (200,0,0), (x,y, bar_w, bar_h))
        pygame.draw.rect(tela, (0,200,0), (x,y, int(bar_w * (self.vida/40)), bar_h))
