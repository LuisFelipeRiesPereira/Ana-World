# enemy.py
import pygame

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__()
        img = pygame.image.load("assets/images/enemy.png").convert_alpha()
        self.base_image = pygame.transform.scale(img, (36, 36))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.vel = 2
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir

        self.morrendo = False
        self.fade_timer = 18

    def update(self):
        if self.morrendo:
            self._process_death()
            return
        self.rect.x += self.vel
        if self.rect.left < self.limite_esq or self.rect.right > self.limite_dir:
            self.vel *= -1
        self.mask = pygame.mask.from_surface(self.image)

    def morrer(self):
        if not self.morrendo:
            self.morrendo = True
            self.fade_timer = 18

    def _process_death(self):
        t = max(1, self.fade_timer)
        fator = t / 18.0
        w, h = self.base_image.get_size()
        new_w = max(1, int(w * fator))
        new_h = max(1, int(h * fator))
        center = self.rect.center
        self.image = pygame.transform.scale(self.base_image, (new_w, new_h))
        self.rect = self.image.get_rect(center=center)
        self.image.set_alpha(120 if (self.fade_timer % 4 < 2) else 255)
        self.mask = pygame.mask.from_surface(self.image)
        self.fade_timer -= 1
        if self.fade_timer <= 0:
            self.kill()
