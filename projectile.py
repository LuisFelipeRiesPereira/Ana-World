# projectile.py
import pygame

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        try:
            surf = pygame.image.load("assets/images/projectile.png").convert_alpha()
        except Exception:
            surf = pygame.Surface((12,8), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255,180,40), surf.get_rect())
        self.image = pygame.transform.scale(surf, (12,8))
        self.rect = self.image.get_rect(center=(x,y))
        self.vel = 8 * (1 if direction>=0 else -1)
        self.from_boss = False
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.rect.x += int(self.vel)
        if self.rect.right < -200 or self.rect.left > 3800:
            self.kill()
