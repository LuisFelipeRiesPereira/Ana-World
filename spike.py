# spike.py
import pygame

class Espinho(pygame.sprite.Sprite):
    def __init__(self, x, chao_topo_y):
        super().__init__()
        img = pygame.image.load("assets/images/spike.png").convert_alpha()
        # padroniza o tamanho (ajuste se sua arte tem outro tamanho)
        self.image = pygame.transform.scale(img, (36, 28))
        self.rect = self.image.get_rect()
        # alinhar a base do espinho ao topo do chão (midbottom)
        self.rect.midbottom = (x, chao_topo_y)
        self.mask = pygame.mask.from_surface(self.image)
