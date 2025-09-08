# player.py
import pygame, glob, os, random
from settings import ALTURA

JUMP_FORCE = 15
GRAVITY = 1
MAX_FALL = 12
WALK_SPEED = 4

def load_frames(pattern, scale=(40,50)):
    frames = []
    for path in sorted(glob.glob(pattern)):
        im = pygame.image.load(path).convert_alpha()
        if scale:
            im = pygame.transform.scale(im, scale)
        frames.append(im)
    return frames

class Jogador(pygame.sprite.Sprite):
    def __init__(self, particulas_group):
        super().__init__()
        scale = (40,50)
        self.idle_frames = load_frames("assets/images/player/idle_*.png", scale)
        self.run_frames  = load_frames("assets/images/player/run_*.png", scale)

        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 10
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(center=(100, ALTURA - 150))
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
        moving = False
        if keys[pygame.K_LEFT]:
            self.rect.x -= WALK_SPEED
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += WALK_SPEED
            self.facing_right = True
            moving = True

        new_max = 2 if self.duplo_pulo else 1
        if new_max != self.max_pulos:
            if new_max > self.max_pulos and not self.no_chao and self.pulos_restantes == 0:
                self.pulos_restantes = 1
            self.max_pulos = new_max

        pressed = keys[pygame.K_SPACE] and not self._prev_space
        if pressed:
            if self.no_chao:
                self.vel_y = -JUMP_FORCE
                self.no_chao = False
                self.pulos_restantes = self.max_pulos - 1
            elif self.pulos_restantes > 0:
                self.vel_y = -JUMP_FORCE
                self.pulos_restantes -= 1
                self._start_bounce()
                for _ in range(10):
                    angle = random.uniform(-30, 30)
                    v = pygame.math.Vector2(0, 4).rotate(angle)
                    self._spawn_particle(self.rect.centerx, self.rect.centery+8, (180,220,255), v)

        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        prev_bottom = self.rect.bottom
        impact_speed = self.vel_y
        self.rect.y += self.vel_y

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

        if self.invulneravel:
            self.invul_timer -= 1
            if self.invul_timer <=0:
                self.invulneravel=False

        self._update_animation(moving)
        self.mask = pygame.mask.from_surface(self.image)
        self._prev_space = keys[pygame.K_SPACE]

    def _update_animation(self, moving):
        frames = self.idle_frames if not moving else self.run_frames
        
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)
 
        if self.anim_index >= len(frames) :
            return
        frame = frames[self.anim_index]
        print (frame)

        if self.bounce_timer > 0:
            t = self.bounce_timer / self.BOUNCE_DUR
            sx = 1.0 - 0.08 * t
            sy = 1.0 + 0.22 * t
            w,h = frame.get_size()
            frame = pygame.transform.scale(frame, (max(1,int(w*sx)), max(1,int(h*sy))))
            self.bounce_timer -= 1

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        if self.invulneravel and ((self.invul_timer//6)%2==0):
            frame.set_alpha(140)
        else:
            frame.set_alpha(255)

        self.image = frame

    def _start_bounce(self):
        self.bounce_timer = self.BOUNCE_DUR

    def _spawn_particle(self, x, y, cor, vel_vec):
        surf = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(surf, cor, (2,2), 2)
        p = pygame.sprite.Sprite()
        p.image = surf
        p.rect = surf.get_rect(center=(x,y))
        p.vel = pygame.math.Vector2(vel_vec)
        p.life = 28
        def upd(this=p):
            this.rect.x += int(this.vel.x)
            this.rect.y += int(this.vel.y)
            this.vel.y += 0.4
            this.life -=1
            if this.life<=0: this.kill()
        p.update = upd
        self.particulas.add(p)

    def levar_dano(self):
        if not self.invulneravel:
            self.vidas -= 1
            self.invulneravel = True
            self.invul_timer = 60
            knock = -12 if self.facing_right else 12
            self.rect.x += knock
            self.vel_y = -10
            self.request_shake = 12
