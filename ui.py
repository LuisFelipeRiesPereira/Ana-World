# ui.py
import pygame

class Botao:
    def __init__(self, x, y, largura, altura, texto):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.fonte = pygame.font.SysFont(None, 28)
        self.cor_normal = (80, 80, 80)
        self.cor_hover = (120, 120, 120)
        self.cor_texto = (255, 255, 255)

    def desenhar(self, tela):
        cor = self.cor_hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect, border_radius=8)
        pygame.draw.rect(tela, (0, 0, 0), self.rect, 2, border_radius=8)
        txt = self.fonte.render(self.texto, True, self.cor_texto)
        tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def clicado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False
