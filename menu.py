# menu.py
import pygame, math, time
from settings import *
from ui import Botao

def mostrar_menu(tela, clock, volume_atual=0.5, modo="start"):
    fonte_titulo = pygame.font.SysFont(None, 72)
    fonte_small = pygame.font.SysFont(None, 24)
    start_btn = Botao(LARGURA//2 - 100, ALTURA//2 + 30, 200, 48, "Start")
    quit_btn  = Botao(LARGURA//2 - 100, ALTURA//2 + 96, 200, 48, "Quit")
    slider_rect = pygame.Rect(LARGURA//2 - 100, ALTURA//2 + 170, 200, 10)
    knob_x = slider_rect.x + int(slider_rect.width * volume_atual)
    t0 = time.time()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit", volume_atual
            if start_btn.clicado(ev):
                return "start", volume_atual
            if quit_btn.clicado(ev):
                return "quit", volume_atual
            if ev.type == pygame.MOUSEBUTTONDOWN and slider_rect.collidepoint(ev.pos):
                knob_x = ev.pos[0]
                volume_atual = (knob_x - slider_rect.x) / slider_rect.width
                volume_atual = max(0, min(1, volume_atual))
                pygame.mixer.music.set_volume(volume_atual)

        tela.fill(BRANCO)
        elapsed = time.time() - t0
        offset = int(24 * math.sin(elapsed * 1.6))
        titulo = fonte_titulo.render("Ana's World", True, PRETO)
        rect = titulo.get_rect(center=(LARGURA//2 + offset, ALTURA//3))
        tela.blit(titulo, rect)

        start_btn.desenhar(tela)
        quit_btn.desenhar(tela)

        pygame.draw.rect(tela, (220,220,220), slider_rect)
        pygame.draw.rect(tela, PRETO, slider_rect, 2)
        pygame.draw.rect(tela, (120,120,255), (knob_x-8, slider_rect.y-8, 16, slider_rect.height+16))

        instr = fonte_small.render("Arrows: mover — SPACE: pular — X: atirar", True, PRETO)
        tela.blit(instr, (LARGURA//2 - instr.get_width()//2, ALTURA//2 - 40))

        pygame.display.update()
        clock.tick(FPS)
