# main.py
import pygame
import random
import math
import os
from settings import *
from player import Jogador
from platform import Plataforma
from item import Item, PowerUp
from enemy import Inimigo
from spike import Espinho
from projectile import Projetil
from ui import Botao
from menu import mostrar_menu
from boss import Boss

# -----------------------
# Audio manager (global)
# -----------------------
current_music = None
music_volume = 0.5
camera_shake = 0

def init_audio():
    # tenta iniciar o mixer com tolerância (evita crash se não puder)
    try:
        pygame.mixer.init()
    except Exception as e:
        print("Aviso: mixer init falhou:", e)

def play_music(path, volume=0.5, force=False):
    """
    Toca a música se e somente se for diferente da atual, a não ser que force=True.
    Atualiza current_music e volume global.
    """
    global current_music, music_volume
    music_volume = volume
    if not pygame.mixer.get_init():
        return
    if current_music == path and not force:
        pygame.mixer.music.set_volume(music_volume)
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
        current_music = path
    except Exception as e:
        print("Erro ao tocar música:", e)

def stop_music():
    global current_music
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    current_music = None

# -----------------------
# Transition, Menus, Helpers
# -----------------------
def mostrar_transicao(tela, clock, nivel):
    """Texto LEVEL X entra do topo, pausa e sai - com leve bounce"""
    fonte = pygame.font.SysFont(None, 72, bold=True)
    texto_surf = fonte.render(f"LEVEL {nivel}", True, PRETO)
    center_x = LARGURA // 2
    # anim frames
    frames = int(1.2 * FPS)
    for f in range(frames):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
        tela.fill(BRANCO)
        # y: entra (0..frames//3) -> fica -> sai
        if f < frames // 3:
            t = f / (frames // 3)
            y = int(-120 + t * (ALTURA // 3 + 120))
        elif f > 2 * frames // 3:
            t = (f - 2 * frames // 3) / (frames // 3)
            y = int(ALTURA // 3 + t * (ALTURA // 2))
        else:
            y = ALTURA // 3
        # slight scale bounce
        scale = 1.0 + 0.03 * math.sin(f * 0.4)
        s = pygame.transform.rotozoom(texto_surf, 0, scale)
        r = s.get_rect(center=(center_x, y))
        tela.blit(s, r)
        pygame.display.flip()
        clock.tick(FPS)

def mostrar_gameover_menu(tela, clock):
    """
    Animação: painel semi-transparente aparece do topo ("desce rápido") e fica centralizado.
    Retorna "retry" ou "menu".
    """
    btn_retry = Botao(LARGURA//2 - 110, -160, 220, 48, "Tentar novamente")
    btn_menu  = Botao(LARGURA//2 - 110, -90, 220, 48, "Voltar ao menu")
    fonte = pygame.font.SysFont(None, 56, bold=True)
    text = fonte.render("GAME OVER", True, (255,255,255))

    # animação de descida (rápida)
    total_frames = int(0.45 * FPS)  # bem rápido
    for f in range(total_frames):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
        t = (f + 1) / total_frames
        center_y = int(-200 + t * (ALTURA//2))
        # painel semi-transparente
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((30, 30, 30, 180))  # cinza escuro, alpha
        tela.blit(s, (0,0))
        rect_text = text.get_rect(center=(LARGURA//2, center_y - 80))
        tela.blit(text, rect_text)
        # posiciona botões relativos
        btn_retry.rect.y = center_y - 10
        btn_menu.rect.y = center_y + 60
        btn_retry.desenhar(tela)
        btn_menu.desenhar(tela)
        pygame.display.flip()
        clock.tick(FPS)

    # espera a escolha
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if btn_retry.clicado(ev):
                return "retry"
            if btn_menu.clicado(ev):
                return "menu"
        clock.tick(FPS)

def mostrar_victory_menu(tela, clock, nivel):
    """
    Fade-in + slide leve do painel de vitória. Retorna "next" ou "menu".
    """
    btn_next = Botao(LARGURA//2 - 140, ALTURA//2 + 10, 280, 48, "Ir para a próxima fase")
    btn_menu = Botao(LARGURA//2 - 140, ALTURA//2 + 80, 280, 48, "Voltar ao menu")
    fonte = pygame.font.SysFont(None, 48, bold=True)
    text = fonte.render(f"Fase {nivel} concluída!", True, (10,120,10))

    # fade-in do painel
    steps = int(0.6 * FPS)
    for i in range(steps):
        alpha = int(180 * (i / steps))
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((20,20,20, alpha))
        tela.blit(s, (0,0))
        # texto e botões
        y = int(ALTURA//3)
        rect = text.get_rect(center=(LARGURA//2, y))
        tela.blit(text, rect)
        # botões aparecendo com alpha (não necessário)
        btn_next.desenhar(tela)
        btn_menu.desenhar(tela)
        pygame.display.flip()
        clock.tick(FPS)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if btn_next.clicado(ev):
                return "next"
            if btn_menu.clicado(ev):
                return "menu"
        clock.tick(FPS)

# -----------------------
# level generation
# -----------------------
def gerar_level(mapa_largura, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas):
    chao = Plataforma(0, ALTURA - 40, mapa_largura, 40, "assets/images/ground.png")
    plataformas.add(chao); todos.add(chao)

    plataformas_lista = []
    last_x = 80

    if nivel < 3:
        faixas_y = [ALTURA - 150, ALTURA - 250, ALTURA - 350]
        for faixa in faixas_y:
            partes = 3
            for _ in range(partes):
                largura_plat = random.randint(130, 180)
                x = last_x + random.randint(140, 260)
                x = min(x, mapa_largura - largura_plat - 80)
                plat = Plataforma(x, faixa, largura_plat, 20, "assets/images/platform.png")
                plataformas.add(plat); todos.add(plat); plataformas_lista.append(plat)
                last_x = x
    else:
        # boss stage menor e mais apertado
        faixas_y = [ALTURA - 150, ALTURA - 260]
        for faixa in faixas_y:
            for _ in range(3):
                largura_plat = random.randint(140, 180)
                x = last_x + random.randint(160, 260)
                x = min(x, mapa_largura - largura_plat - 80)
                plat = Plataforma(x, faixa, largura_plat, 20, "assets/images/platform.png")
                plataformas.add(plat); todos.add(plat); plataformas_lista.append(plat)
                last_x = x

    # espinhos
    for _ in range(10):
        x = random.randint(150, mapa_largura - 150)
        esp = Espinho(x, ALTURA - 40)
        espinhos.add(esp); todos.add(esp)

    # itens (evita espinhos próximos)
    todas_plataformas_para_itens = [chao] + plataformas_lista
    for plat in todas_plataformas_para_itens:
        tent = 0
        while tent < 14:
            x = random.randint(plat.rect.x + 20, plat.rect.x + plat.rect.width - 20)
            y = plat.rect.y - 30
            seguro = True
            for esp in espinhos:
                if abs(x - esp.rect.centerx) < 90:
                    seguro = False; break
            if seguro:
                item = Item(x, y)
                itens.add(item); todos.add(item)
                break
            tent += 1

    # inimigos normais (se nivel < 3)
    if nivel < 3:
        for _ in range(5):
            while True:
                x = random.randint(300, mapa_largura - 300)
                if abs(x - 200) > 150: break
            inimigo = Inimigo(x, ALTURA - 80, x - 120, x + 120)
            inimigos.add(inimigo); todos.add(inimigo)

    # powerup
    powerup = PowerUp(mapa_largura // 3, ALTURA - 200)
    itens.add(powerup); todos.add(powerup)

    return chao, plataformas_lista

# -----------------------
# main loop for a level
# -----------------------
def jogar_level(nivel):
    """
    Roda um level. Retorna True se venceu (player quer ir next), False se quiser voltar ao menu (ou morreu).
    """
    global camera_shake, music_volume, current_music

    clock = pygame.time.Clock()

    # grupos
    todos = pygame.sprite.LayeredUpdates()
    plataformas = pygame.sprite.Group()
    itens = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    espinhos = pygame.sprite.Group()
    projeteis = pygame.sprite.Group()
    fim_fase = pygame.sprite.Group()
    particulas = pygame.sprite.Group()

    # jogador
    jogador = Jogador(particulas)
    todos.add(jogador)

    # mapa
    MAPA_LARGURA = 2000 if nivel == 3 else 3000
    chao, plataformas_lista = gerar_level(MAPA_LARGURA, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas)

    # boss se nivel 3
    boss = None
    if nivel == 3:
        # boss spawn numa área central reduzida
        boss = Boss(MAPA_LARGURA - 700, ALTURA - 160)
        # ajustar patrulha do boss para área curta
        boss.min_x = MAPA_LARGURA - 1100
        boss.max_x = MAPA_LARGURA - 400
        todos.add(boss)
        # tocar música do boss se disponível
        play_music("assets/sounds/boss_music.mp3", music_volume, force=True)

    # goal
    goal = Plataforma(MAPA_LARGURA - 80, ALTURA - 120, 80, 80, "assets/images/goal.png")
    fim_fase.add(goal); todos.add(goal)

    pontuacao = 0
    total_itens = len([i for i in itens if not isinstance(i, PowerUp)])
    game_over = False
    venceu = False

    # garantir música de fundo (apenas se não for boss; caso boss, já ajustamos)
    if not boss:
        if current_music != "assets/sounds/music.mp3":
            play_music("assets/sounds/music.mp3", music_volume, force=False)
        else:
            pygame.mixer.music.set_volume(music_volume)

    # loop do level
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return False  # volta ao menu
            # atirar (X)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_x:
                if jogador.pode_atacar:
                    proj = Projetil(jogador.rect.centerx, jogador.rect.centery, 1 if jogador.facing_right else -1)
                    projeteis.add(proj); todos.add(proj)

        # atualizações somente se não congelado por menu
        if not game_over:
            jogador.update(plataformas, chao)
            inimigos.update()
            projeteis.update()
            particulas.update()
            if boss:
                # boss.update pode aceitar projeteis,todos; ele patrulha e flutua internamente
                boss.update(projeteis, todos)

            # camera shake pedido pelo jogador
            if jogador.request_shake > 0:
                camera_shake = max(camera_shake, jogador.request_shake)
                jogador.request_shake = 0

            # coleta de itens
            coletados = pygame.sprite.spritecollide(jogador, itens, True)
            for c in coletados:
                if isinstance(c, PowerUp):
                    jogador.pode_atacar = True
                    jogador.duplo_pulo = True
                else:
                    pontuacao += 1

            # colisões com inimigos e espinhos (mask-based)
            hit_enemy = pygame.sprite.spritecollide(jogador, inimigos, False, pygame.sprite.collide_mask)
            hit_spike = pygame.sprite.spritecollide(jogador, espinhos, False, pygame.sprite.collide_mask)
            if not jogador.invulneravel and (hit_enemy or hit_spike):
                jogador.levar_dano()
                camera_shake = max(camera_shake, 10)
                if jogador.vidas <= 0:
                    game_over = True
                    venceu = False

            # projetil x inimigos
            for proj in list(projeteis):
                atingidos = pygame.sprite.spritecollide(proj, inimigos, False, pygame.sprite.collide_mask)
                if atingidos:
                    for inim in atingidos:
                        inim.morrer()
                    proj.kill()
                    continue
                # projetil do boss pode acertar jogador
                if getattr(proj, "from_boss", False):
                    if pygame.sprite.collide_mask(proj, jogador):
                        proj.kill()
                        jogador.levar_dano()
                        camera_shake = max(camera_shake, 10)
                        if jogador.vidas <= 0:
                            game_over = True
                            venceu = False

            # projetil do jogador atinge boss
            if boss:
                atingiu_boss = pygame.sprite.spritecollide(boss, projeteis, False, pygame.sprite.collide_mask)
                for p in list(atingiu_boss):
                    if not getattr(p, "from_boss", False):
                        # aplicar dano no boss e spawn de partículas azuis
                        boss.levar_dano(1)
                        # partículas azuis
                        for _ in range(10):
                            v = pygame.math.Vector2(random.uniform(-3,3), random.uniform(-3,-0.6))
                            # cria particle sprite no grupo particulas
                            surf = pygame.Surface((4,4), pygame.SRCALPHA)
                            pygame.draw.circle(surf, (120,180,255), (2,2), 2)
                            pfx = pygame.sprite.Sprite(); pfx.image = surf
                            pfx.rect = surf.get_rect(center=(boss.rect.centerx + random.randint(-16,16), boss.rect.centery + random.randint(-16,16)))
                            pfx.vel = v; pfx.life = 24
                            def upd(this=pfx):
                                this.rect.x += int(this.vel.x); this.rect.y += int(this.vel.y)
                                this.vel.y += 0.4
                                this.life -= 1
                                if this.life <= 0: this.kill()
                            pfx.update = upd
                            particulas.add(pfx)
                        p.kill()

                        # quando boss reach zero, restore bg music
                        if boss.vida <= 0:
                            play_music("assets/sounds/music.mp3", music_volume, force=True)

            # condição de vitória do level
            if pontuacao >= total_itens and pygame.sprite.spritecollide(jogador, fim_fase, False):
                game_over = True
                venceu = True

        # camera position + shake
        camera_x = jogador.rect.centerx - LARGURA // 2
        camera_x = max(0, min(camera_x, MAPA_LARGURA - LARGURA))

        offset_x = offset_y = 0
        if camera_shake > 0:
            offset_x = random.randint(-6,6); offset_y = random.randint(-6,6)
            camera_shake -= 1

        # draw
        tela = pygame.display.get_surface()
        tela.fill(BRANCO)
        # background scaled to map width
        try:
            bg = pygame.image.load("assets/images/background.png").convert()
            bg = pygame.transform.scale(bg, (MAPA_LARGURA, ALTURA))
            tela.blit(bg, (-camera_x + offset_x, 0 + offset_y))
        except Exception:
            # fallback plain
            pygame.draw.rect(tela, (180,220,255), (0,0,LARGURA,ALTURA))

        # draw all sprites
        for spr in todos:
            tela.blit(spr.image, (spr.rect.x - camera_x + offset_x, spr.rect.y + offset_y))
        # draw particulas over
        for p in particulas:
            tela.blit(p.image, (p.rect.x - camera_x + offset_x, p.rect.y + offset_y))

        # boss bar
        if boss:
            boss.desenhar_barra(tela)

        # HUD
        fonte = pygame.font.SysFont(None, 28)
        tela.blit(fonte.render(f"Itens: {pontuacao}/{total_itens}", True, PRETO), (10,10))
        tela.blit(fonte.render(f"Vidas: {jogador.vidas}", True, VERMELHO), (10,40))

        pygame.display.update()
        clock.tick(FPS)

        # se menu de game over / victory deve aparecer, congela o mundo e exibe o menu animado
        if game_over:
            # se venceu: mostrar victory menu (fade-in)
            if venceu:
                escolha = mostrar_victory_menu(tela, clock, nivel)
                return True if escolha == "next" else False
            else:
                escolha = mostrar_gameover_menu(tela, clock)
                if escolha == "retry":
                    return False  # main trata re-executar o mesmo level
                else:
                    return False  # volta ao menu

# -----------------------
# MAIN: fluxo dos Níveis
# -----------------------
def main():
    global music_volume 

    init_audio()
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Ana's World")
    clock = pygame.time.Clock()

    # tocar menu/music inicialmente
    play_music("assets/sounds/music.mp3", music_volume, force=False)

    # Menu inicial (retorna escolha e volume)
    escolha, vol = mostrar_menu(tela, clock, music_volume, "start")
    music_volume = vol
    pygame.mixer.music.set_volume(music_volume)


    if escolha == "quit":
        pygame.quit(); return

    nivel = 1
    while nivel <= 3:
        mostrar_transicao(tela, clock, nivel)
        venceu = jogar_level(nivel)
        if not venceu:
            # morreu ou escolheu voltar para menu
            escolha, vol = mostrar_menu(tela, clock, music_volume, "start")
            music_volume = vol
            pygame.mixer.music.set_volume(music_volume)
            if escolha == "quit":
                pygame.quit(); return
            # reiniciar do level 1 se user escolheu start
            nivel = 1
            continue
        else:
            nivel += 1

    # jogo zerado
    tela.fill(BRANCO)
    fonte = pygame.font.SysFont(None, 48)
    tela.blit(fonte.render("Parabéns! Você zerou o jogo!", True, (10,120,10)), (80, ALTURA // 2 - 20))
    pygame.display.update()
    pygame.time.wait(2500)
    pygame.quit()

if __name__ == "__main__":
    main()
