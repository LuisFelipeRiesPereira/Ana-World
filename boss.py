# boss.py
import pygame, random, math, os
from projectile import Projetil

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img_path = "assets/images/boss.png"
        if os.path.exists(img_path):
            self.base_image = pygame.image.load(img_path).convert_alpha()
        else:
            self.base_image = pygame.Surface((100,100), pygame.SRCALPHA)
            pygame.draw.circle(self.base_image, (120,0,200), (50,50), 50)

        self.base_image = pygame.transform.scale(self.base_image, (100,100))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x,y))
        self.mask = pygame.mask.from_surface(self.image)

        self.vida = 20  # 🔥 menos vida no boss
        self.float_phase = 0
        self.shoot_cd = 90
        self.teleport_cd = 160
        self.teleporting = False
        self.teleport_phase = 0
        self.teleport_targets = [(x, y), (x + 400, y)]
        self.current_target = 0

    def update(self, projeteis, todos):
        self.float_phase += 0.06
        float_offset = int(6 * math.sin(self.float_phase))

        self.teleport_cd -= 1
        if self.teleport_cd <= 0 and not self.teleporting:
            self.teleporting = True
            self.teleport_phase = 0

        if self.teleporting:
            self.teleport_phase += 1
            if self.teleport_phase <= 15:
                scale = 1 - (self.teleport_phase / 15.0)
                self._set_scaled(scale)
            elif self.teleport_phase == 16:
                self.current_target = 1 - self.current_target
                tx, ty = self.teleport_targets[self.current_target]
                self.rect.topleft = (tx, ty)
            elif 17 <= self.teleport_phase <= 32:
                scale = (self.teleport_phase - 16) / 16.0
                self._set_scaled(scale)
            else:
                self.teleporting = False
                self.teleport_cd = random.randint(120, 220)
                self._set_scaled(1.0)

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            dir_choice = random.choice([-1, 1])
            proj = Projetil(self.rect.centerx, self.rect.centery, dir_choice, from_boss=True)
            proj.vel = 6 * dir_choice
            projeteis.add(proj); todos.add(proj)
            self.shoot_cd = random.randint(60, 120)

    def _set_scaled(self, scale):
        scale = max(0.01, scale)
        w, h = self.base_image.get_size()
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        self.image = pygame.transform.smoothscale(self.base_image, (nw, nh))
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def levar_dano(self, qtd=1):
        self.vida -= qtd
        if self.vida <= 0:
            self.kill()

    def desenhar_barra(self, tela):
        bar_w, bar_h = 220, 16
        x, y = (tela.get_width() - bar_w)//2, 10
        pygame.draw.rect(tela, (0,0,0), (x-2,y-2,bar_w+4,bar_h+4))
        pygame.draw.rect(tela, (200,0,0), (x,y, bar_w, bar_h))
        fill = int(bar_w * max(0, self.vida / 20))  # 🔥 vida ajustada
        pygame.draw.rect(tela, (0,200,0), (x,y, fill, bar_h))
