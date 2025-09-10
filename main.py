# main.py
import pygame
import random
import math
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
# Variáveis globais
# -----------------------
current_music = None
music_volume = 0.5
camera_shake = 0

# -----------------------
# Áudio
# -----------------------
def init_audio():
    try:
        pygame.mixer.init()
    except Exception as e:
        print("Aviso: mixer init falhou:", e)

def play_music(path, volume=0.5, force=False):
    global current_music, music_volume
    music_volume = volume
    if not pygame.mixer.get_init():
        return
    try:
        if current_music == path and not force:
            pygame.mixer.music.set_volume(music_volume)
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
        current_music = path
    except Exception as e:
        print("Erro ao tocar música:", e)

# -----------------------
# Tutorial (mini tela)
# -----------------------
def mostrar_tutorial(tela, clock):
    fonte_titulo = pygame.font.SysFont(None, 56, bold=True)
    fonte = pygame.font.SysFont(None, 28)
    btn = Botao(LARGURA//2 - 100, ALTURA - 100, 200, 48, "Continuar")

    linhas = [
        "🎯 Objetivo: coletar todos os itens e chegar ao portal!",
        "⭐ Itens: aumentam sua pontuação.",
        "💎 PowerUp: permite pular duplo e atirar projéteis.",
        "👾 Inimigos: evite-os ou derrote com projéteis.",
        "☠️ Espinhos: causam dano imediato.",
        "",
        "🎮 Controles:",
        "→ / ← : mover",
        "SPACE : pular / pulo duplo",
        "X : atirar (se habilitado)",
        "↓ : atravessar plataformas finas",
        "ESC : abrir menu"
    ]

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                return
            if btn.clicado(ev):
                return

        tela.fill((240, 240, 240))
        titulo = fonte_titulo.render("Tutorial", True, PRETO)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 40))

        y = 120
        for linha in linhas:
            txt = fonte.render(linha, True, PRETO)
            tela.blit(txt, (80, y))
            y += 34

        btn.desenhar(tela)

        pygame.display.flip()
        clock.tick(FPS)

