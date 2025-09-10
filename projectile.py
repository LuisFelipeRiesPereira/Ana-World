# projectile.py
import pygame

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1, speed=None, from_boss=False):
        super().__init__()
        # tenta carregar sprite; fallback simples
        try:
            surf = pygame.image.load("assets/images/projectile.png").convert_alpha()
        except Exception:
            surf = pygame.Surface((12,8), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255,180,40), surf.get_rect())
        # escala pequena
        try:
            self.image = pygame.transform.scale(surf, (12,8))
        except Exception:
            self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        # flags
        self.from_boss = bool(from_boss)
        # velocidade
        if speed is None:
            self.vel = 8 * (1 if direction >= 0 else -1)
        else:
            self.vel = float(speed) * (1 if direction >= 0 else -1)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # move horizontalmente
        self.rect.x += int(self.vel)
        # kill fora de tela (limites largos)
        if self.rect.right < -300 or self.rect.left > 5000:
            self.kill()
