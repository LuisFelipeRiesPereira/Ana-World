# platform.py
import pygame, os

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image_path=None):
        """
        Plataforma que repete (tile) a imagem horizontalmente para evitar distorção.
        x,y = posição; w,h = dimensão desejada; image_path opcional.
        """
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)

        if image_path and os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            # queremos que a altura do tile fique = h, então escalamos a imagem proporcionalmente pela altura
            ih = img.get_height()
            iw = img.get_width()
            if ih != h:
                scale_ratio = h / ih 
                new_w = max(1, int(iw * scale_ratio))
                img = pygame.transform.scale(img, (new_w, h))
                iw = img.get_width()
                ih = img.get_height()
            # agora criamos uma surface w x h e blitamos o tile repetido horizontalmente
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            x_off = 0
            while x_off < w:
                surf.blit(img, (x_off, 0))
                x_off += iw
            self.image = surf
        else:
            # fallback simples (sem tile)
            surf = pygame.Surface((w, h))
            surf.fill((100, 180, 100))
            self.image = surf

        self.mask = pygame.mask.from_surface(self.image)
