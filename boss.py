# boss.py
import pygame, random
from projectile import Projetil

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load("assets/images/boss.png").convert_alpha()
        self.base = pygame.transform.scale(img, (100, 100))
        self.image = self.base.copy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.vida_max = 20
        self.vida = self.vida_max
        self.vel = 2
        self.direcao = 1
        self.atk_timer = 0

        # área de patrulha
        self.min_x = 200
        self.max_x = 2800

    def update(self, projeteis, todos):
        # movimento lateral simples
        self.rect.x += self.vel * self.direcao
        if self.rect.left < self.min_x or self.rect.right > self.max_x:
            self.direcao *= -1

        # atirar de tempos em tempos
        self.atk_timer += 1
        if self.atk_timer >= 75:
            self.atk_timer = 0
            # dispara três projéteis com spread
            for ang in (-10, 0, 10):
                proj = Projetil(self.rect.centerx, self.rect.centery - 20, 1 if self.direcao > 0 else -1)
                proj.from_boss = True
                # ajuste de velocidade lateral
                proj.vel = 6 * (1 if self.direcao > 0 else -1)
                # adiciona pequeno desvio vertical (não física) - não implementado no Projetil, mas ok
                projeteis.add(proj)
                todos.add(proj)

    def levar_dano(self, qtd=1):
        self.vida -= qtd
        if self.vida <= 0:
            self.kill()

    def desenhar_barra(self, tela):
        barra_w = 240
        barra_h = 18
        x = (tela.get_width() - barra_w) // 2
        y = 16
        pygame.draw.rect(tela, (0,0,0), (x-2, y-2, barra_w+4, barra_h+4))
        pygame.draw.rect(tela, (180,0,0), (x, y, barra_w, barra_h))
        fill_w = int(barra_w * max(0, self.vida / self.vida_max))
        pygame.draw.rect(tela, (0,200,0), (x, y, fill_w, barra_h))
