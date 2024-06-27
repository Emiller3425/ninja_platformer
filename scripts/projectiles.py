import pygame

class Projectile:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['projectiles/' + p_type].copy()
        self.animation_frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

class Shuriken(Projectile):
    def __init__(self, game, pos, velocity=[0, 0], frame=0):
        super().__init__(game, 'shuriken', pos, velocity=velocity, frame=frame)
        # shallow copy because we can reverse the list without affecting the original
        self.animation.images = self.animation.images[:]
        if self.velocity[0] < 0:
            self.animation.images.reverse()

