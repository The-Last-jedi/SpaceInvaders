import pygame
WIN = pygame.display.set_mode((750, 750))

class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.images = []
        for i in range(1,16):
            img = pygame.image.load('sprites',f'exp{i}.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.img = self.images[self.index]
        self.mask = pygame.mask.from_surface(self.img)
        self.counter =0

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))   

    def explode(self):
        explode_speed = 3
        self.counter += 1
        if self.counter >= explode_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index +=1
            self.img = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= explode_speed:
            self.images.remove(self.img)

while True:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        explode()