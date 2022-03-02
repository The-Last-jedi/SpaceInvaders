import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 300

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Explosion Demo')

#define colours
bg = (50, 50, 50)

def draw_bg():
	screen.fill(bg)


#create Explosion class
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 16):
			img = pygame.image.load(f"img/tile0{num}.png")
			img = pygame.transform.scale(img, (30, 30))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [20, 20]
		
		self.counter = 0

	def update(self):
		explosion_speed = 3
		#update explosion animation
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, reset animation index
		#if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			#self.kill()


explosion_group = pygame.sprite.Group()


run = True
while run:

	clock.tick(fps)

	#draw background
	draw_bg()

	explosion_group.draw(screen)
	explosion_group.update()


	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			explosion = Explosion(pos[0], pos[1])
			explosion_group.add(explosion)


	pygame.display.update()

pygame.quit()	
