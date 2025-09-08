# ui.py
import pygame

class Botao:
    def __init__(self, x, y, largura, altura, texto):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.fonte = pygame.font.SysFont(None, 30)
        self.cor_normal = (200,200,200)
        self.cor_hover = (160,160,160)

    def desenhar(self, tela):
        mouse = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse) else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect)
        pygame.draw.rect(tela, (0,0,0), self.rect, 2)
        txt = self.fonte.render(self.texto, True, (0,0,0))
        tela.blit(txt, (self.rect.x + (self.rect.width - txt.get_width())//2,
                        self.rect.y + (self.rect.height - txt.get_height())//2))

    def clicado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False
