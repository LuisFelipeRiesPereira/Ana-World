# main.py
import pygame
import random
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

# Shake da câmera
camera_shake = 0


# =============================
# FUNÇÃO DE TRANSIÇÃO DE LEVEL
# =============================
def mostrar_transicao(tela, clock, nivel):
    fonte = pygame.font.SysFont(None, 72, bold=True)
    texto = fonte.render(f"LEVEL {nivel}", True, (0, 0, 0))
    rect = texto.get_rect(center=(LARGURA // 2, -50))  # começa acima da tela

    velocidade = 10
    tempo_total = 90  # frames (~1.5s a 60fps)
    frame = 0

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

        tela.fill((255, 255, 255))

        # entra -> pausa -> sai
        if frame < tempo_total // 3:
            rect.y += velocidade
        elif frame > 2 * tempo_total // 3:
            rect.y += velocidade

        tela.blit(texto, rect)

        pygame.display.flip()
        clock.tick(FPS)

        frame += 1
        if frame >= tempo_total:
            rodando = False


# =============================
# FUNÇÃO PARA GERAR LEVEL
# =============================
def gerar_level(mapa_largura, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas):
    chao = Plataforma(0, ALTURA - 40, mapa_largura, 40, "assets/images/ground.png")
    plataformas.add(chao)
    todos.add(chao)

    plataformas_lista = []
    last_x = 100

    if nivel < 3:
        faixas_y = [ALTURA - 150, ALTURA - 250, ALTURA - 350]
        for faixa in faixas_y:
            for _ in range(3):
                largura_plat = random.randint(120, 180)
                x = last_x + random.randint(140, 260)
                if x > mapa_largura - largura_plat - 100:
                    x = mapa_largura - largura_plat - 100
                plat = Plataforma(x, faixa, largura_plat, 20, "assets/images/platform.png")
                plataformas.add(plat)
                todos.add(plat)
                plataformas_lista.append(plat)
                last_x = x
    else:
        faixas_y = [ALTURA - 150, ALTURA - 280]
        for faixa in faixas_y:
            for _ in range(4):
                largura_plat = random.randint(140, 200)
                x = last_x + random.randint(160, 320)
                x = min(x, mapa_largura - largura_plat - 120)
                plat = Plataforma(x, faixa, largura_plat, 20, "assets/images/platform.png")
                plataformas.add(plat)
                todos.add(plat)
                plataformas_lista.append(plat)
                last_x = x

    # espinhos
    for _ in range(12):
        x = random.randint(150, mapa_largura - 150)
        esp = Espinho(x, ALTURA - 40)
        espinhos.add(esp)
        todos.add(esp)

    # itens
    todas_plataformas_para_itens = [chao] + plataformas_lista
    for plat in todas_plataformas_para_itens:
        tentativas = 0
        while tentativas < 12:
            x = random.randint(plat.rect.x + 20, plat.rect.x + plat.rect.width - 20)
            y = plat.rect.y - 30
            seguro = True
            for esp in espinhos:
                if abs(x - esp.rect.centerx) < 90:
                    seguro = False
                    break
            if seguro:
                item = Item(x, y)
                itens.add(item)
                todos.add(item)
                break
            tentativas += 1

    # inimigos normais
    if nivel < 3:
        for _ in range(5):
            while True:
                x = random.randint(300, mapa_largura - 300)
                if abs(x - 200) > 150:
                    break
            inimigo = Inimigo(x, ALTURA - 80, x - 120, x + 120)
            inimigos.add(inimigo)
            todos.add(inimigo)

    # powerup
    powerup = PowerUp(mapa_largura // 3, ALTURA - 200)
    itens.add(powerup)
    todos.add(powerup)

    return chao, plataformas_lista


# =============================
# LOOP DE UM LEVEL
# =============================
def jogar_level(nivel):
    global camera_shake

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

    MAPA_LARGURA = 3000
    chao, plataformas_lista = gerar_level(MAPA_LARGURA, nivel, todos, plataformas, itens, inimigos, espinhos, projeteis, particulas)

    boss = None
    if nivel == 3:
        boss = Boss(MAPA_LARGURA - 500, ALTURA - 80)
        todos.add(boss)

    goal = Plataforma(MAPA_LARGURA - 80, ALTURA - 120, 80, 80, "assets/images/goal.png")
    fim_fase.add(goal)
    todos.add(goal)

    pontuacao = 0
    total_itens = len([i for i in itens if not isinstance(i, PowerUp)])
    clock = pygame.time.Clock()
    rodando = True
    game_over = False
    venceu = False

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_x:
                if jogador.pode_atacar:
                    proj = Projetil(jogador.rect.centerx, jogador.rect.centery, 1 if jogador.facing_right else -1)
                    projeteis.add(proj)
                    todos.add(proj)

        if not game_over:
            jogador.update(plataformas, chao)
            inimigos.update()
            projeteis.update()
            particulas.update()
            if boss:
                boss.update(projeteis, todos)

            if jogador.request_shake > 0:
                camera_shake = max(camera_shake, jogador.request_shake)
                jogador.request_shake = 0

            coletados = pygame.sprite.spritecollide(jogador, itens, True)
            for c in coletados:
                if isinstance(c, PowerUp):
                    jogador.pode_atacar = True
                    jogador.duplo_pulo = True
                else:
                    pontuacao += 1

            hit_enemy = pygame.sprite.spritecollide(jogador, inimigos, False, pygame.sprite.collide_mask)
            hit_spike = pygame.sprite.spritecollide(jogador, espinhos, False, pygame.sprite.collide_mask)
            if not jogador.invulneravel and (hit_enemy or hit_spike):
                jogador.levar_dano()
                camera_shake = max(camera_shake, 10)

            for proj in list(projeteis):
                atingidos = pygame.sprite.spritecollide(proj, inimigos, False, pygame.sprite.collide_mask)
                if atingidos:
                    for inimigo in atingidos:
                        inimigo.morrer()
                    proj.kill()

                if hasattr(proj, "from_boss") and proj.from_boss:
                    if pygame.sprite.collide_mask(proj, jogador):
                        proj.kill()
                        jogador.levar_dano()
                        camera_shake = max(camera_shake, 10)

            if boss:
                atingiu_boss = pygame.sprite.spritecollide(boss, projeteis, False, pygame.sprite.collide_mask)
                for p in list(atingiu_boss):
                    if not getattr(p, "from_boss", False):
                        boss.levar_dano(1)
                        p.kill()

            if pontuacao >= total_itens and pygame.sprite.spritecollide(jogador, fim_fase, False):
                game_over = True
                venceu = True

            if jogador.vidas <= 0:
                game_over = True
                venceu = False

        camera_x = jogador.rect.centerx - LARGURA // 2
        camera_x = max(0, min(camera_x, MAPA_LARGURA - LARGURA))

        offset_x = offset_y = 0
        if camera_shake > 0:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            camera_shake -= 1

        tela = pygame.display.get_surface()
        tela.fill(BRANCO)
        bg = pygame.image.load("assets/images/background.png").convert()
        bg = pygame.transform.scale(bg, (MAPA_LARGURA, ALTURA))
        tela.blit(bg, (-camera_x + offset_x, 0 + offset_y))

        for sprite in todos:
            tela.blit(sprite.image, (sprite.rect.x - camera_x + offset_x, sprite.rect.y + offset_y))
        for p in particulas:
            tela.blit(p.image, (p.rect.x - camera_x + offset_x, p.rect.y + offset_y))

        if boss:
            boss.desenhar_barra(tela)

        fonte = pygame.font.SysFont(None, 28)
        tela.blit(fonte.render(f"Itens: {pontuacao}/{total_itens}", True, PRETO), (10, 10))
        tela.blit(fonte.render(f"Vidas: {jogador.vidas}", True, VERMELHO), (10, 40))

        pygame.display.update()
        clock.tick(FPS)

        if game_over:
            return venceu


# =============================
# MAIN
# =============================
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Ana's World")
    clock = pygame.time.Clock()

    escolha, volume = mostrar_menu(tela, clock, 0.5, "start")
    if escolha == "quit":
        pygame.quit()
        return

    for nivel in range(1, 4):
        mostrar_transicao(tela, clock, nivel)
        venceu = jogar_level(nivel)
        if not venceu:
            # perdeu -> volta ao menu inicial
            escolha, volume = mostrar_menu(tela, clock, volume, "start")
            if escolha == "quit":
                pygame.quit()
                return
            else:
                return main()

    tela.fill(BRANCO)
    fonte = pygame.font.SysFont(None, 48)
    tela.blit(fonte.render("Parabéns! Você zerou o jogo!", True, (10, 120, 10)), (80, ALTURA // 2 - 20))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    main()
