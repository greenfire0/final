import pygame
from pygame.locals import *
import sys
import random
import math
import time
 
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 450
WIDTH = 1200
ACC = 0.5
FRIC = -0.12
FPS = 60
global speed
global lose
lose= False
speed = 0.6
points = 0
time_at_last_spawn = 3
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

def gravity_collision(a,b):
    #this checks for collisions with mostly the platform
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_s]:
        return False
    return a.rect.colliderect(b.rect)
def platform_collide(a,b):
    #this just for the bottem
    offset = ((0, (int(a.posy - b.posy)-6.5)))
    if (a.mask.overlap(b.mask, offset)):
        return True
    return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.mask = pygame.mask.from_surface(pygame.Surface((15, 1)))
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128,255,40))
        
        self.can_shoot = True
        self.last_shot_time = 1
        self.shooting_delay = 1

        #speed controls
        self.posx = 100
        self.posy = 100
        self.velx = 0
        self.vely = 0
        self.accx = 0
        self.accy = 0
        self.rect = self.surf.get_rect(center = (self.posx,self.posy))

    def update(self, platform,floating):
        ##main control
        self.move(platform,floating)
        self.gravity(platform,floating)
        if (time.time() - self.last_shot_time) > self.shooting_delay: self.shoot()

    def move(self,platform,floating):
        self.accx = 0
        global speed
        pressed_keys = pygame.key.get_pressed()
        
        # i think we should make wasd moving and arrow keys shooting 
        if pressed_keys[K_a]:
            self.accx = -ACC - speed
            ##look into this later
        if pressed_keys[K_d]:
            self.accx = ACC +speed
        if pressed_keys[K_w]:
            ##3this needs to be touching ground
            if platform_collide(self,platform) or gravity_collision(self,floating):
                self.accy = -ACC -20
            

        self.accx += ((self.velx * FRIC))
        self.accy += (self.vely * FRIC)
        self.velx += self.accx
        self.vely += self.accy
        self.posx += self.velx + 0.5 * self.accx
        self.posy += self.vely + 0.5 * self.accy
        if self.posx < 0:
            self.posx = WIDTH
        if self.posx > WIDTH:
            self.posx = 0
        self.rect.midbottom = (self.posx,self.posy)
    
        
    def gravity(self,platform,floating):
        a = platform_collide(self,platform) or gravity_collision(self,floating)
        if a:
            self.accy = 0
            self.vely = 0
        else:
            self.accy = 0.5
            
    def shoot(self):
        pressed_keys = pygame.key.get_pressed()
        ##these controll the shooting
        if pressed_keys[K_LEFT]:
            b = bullet(self.posx, self.posy - 20, "LEFT")
            bullets.append(b)
            all_sprites.add(b)
            self.can_shoot = False
            self.last_shot_time = time.time()
        if pressed_keys[K_RIGHT]: 
            b = bullet(self.posx, self.posy - 29, "RIGHT")
            bullets.append(b)
            all_sprites.add(b)
            self.can_shoot = False
            self.last_shot_time = time.time()
        if pressed_keys[K_UP]:
            b = bullet(self.posx, self.posy - 30, "UP")
            all_sprites.add(b)
            bullets.append(b)
            self.can_shoot = False
            self.last_shot_time = time.time()
    

            
 
class food(pygame.sprite.Sprite):
    ##these are the food the enemies drop
    def __init__(self,posx = 0,posy = 500):
        super().__init__()
        self.posx = posx
        self.posy = posy
        self.surf = pygame.Surface((10,10))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (self.posx,self.posy))
    
    def update(self,P1):
        self.collide(P1)

    def collide(self,P1):
        if self.rect.colliderect(P1.rect):
            all_sprites.remove(self)
            foods.remove(self)
            global speed
            global points
            points += 1
            speed +=0.05
            
