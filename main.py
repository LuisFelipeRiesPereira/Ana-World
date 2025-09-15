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
    import os
    fonte_titulo = pygame.font.SysFont(None, 56, bold=True)
    fonte = pygame.font.SysFont(None, 26)
    btn = Botao(LARGURA//2 - 100, ALTURA - 80, 200, 48, "Continuar")

    # candidates - tente vários nomes comuns para cada asset
    candidates = {
        "item": [
            "assets/images/coin.png"
        ],
        "powerup": [
            "assets/images/powerup.png",
        ],
        "enemy": [
            "assets/images/enemy/idle_01.png",
        ],
        "spike": [
            "assets/images/spike.png"
        ]
    }

    def try_load(list_paths):
        for p in list_paths:
            try:
                if os.path.exists(p):
                    img = pygame.image.load(p)
                    # convert_alpha pode falhar se display não estiver inicializado; tente com fallback
                    try:
                        img = img.convert_alpha()
                    except Exception:
                        img = img.convert()
                    print(f"[Tutorial] carregou: {p}")
                    return img
            except Exception as e:
                print(f"[Tutorial] erro ao carregar {p}: {e}")
        print(f"[Tutorial] não encontrou nenhum de: {list_paths}")
        return None

    img_item = try_load(candidates["item"])
    img_powerup = try_load(candidates["powerup"])
    img_enemy = try_load(candidates["enemy"])
    img_spike = try_load(candidates["spike"])

    # placeholders simples (32x32) caso a imagem não exista
    def placeholder(color, label=None):
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=6)
        if label:
            try:
                f = pygame.font.SysFont(None, 18)
                text = f.render(label, True, (255,255,255))
                tr = text.get_rect(center=(16,16))
                s.blit(text, tr)
            except Exception:
                pass
        return s

    if img_item is None:
        img_item = placeholder((200,160,40), "I")
    if img_powerup is None:
        img_powerup = placeholder((120,200,255), "P")
    if img_enemy is None:
        img_enemy = placeholder((200,60,60), "E")
    if img_spike is None:
        img_spike = placeholder((100,100,100), "!")

    # linhas com sprites
    linhas = [
        (img_item,   "Itens: Aumentam sua pontuação."),
        (img_powerup,"PowerUp: Permite pular duplo e atirar projéteis."),
        (img_enemy,  "Inimigos: Evite ou derrote com projéteis."),
        (img_spike,  "Espinhos: Causam dano imediato."),
        (None,       ""),
        (None, "Controles:"),
        (None, "<- / -> : Mover"),
        (None, "SPACE : Pular / pulo duplo"),
        (None, "X : Atirar (se habilitado)"),
        (None, "Seta para baixo : Atravessar plataformas")
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
        for img, texto in linhas:
            if img:
                try:
                    img_s = pygame.transform.smoothscale(img, (32,32))
                except Exception:
                    img_s = pygame.transform.scale(img, (32,32))
                tela.blit(img_s, (80, y))
                txt = fonte.render(texto, True, PRETO)
                tela.blit(txt, (120, y+6))
            else:
                txt = fonte.render(texto, True, PRETO)
                tela.blit(txt, (80, y))
            y += 40

        btn.desenhar(tela)
        pygame.display.flip()
        clock.tick(FPS)


# -----------------------
# Transição LEVEL
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
# Gerador de level
# -----------------------
def gerar_level(mapa_largura, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas):
    # Chão tileado
    chao = Plataforma(0, ALTURA - 60, mapa_largura, 70, "assets/images/groundtest.png")
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
        espinho_posicoes = []
        for _ in range(10):
            tentativas = 0
            while tentativas < 20:  # até 20 tentativas para encontrar posição válida
                x = random.randint(150, mapa_largura - 150)
                if all(abs(x - ex) > 80 for ex in espinho_posicoes):  # mínimo 80px de distância
                    esp = Espinho(x, ALTURA - 60)
                    espinhos.add(esp); todos.add(esp)
                    espinho_posicoes.append(x)
                    break
                tentativas += 1


        # itens: tentar spawnar por plataforma
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
            inimigo = Inimigo(x, ALTURA - 100, max(0, x - 120), min(mapa_largura, x + 120))
            inimigos.add(inimigo); todos.add(inimigo)

        # powerup adicionar
        powerup = PowerUp(mapa_largura // 2, ALTURA - 200)
        itens.add(powerup); todos.add(powerup)

    else:
        # Arena do boss: 2 plataformas fixas
        plat1 = Plataforma(200, ALTURA - 200, 120, 20, "assets/images/platform.png")
        plat2 = Plataforma(480, ALTURA - 320, 120, 20, "assets/images/platform.png")
        plataformas.add(plat1, plat2); todos.add(plat1, plat2)
        plataformas_lista.extend([plat1, plat2])

        # spawn apenas UM powerup no boss
        # posiciona no centro da arena
        center_x = mapa_largura // 2
        powerup = PowerUp(center_x, ALTURA - 200)
        itens.add(powerup); todos.add(powerup)

    return chao, plataformas_lista

# -----------------------
# Loop de um level
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

    goal = Plataforma(MAPA_LARGURA - 60, ALTURA - 150, 45, 90, "assets/images/goal.png")
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
            fonte = pygame.font.SysFont(None, 42, bold=True)
            msg = fonte.render("Parabéns! Você derrotou o Chefão!", True, (10,120,10))
            msg2 = fonte.render("Você zerou o jogo!", True, (10,120,10))
            btn_menu = Botao(LARGURA//2 - 100, ALTURA//2 + 80, 200, 48, "Voltar ao Menu")

            alpha_surface = pygame.Surface((LARGURA, ALTURA))
            alpha_surface.fill(BRANCO)

            fade = 0
            clock = pygame.time.Clock()
            esperando = True
            while esperando:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit
                    if btn_menu.clicado(ev):
                        # volta ao menu inicial
                        escolha, vol = mostrar_menu(tela, clock, music_volume, "start")
                        music_volume = vol
                        if escolha == "quit":
                            pygame.quit(); return
                        nivel = 1  # reinicia jogo desde o início
                        esperando = False

                tela.fill(BRANCO)
                offset_x = int(6 * math.sin(pygame.time.get_ticks() * 0.004))
                tela.blit(msg, (LARGURA//2 - msg.get_width()//2 + offset_x, ALTURA//2 - 60))
                tela.blit(msg2, (LARGURA//2 - msg2.get_width()//2, ALTURA//2 - 20))
                btn_menu.desenhar(tela)

                if fade < 255:
                    alpha_surface.set_alpha(255 - fade)
                    tela.blit(alpha_surface, (0,0))
                    fade += 5

                pygame.display.update()
                clock.tick(FPS)
            continue  # volta ao loop principal de levels

    pygame.quit()

if __name__ == "__main__":
    main()
