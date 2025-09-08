# player.py
import pygame
import random
from settings import ALTURA

# constantes locais
JUMP_FORCE = 20
GRAVITY = 1
MAX_FALL = 12

class Jogador(pygame.sprite.Sprite):
    def __init__(self, particulas_group):
        super().__init__()
        self.base_right = pygame.image.load("assets/images/player.png").convert_alpha()
        self.base_right = pygame.transform.scale(self.base_right, (40, 50))
        self.base_left = pygame.transform.flip(self.base_right, True, False)
        self.image = self.base_right.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (100, ALTURA - 150)
        self.mask = pygame.mask.from_surface(self.image)

        self.vel_y = 0
        self.no_chao = False

        self.duplo_pulo = False
        self.max_pulos = 1
        self.pulos_restantes = 1
        self._prev_space = False

        self.facing_right = True

        self.bounce_timer = 0
        self.BOUNCE_DUR = 8

        self.vidas = 3
        self.invulneravel = False
        self.invul_timer = 0
        self.pode_atacar = False

        self.request_shake = 0

        self.particulas = particulas_group

    def update(self, plataformas, chao=None):
        keys = pygame.key.get_pressed()

        # horiz
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.facing_right = True

        # ajustar max pulos
        new_max = 2 if self.duplo_pulo else 1
        if new_max != self.max_pulos:
            if new_max > self.max_pulos and not self.no_chao and self.pulos_restantes == 0:
                self.pulos_restantes = 1
            self.max_pulos = new_max

        # pulo com edge detect
        jump_pressed = keys[pygame.K_SPACE] and not self._prev_space
        if jump_pressed:
            if self.no_chao:
                self.vel_y = -JUMP_FORCE
                self.no_chao = False
                self.pulos_restantes = self.max_pulos - 1
            elif self.pulos_restantes > 0:
                self.vel_y = -JUMP_FORCE
                self.pulos_restantes -= 1
                self._start_bounce()
                # partículas do duplo pulo
                for _ in range(10):
                    angle = random.uniform(-30, 30)
                    v = pygame.math.Vector2(0, 4).rotate(angle)
                    self._spawn_particle(self.rect.centerx, self.rect.centery + 8, (180,220,255), v)

        # gravidade
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        prev_bottom = self.rect.bottom
        impact_speed = self.vel_y
        self.rect.y += self.vel_y

        # colisão vertical (one-way)
        self.no_chao = False
        landed = False
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vel_y >= 0 and prev_bottom <= p.rect.top:
                    if p == chao:
                        self.rect.bottom = p.rect.top
                        self.vel_y = 0
                        landed = True
                        break
                    else:
                        if not keys[pygame.K_DOWN]:
                            self.rect.bottom = p.rect.top
                            self.vel_y = 0
                            landed = True
                            break

        if landed:
            self.no_chao = True
            self.pulos_restantes = self.max_pulos
            self.bounce_timer = 0
            if impact_speed > 6:
                for _ in range(6):
                    v = pygame.math.Vector2(random.uniform(-2,2), random.uniform(-4,-1))
                    self._spawn_particle(self.rect.centerx, self.rect.bottom, (200,200,200), v)

        # invul
        if self.invulneravel:
            self.invul_timer -= 1
            if self.invul_timer <= 0:
                self.invulneravel = False

        # composição visual
        self._compose_image()
        self.mask = pygame.mask.from_surface(self.image)
        self._prev_space = keys[pygame.K_SPACE]

    def _start_bounce(self):
        self.bounce_timer = self.BOUNCE_DUR

    def _compose_image(self):
        base = self.base_right if self.facing_right else self.base_left
        if self.bounce_timer > 0:
            t = self.bounce_timer / self.BOUNCE_DUR
            sx = 1.0 - 0.08 * t
            sy = 1.0 + 0.22 * t
            w, h = base.get_size()
            scaled = pygame.transform.scale(base, (max(1, int(w * sx)), max(1, int(h * sy))))
            self.image = scaled
            self.bounce_timer -= 1
        else:
            self.image = base

        if self.invulneravel:
            if (self.invul_timer // 4) % 2 == 0:
                self.image.set_alpha(120)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def _spawn_particle(self, x, y, cor, vel_vec):
        surf = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(surf, cor, (2,2), 2)
        p = pygame.sprite.Sprite()
        p.image = surf
        p.rect = surf.get_rect(center=(x,y))
        # vel_vec is a Vector2
        p.vel = pygame.math.Vector2(vel_vec)
        p.life = 28
        def _update(this=p):
            this.rect.x += int(this.vel.x)
            this.rect.y += int(this.vel.y)
            this.vel.y += 0.4
            this.life -= 1
            if this.life <= 0:
                this.kill()
        p.update = _update
        self.particulas.add(p)

    def levar_dano(self):
        if not self.invulneravel:
            self.vidas -= 1
            self.invulneravel = True
            self.invul_timer = 60
            knock = -12 if self.facing_right else 12
            self.rect.x += knock
            self.vel_y = -10
            self.request_shake = 10