class enemy(pygame.sprite.Sprite):
    def __init__(self, size, health, posx, posy):
        super().__init__()
        self.posx = posx
        self.posy = posy
        self.size = size
        self.health = health
        self.surf = pygame.Surface((self.size, self.size))
        # self.mask = pygame.mask.from_surface(pygame.Surface((self.size*2, self.size*2)))
        self.mask = pygame.mask.from_surface(self.surf)
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (self.posx,self.posy))
        
    def update(self, P1, bullets):
        self.collide(P1, bullets)
        self.move(P1)
        
    def collide(self, P1, bullets):
        global lose
        if self.rect.colliderect(P1.rect):
            print("hi")
            lose= True
            all_sprites.remove(P1)
            # kills the player
        for b in bullets:
            if self.rect.colliderect(b.rect):
                self.health -= 1
                if self.health == 0:
                    all_sprites.remove(self)
                    enemies.remove(self)
                    f = food(self.posx, self.posy + 10)
                    all_sprites.add(f)
                    foods.append(f)
                all_sprites.remove(b)
                bullets.remove(b)
                           
    def move(self, P1):
        distX = self.posx - P1.posx
        distY = self.posy - P1.posy
        distance = math.sqrt(distX**2 + distY**2)
        self.posx -= distX/distance
        self.posy -= distY/distance
        self.rect.midbottom = (self.posx,self.posy)
        
            
            
class bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy, direction):
        super().__init__()
        self.posx = posx
        self.posy = posy
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255,255,255))
        self.mask = pygame.mask.from_surface(self.surf)
        self.rect = self.surf.get_rect(center = (self.posx,self.posy))
        self.direction = direction
        self.vel = 8
        
    def update(self):
        self.move()
        
    def move(self):
        match self.direction:
            case "UP":
                self.posy -= self.vel
                self.rect.midbottom = (self.posx,self.posy)
            case "LEFT":
                self.posx -= self.vel
                self.rect.midbottom = (self.posx,self.posy)
            case "RIGHT":
                self.posx += self.vel
                self.rect.midbottom = (self.posx,self.posy)

    
            
        


class platform(pygame.sprite.Sprite):
    def __init__(self):
    

        super().__init__()
        
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))
        self.mask = pygame.mask.from_surface(self.surf)
        self.posy =  HEIGHT - 10
    def extend(self):
        
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))
        
class floating(pygame.sprite.Sprite):
    def __init__(self, posx, posy, width) -> None:
        super().__init__()
        self.posy =  posy
        self.posx = posx
        self.surf = pygame.Surface((width, 10))
        self.surf.fill((255,255,255))
        self.rect = self.surf.get_rect(center = (self.posx, self.posy))
        self.mask = pygame.mask.from_surface(self.surf)
        self.posy =  HEIGHT - 100
    
    def extend(self):
        self.posx= random.randint(0,WIDTH)
        self.posy= HEIGHT - random.randint(40,120)
        self.surf = pygame.Surface((50, 10))
        self.surf.fill((255,255,255))
        self.rect = self.surf.get_rect(center = (self.posx, self.posy))
        self.mask = pygame.mask.from_surface(self.surf)

 
PT1 = platform()
P1 = Player()
foods = []
f = food()
floating = floating(WIDTH/2, HEIGHT - 100, WIDTH)
bullets = []
enemies = []

font = pygame.font.Font(None,32)




all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
all_sprites.add(f)
all_sprites.add(floating)
all_sprites.add(bullets)

lose = False
while True:
    if not lose:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        displaysurface.fill((0,0,0))
        if time.time() - time_at_last_spawn > 3:
            if random.choice([True, False]):
                posx = -10
            else:
                posx = WIDTH + 10
            posy = random.randint(40, HEIGHT + 50)
            e = enemy(75, int(math.log(speed + 1))+1, posx, posy)
            all_sprites.add(e)
            enemies.append(e)
            time_at_last_spawn = time.time()
        for entity in all_sprites:
            displaysurface.blit(entity.surf, entity.rect)
        P1.update(PT1,floating)
        for f in foods:
            f.update(P1)
        for e in enemies:
            e.update(P1, bullets)
        for b in bullets:
            b.update()
    else:
            pygame.display.update()
            FramePerSec.tick(FPS)
    if lose:
        for a in all_sprites:
            all_sprites.remove(a)
        score = font.render("YOU LOSE. YOU CANNOT PLAY AGAIN UNLESS YOU GIVE US BTC.", True, (255,255,255))
        displaysurface.blit(score,(0,HEIGHT/2))
        pygame.display.update()
        FramePerSec.tick(FPS)
    else:
        score = font.render("Score :" + str(points), True, (255,255,255))
        displaysurface.blit(score,(0,0))
        pygame.display.update()
        FramePerSec.tick(FPS)