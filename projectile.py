# projectile.py
import pygame

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        surf = pygame.image.load("assets/images/projectile.png").convert_alpha()
        self.image = pygame.transform.scale(surf, (12, 8))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 8 * direction
        self.from_boss = False  # marque para distinguir origem se necessário
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += int(self.vel)
        # remover se sair do mapa (assumir largura grande)
        if self.rect.right < -200 or self.rect.left > 3400:
            self.kill()
