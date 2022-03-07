import pygame
import os
import random
import time
from pygame.locals import *
pygame.init()
pygame.font.init()

#draw window
WIDTH,HEIGHT = 750,650
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Space Invaders')
pygame.mouse.set_visible(False)

#load images
ORANGE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join('sprites',"orange_space_ship.png")),(100,83))
XWING = pygame.transform.scale(pygame.image.load(os.path.join('sprites', 'X-wing_top.png')), (107, 122))
RED_ENEMY_SHIP = pygame.transform.scale(pygame.image.load(os.path.join('sprites', 'red_enemy.png')),(85, 95))
GREEN_ENEMY_SHIP = pygame.transform.scale(pygame.image.load(os.path.join('sprites', 'green_enemy.png')), (80, 81))
BLUE_ENEMY_SHIP = pygame.transform.scale(pygame.image.load(os.path.join('sprites', 'blue_enemy.png')), (99, 81))
#load drops
MEDPACK = pygame.transform.scale(pygame.image.load(os.path.join('sprites','medpack.png')), (60, 60))
#load lasers
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join('sprites','red_laser.png')), (13, 37))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join('sprites','green_laser.png')), (14, 37))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join('sprites','blue_laser.png')), (15, 37))
GREEN_LASER_ROUND = pygame.image.load(os.path.join('sprites','green_laser_round.png'))
#load bg
BG = pygame.transform.scale(pygame.image.load(os.path.join('sprites','background.jpg')),(WIDTH,HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def offscreen(self, height):
        return not(self.y<=height and self.y>=0)
    
    def collision(self, obj):
        return collide(obj, self)

class Medpack:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)        
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

#create explosion group
explosion_group = pygame.sprite.Group()
#create Explosion class
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 16):
			img = pygame.image.load(f"explode/img/exp{num}.png")
			img = pygame.transform.scale(img, (100, 100))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		
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
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()

class Ship:
    COOLDOWN = 20
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.ship_laser = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter +=1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser((self.x)+45, self.y, self.ship_laser)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=100)
        self.ship_img = ORANGE_SPACE_SHIP
        self.ship_laser = RED_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def lost(self):
        posx = self.x + 50
        posy = self.y + 50
        explosion = Explosion(posx, posy)
        explosion_group.add(explosion)

    def pick(self, obj):
        return collide(obj, self)

    def picked(self, objs):
        for obj in objs:
            if self.pick(obj):
                objs.remove(obj)
                self.health += 10

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        posx = obj.x + 50
                        posy = obj.y + 50
                        explosion = Explosion(posx, posy)
                        explosion_group.add(explosion)
                        self.lasers.remove(laser)
    
class Enemy(Ship):
    COLOR_MAP = {
                    'red': (RED_ENEMY_SHIP, RED_LASER),
                    'green': (GREEN_ENEMY_SHIP, GREEN_LASER),
                    'blue': (BLUE_ENEMY_SHIP, BLUE_LASER)
                 }

    COOLDOWN = 30
    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter +=1
            
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health=100)
        self.ship_img, self.ship_laser = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser((self.x)+30, self.y, self.ship_laser)
            self.lasers.append(laser)
            self.cooldown_counter = 1        

    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    levels = 0
    lives = 5
    main_font = pygame.font.SysFont('comcisans', 35)
    lost_font = pygame.font.SysFont('comicsans', 60)
    enemies = []
    medpacks = []
    wave_length = 5
    enemy_v = 1
    player = Player(330, 550)
    player_v = 5
    laser_v = 7
    lost = False
    lost_count = 0
    enel = len(enemies)
    score = -5

    def redraw_window():
        #draw background
        WIN.blit(BG, (0,0))

        #draw explosion
        explosion_group.draw(WIN)
        explosion_group.update()

        #draw text
        lives_label = main_font.render(f'Lives: {lives}', 1, (255,255,255))
        level_label = main_font.render(f'Level: {levels}', 1, (255,255,255))
        score_label = main_font.render(f'Score: {score}', 1, (255,255,255))
        health_label = main_font.render(f'Health: {player.health}', 1, (255,255,255))
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 340,10))
        WIN.blit(health_label, (WIDTH - health_label.get_width() - 10,625))

        #draw drops
        for hp in medpacks:
            hp.draw(WIN)
        #draw enemies
        for enemy in enemies:
            enemy.draw(WIN)
        #draw player
        player.draw(WIN)

         #draw lost
        if lost:
            player.lost()
            lost_label = lost_font.render('You Lost.', 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        if enel != len(enemies):
            score += 5
            enel = len(enemies)

        redraw_window()

        if lives<=0 or player.health<=0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS*3:
                run = False
            else:
                continue

        if len(medpacks)==0 and player.health != player.max_health:
            max_drop = 1
            for i in range(max_drop):
                hp = Medpack(random.randrange(70, WIDTH-90), random.randrange(70, WIDTH-90), MEDPACK)
                medpacks.append(hp)

        if len(enemies)==0:
            levels +=1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(70, WIDTH-90), random.randrange(-1500, -200), random.choice(['red','green','blue']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x-player_v>0:   #left
            player.x -= player_v
        if keys[pygame.K_s] and player.y+player_v+player.get_height()<HEIGHT:    #down
            player.y += player_v
        if keys[pygame.K_d] and player.x+player_v+player.get_width()<WIDTH:    #right
            player.x += player_v
        if keys[pygame.K_w] and player.y-player_v>0:    #up
            player.y -= player_v
        if keys[pygame.K_LEFT] and player.x-player_v>0:   #left
            player.x -= player_v
        if keys[pygame.K_DOWN] and player.y+player_v+player.get_height()<HEIGHT:    #down
            player.y += player_v
        if keys[pygame.K_RIGHT] and player.x+player_v+player.get_width()<WIDTH:    #right
            player.x += player_v
        if keys[pygame.K_UP] and player.y-player_v>0:    #up
            player.y -= player_v
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_v)
            enemy.move_lasers(laser_v, player)
            if random.randrange(0, 1*60) == 1:
                enemy.shoot()
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.picked(medpacks)
        player.move_lasers(-laser_v, enemies)
    
main()