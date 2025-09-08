# platform.py
import pygame

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image_path=None):
        super().__init__()
        if image_path:
            img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (w, h))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill((100,300,100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # plataformas simples não precisam de mask (pode ter)
        self.mask = pygame.mask.from_surface(self.image)