# -----------------------
# Transição LEVEL (entra do topo, pausa, sai pra baixo)
# -----------------------
def mostrar_transicao(tela, clock, nivel):
    fonte = pygame.font.SysFont(None, 84, bold=True)
    texto = fonte.render(f"LEVEL {nivel}", True, PRETO)
    h = texto.get_height()
    enter_frames = int(0.5 * FPS)
    hold_frames = int(0.6 * FPS)
    exit_frames = int(0.5 * FPS)
    total = enter_frames + hold_frames + exit_frames

    for f in range(total):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

        if f < enter_frames:
            t = f / max(1, enter_frames)
            y = int(-h + t * (ALTURA//3 + h))
        elif f < enter_frames + hold_frames:
            y = ALTURA // 3
        else:
            t = (f - enter_frames - hold_frames) / max(1, exit_frames)
            y = int(ALTURA//3 + t * (ALTURA//2 + h))

        offset_x = int(24 * math.sin(f * 0.12))
        scale = 1.0 + 0.03 * math.sin(f * 0.25)
        s = pygame.transform.rotozoom(texto, 0, scale)
        r = s.get_rect(center=(LARGURA//2 + offset_x, y))

        tela.fill(BRANCO)
        tela.blit(s, r)
        pygame.display.flip()
        clock.tick(FPS)

# -----------------------
# Gerador de level (items & inimigos adicionados)
# -----------------------
def gerar_level(mapa_largura, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas):
    # Chão tileado
    chao = Plataforma(0, ALTURA - 40, mapa_largura, 40, "assets/images/ground.png")
    plataformas.add(chao); todos.add(chao)

    plataformas_lista = []
    if nivel < 3:
        last_x = 80
        for faixa in [ALTURA - 150, ALTURA - 250, ALTURA - 350]:
            for _ in range(3):
                largura_plat = random.randint(130, 180)
                x = last_x + random.randint(140, 260)
                x = min(x, mapa_largura - largura_plat - 80)
                plat = Plataforma(x, faixa, largura_plat, 20, "assets/images/platform.png")
                plataformas.add(plat); todos.add(plat); plataformas_lista.append(plat)
                last_x = x
        # espinhos
        for _ in range(10):
            x = random.randint(150, mapa_largura - 150)
            esp = Espinho(x, ALTURA - 40)
            espinhos.add(esp); todos.add(esp)

        # itens: tentar spawnar por plataforma (inclusive chão)
        todas_plat_para_itens = [chao] + plataformas_lista
        for plat in todas_plat_para_itens:
            tentativas = 0
            while tentativas < 12:
                if plat.rect.width < 40:
                    break
                x = random.randint(plat.rect.x + 20, plat.rect.x + plat.rect.width - 20)
                y = plat.rect.y - 28
                seguro = True
                for esp in espinhos:
                    if abs(x - esp.rect.centerx) < 90:
                        seguro = False; break
                if seguro:
                    if random.random() < 0.12:
                        it = PowerUp(x, y)
                    else:
                        it = Item(x, y)
                    itens.add(it); todos.add(it)
                    break
                tentativas += 1

        # inimigos
        for _ in range(5):
            while True:
                x = random.randint(300, mapa_largura - 300)
                if abs(x - 100) > 150:
                    break
            inimigo = Inimigo(x, ALTURA - 80, max(0, x - 120), min(mapa_largura, x + 120))
            inimigos.add(inimigo); todos.add(inimigo)

        # powerup adicional por fase normal (garante um powerup por fase, mas não adiciona ao boss aqui)
        powerup = PowerUp(min(mapa_largura - 100, mapa_largura // 2), ALTURA - 200)
        itens.add(powerup); todos.add(powerup)

    else:
        # Arena do boss: 2 plataformas fixas (sem spawn massivo)
        plat1 = Plataforma(200, ALTURA - 200, 120, 20, "assets/images/platform.png")
        plat2 = Plataforma(480, ALTURA - 320, 120, 20, "assets/images/platform.png")
        plataformas.add(plat1, plat2); todos.add(plat1, plat2)
        plataformas_lista.extend([plat1, plat2])

        # spawn apenas UM powerup no boss (como você pediu)
        # posiciona no centro da arena
        center_x = mapa_largura // 2
        powerup = PowerUp(center_x, ALTURA - 200)
        itens.add(powerup); todos.add(powerup)

    return chao, plataformas_lista

# -----------------------
# Loop de um level (coleta de itens tratada)
# -----------------------
def jogar_level(nivel):
    global camera_shake, music_volume, current_music
    clock = pygame.time.Clock()

    todos = pygame.sprite.LayeredUpdates()
    plataformas = pygame.sprite.Group()
    itens = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    espinhos = pygame.sprite.Group()
    projeteis = pygame.sprite.Group()
    fim_fase = pygame.sprite.Group()
    particulas = pygame.sprite.Group()

    jogador = Jogador(particulas)
    todos.add(jogador)

    # largura do mapa: boss = tela, senão largos níveis
    if nivel == 3:
        MAPA_LARGURA = LARGURA
    else:
        MAPA_LARGURA = 3000

    chao, plataformas_lista = gerar_level(
        MAPA_LARGURA, nivel, todos, plataformas,
        itens, inimigos, espinhos, projeteis, particulas
    )

    boss = None
    if nivel == 3:
        boss = Boss(100, ALTURA - 160)
        # teleport targets dentro da arena
        boss.teleport_targets = [(80, ALTURA - 160), (LARGURA - 120, ALTURA - 160)]
        todos.add(boss)
        play_music("assets/sounds/boss_music.mp3", music_volume, force=True)
    else:
        play_music("assets/sounds/music.mp3", music_volume, force=False)

    goal = Plataforma(MAPA_LARGURA - 80, ALTURA - 120, 80, 80, "assets/images/goal.png")
    fim_fase.add(goal); todos.add(goal)

    # pre-cálculo: quantos itens (não powerups) precisamos coletar
    total_itens = len([i for i in itens if not isinstance(i, PowerUp)])
    pontuacao = 0

    # carregar background escalado do mapa
    try:
        bg = pygame.image.load("assets/images/background.png").convert()
        bg_surf = pygame.transform.scale(bg, (MAPA_LARGURA, ALTURA))
    except Exception:
        bg_surf = None

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_x:
                if jogador.pode_atacar:
                    proj = Projetil(jogador.rect.centerx, jogador.rect.centery, 1 if jogador.facing_right else -1)
                    projeteis.add(proj); todos.add(proj)

        # Atualizações
        jogador.update(plataformas, chao)
        inimigos.update()
        projeteis.update()
        particulas.update()
        if boss:
            boss.update(projeteis, todos)

        # coleta de itens
        coletados = pygame.sprite.spritecollide(jogador, itens, True, pygame.sprite.collide_mask)
        for c in coletados:
            if isinstance(c, PowerUp):
                jogador.pode_atacar = True
                jogador.duplo_pulo = True
            else:
                pontuacao += 1

        # colisões / danos
        if not jogador.invulneravel:
            if pygame.sprite.spritecollide(jogador, inimigos, False, pygame.sprite.collide_mask) or \
               pygame.sprite.spritecollide(jogador, espinhos, False, pygame.sprite.collide_mask):
                jogador.levar_dano()
                if jogador.vidas <= 0:
                    return "morreu"

        # projéteis do boss atingem jogador
        for proj in list(projeteis):
            if getattr(proj, "from_boss", False):
                if pygame.sprite.collide_mask(proj, jogador):
                    proj.kill()
                    jogador.levar_dano()
                    if jogador.vidas <= 0:
                        return "morreu"

        # projetil do jogador atinge inimigos
        for proj in list(projeteis):
            if not getattr(proj, "from_boss", False):
                atingidos = pygame.sprite.spritecollide(proj, inimigos, False, pygame.sprite.collide_mask)
                if atingidos:
                    for inim in atingidos:
                        inim.morrer()
                    proj.kill()

        # projetil do jogador atinge boss
        if boss:
            atingiu_boss = pygame.sprite.spritecollide(boss, projeteis, False, pygame.sprite.collide_mask)
            for p in list(atingiu_boss):
                if not getattr(p, "from_boss", False):
                    boss.levar_dano(1)
                    # spawn partículas azuis
                    for _ in range(10):
                        surf = pygame.Surface((4,4), pygame.SRCALPHA)
                        pygame.draw.circle(surf, (120,180,255), (2,2), 2)
                        pfx = pygame.sprite.Sprite(); pfx.image = surf
                        pfx.rect = surf.get_rect(center=(boss.rect.centerx + random.randint(-16,16), boss.rect.centery + random.randint(-16,16)))
                        pfx.vel = pygame.math.Vector2(random.uniform(-3,3), random.uniform(-3,-0.6))
                        pfx.life = 24
                        def upd(this=pfx):
                            this.rect.x += int(this.vel.x); this.rect.y += int(this.vel.y)
                            this.vel.y += 0.4
                            this.life -= 1
                            if this.life <= 0: this.kill()
                        pfx.update = upd
                        particulas.add(pfx)
                    p.kill()
                    if boss.vida <= 0:
                        return "boss_defeated"

        # vitória por coleta + portal
        if pontuacao >= total_itens and pygame.sprite.spritecollide(jogador, fim_fase, False):
            return "venceu"

        # CÂMERA segue jogador se mapa maior que tela
        if MAPA_LARGURA > LARGURA:
            camera_x = jogador.rect.centerx - LARGURA // 2
            if camera_x < 0: camera_x = 0
            if camera_x > MAPA_LARGURA - LARGURA: camera_x = MAPA_LARGURA - LARGURA
        else:
            camera_x = 0

        offset_x = offset_y = 0
        if camera_shake > 0:
            offset_x = random.randint(-6,6); offset_y = random.randint(-6,6)
            camera_shake -= 1

        # Desenho
        tela = pygame.display.get_surface()
        tela.fill(BRANCO)

        if bg_surf:
            tela.blit(bg_surf, (-camera_x + offset_x, 0 + offset_y))
        else:
            pygame.draw.rect(tela, (180,220,255), (0,0,LARGURA,ALTURA))

        for spr in todos:
            tela.blit(spr.image, (spr.rect.x - camera_x + offset_x, spr.rect.y + offset_y))

        for p in particulas:
            tela.blit(p.image, (p.rect.x - camera_x + offset_x, p.rect.y + offset_y))

        if boss:
            boss.desenhar_barra(tela)

        fonte = pygame.font.SysFont(None, 28)
        tela.blit(fonte.render(f"Itens: {pontuacao}/{total_itens}", True, PRETO), (10, 10))
        tela.blit(fonte.render(f"Vidas: {jogador.vidas}", True, VERMELHO), (10, 40))

        pygame.display.update()
        clock.tick(FPS)

# -----------------------
# MAIN
# -----------------------
def main():
    global music_volume
    init_audio()
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Ana's World")
    clock = pygame.time.Clock()

    play_music("assets/sounds/music.mp3", music_volume, force=False)

    escolha, vol = mostrar_menu(tela, clock, music_volume, "start")
    music_volume = vol
    try:
        pygame.mixer.music.set_volume(music_volume)
    except Exception:
        pass

    if escolha == "quit":
        pygame.quit(); return

    mostrar_tutorial(tela, clock)

    nivel = 1
    while nivel <= 3:
        mostrar_transicao(tela, clock, nivel)
        resultado = jogar_level(nivel)
        if resultado == "morreu":
            escolha, vol = mostrar_menu(tela, clock, music_volume, "start")
            music_volume = vol
            try:
                pygame.mixer.music.set_volume(music_volume)
            except Exception:
                pass
            if escolha == "quit":
                break
            nivel = 1
            continue
        elif resultado == "venceu":
            nivel += 1
            continue
        elif resultado == "boss_defeated":
            tela.fill(BRANCO)
            fonte = pygame.font.SysFont(None, 48)
            msg = fonte.render("Parabéns! Você derrotou o Chefão e zerou o jogo!", True, (10,120,10))
            tela.blit(msg, (40, ALTURA//2 - 24))
            pygame.display.update()
            pygame.time.wait(4000)
            break
        else:
            break

    pygame.quit()

if __name__ == "__main__":
    main()
