# menu.py
import pygame, math, time
from settings import LARGURA, ALTURA, PRETO, BRANCO
from ui import Botao

def mostrar_menu(tela, clock, volume_atual=0.5, modo="start"):
    fonte_titulo = pygame.font.SysFont(None, 72)
    fonte_small = pygame.font.SysFont(None, 28)

    # Botões simples
    if modo == "start":
        start_btn = Botao(LARGURA//2 - 100, ALTURA//2 + 40, 200, 50, "Start")
    else:
        start_btn = Botao(LARGURA//2 - 100, ALTURA//2 + 40, 200, 50, "Resume")
    quit_btn = Botao(LARGURA//2 - 100, ALTURA//2 + 110, 200, 50, "Quit")

    slider_rect = pygame.Rect(LARGURA//2 - 100, ALTURA//2 + 180, 200, 10)
    knob_x = slider_rect.x + int(slider_rect.width * volume_atual)

    t0 = time.time()
    rodando = True
    novo_vol = volume_atual
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit", novo_vol
            if start_btn.clicado(evento):
                return "start", novo_vol
            if quit_btn.clicado(evento):
                return "quit", novo_vol
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if slider_rect.collidepoint(evento.pos):
                    knob_x = max(slider_rect.x, min(evento.pos[0], slider_rect.right))
                    novo_vol = (knob_x - slider_rect.x) / slider_rect.width

        # animação senoidal do título
        elapsed = time.time() - t0
        offset = int(22 * math.sin(elapsed * 1.6))

        tela.fill(BRANCO)
        título = fonte_titulo.render("Ana's World", True, PRETO)
        rect = título.get_rect(center=(LARGURA//2 + offset, ALTURA//3))
        tela.blit(título, rect)

        start_btn.desenhar(tela)
        quit_btn.desenhar(tela)

        # slider
        pygame.draw.rect(tela, PRETO, slider_rect, 2)
        pygame.draw.rect(tela, (200,200,200), (slider_rect.x, slider_rect.y, slider_rect.width, slider_rect.height))
        pygame.draw.rect(tela, (120,120,255), (knob_x-6, slider_rect.y-6, 12, slider_rect.height+12))

        instr = fonte_small.render("Use ARROWS to move, SPACE to jump, X to shoot", True, PRETO)
        tela.blit(instr, (LARGURA//2 - instr.get_width()//2, ALTURA//2 - 40))

        pygame.display.update()
        clock.tick(60)
