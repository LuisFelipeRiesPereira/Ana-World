# enemy.py
import pygame, glob, os, random

ANIM_SCALE = (36, 36)
DEATH_DURATION = 40  # frames que dura a animação de morte
ANIM_SPEED = 6

def load_frames(folder, prefix, scale=None):
    pattern = os.path.join(folder, f"{prefix}*.png")
    frames = []
    for path in sorted(glob.glob(pattern)):
        try:
            im = pygame.image.load(path).convert_alpha()
            if scale:
                im = pygame.transform.scale(im, scale)
            frames.append(im)
        except Exception:
            pass
    return frames

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__()
        folder = "assets/images/enemy"
        self.idle_frames = load_frames(folder, "idle_", ANIM_SCALE)
        self.death_frames = load_frames(folder, "death_", ANIM_SCALE)

        # fallbacks
        if not self.idle_frames:
            base = pygame.Surface(ANIM_SCALE, pygame.SRCALPHA)
            base.fill((200,50,50))
            self.idle_frames = [base]
        if not self.death_frames:
            self.death_frames = []

        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = ANIM_SPEED

        self.image = self.idle_frames[0].copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.limite_esq = limite_esq
        self.limite_dir = limite_dir
        self.vel_x = 2 if random.random() < 0.5 else -2

        # morte/estado
        self.morto = False
        self.death_timer = 0
        self.death_duration = DEATH_DURATION

    def update(self):
        # se está morrendo => animação de morte com shrink + flicker
        if self.morto:
            self.death_timer += 1
            t = self.death_timer / max(1, self.death_duration)
            if t >= 1.0:
                self.kill()
                return
            # escolher frame de morte se houver
            if self.death_frames:
                idx = min(len(self.death_frames)-1, (self.death_timer // self.anim_speed))
                base = self.death_frames[idx]
            else:
                base = self.idle_frames[0]
            # escala decrescente
            scale = max(0.01, 1.0 - t)
            img = pygame.transform.rotozoom(base, 0, scale)
            # flicker alpha: alterna transparente/visível
            if (self.death_timer // 4) % 2 == 0:
                img.set_alpha(100)
            else:
                img.set_alpha(255)
            # manter o centro praticamente no mesmo local
            center = self.rect.center
            self.image = img
            self.rect = self.image.get_rect(center=center)
            return

        # comportamento normal: andar entre limites + animação idle
        self.rect.x += self.vel_x
        if self.rect.left < self.limite_esq or self.rect.right > self.limite_dir:
            self.vel_x *= -1
            self.rect.x += self.vel_x * 2

        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.idle_frames)
        self.image = self.idle_frames[self.anim_index]
        self.mask = pygame.mask.from_surface(self.image)

    def morrer(self):
        if not self.morto:
            self.morto = True
            self.death_timer = 0
            # opcional: empurrão/efeito inicial ao morrer
            # (não remove imediatamente; animação cuidará do final)
