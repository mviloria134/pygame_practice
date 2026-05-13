import pygame
import random

# global vars
pygame.init()
done = False
SCREEN_W = 1200
SCREEN_H = 800
PLAY_AREA_W = 4800
PLAY_AREA_H = 3200
screen = pygame.display.set_mode(size=(SCREEN_W, SCREEN_H),flags=pygame.RESIZABLE|pygame.SCALED)
clock = pygame.time.Clock()
framerate = 60
dt = clock.tick(framerate) / 1000

class PlayArea:
    def __init__(self):
        self.surf = pygame.Surface((PLAY_AREA_W, PLAY_AREA_H))
        self.rect = self.surf.get_rect(bottomleft=(0,PLAY_AREA_H))
        self.surf.fill((0,0,50))
    def display(self, display_surf:pygame.Surface):
        display_surf.blit(self.surf, self.rect)

class Player(pygame.sprite.Sprite):
    size = (60,60)
    world_coords = pygame.Rect((0,0), size)
    world_coords.center = (screen.get_size()[0]//2 ,screen.get_size()[1]//2)
    walk1 = pygame.transform.scale(pygame.image.load('player-walk-1.png').convert_alpha(), size)
    walk2 = pygame.transform.scale(pygame.image.load('player-walk-2.png').convert_alpha(), size)
    stand = pygame.transform.scale(pygame.image.load('player-sprite.png').convert_alpha(), size)
    walk_anim = [stand, walk1, stand, walk2]
    image = stand
    rect = image.get_rect(center=(screen.get_size()[0]//2 ,screen.get_size()[1]//2))
    acceleration = 50
    max_vel = 600
    
    def __init__(self):
        super().__init__()
        self.walk_anim_frame = 0
        self.walk_anim_timer = 0
        self.walk_anim_duration = framerate // 6
        self.is_walking = False
        
        self.image = self.stand
        self.velx = 0
        self.vely = 0
        self.health = 3
    
    def animate_walk(self):
        if self.walk_anim_timer%self.walk_anim_duration == 0:
            self.walk_anim_frame += 1
        self.image = self.walk_anim[self.walk_anim_frame % len(self.walk_anim)]
        self.walk_anim_timer += 1
        
    
    def keyboard_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.vely = max(self.vely - self.acceleration, -self.max_vel)
        if keys[pygame.K_s]:
            self.vely = min(self.vely + self.acceleration, self.max_vel)
        if keys[pygame.K_a]:
            self.velx = max(self.velx - self.acceleration, -self.max_vel)
        if keys[pygame.K_d]:
            self.velx = min(self.velx + self.acceleration, self.max_vel)
            
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.vely = 0
            self.is_walking = False
        else:
            self.is_walking = True
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.velx = 0
            self.is_walking = self.is_walking or False
        else:
            self.is_walking = True
        
    def move(self):
        self.world_coords.x += self.velx * dt
        self.world_coords.y += self.vely * dt
        if self.world_coords.left < 0 or self.world_coords.right > PLAY_AREA_W:
            if self.velx < 0:
                self.world_coords.left = 0
            elif self.velx > 0:
                self.world_coords.right = PLAY_AREA_W
            self.velx = 0
        else:
            self.rect.x += self.velx * dt
        if self.world_coords.top < 0 or self.world_coords.bottom > PLAY_AREA_H:
            if self.vely < 0:
                self.world_coords.top = 0
            elif self.vely > 0:
                self.world_coords.bottom = PLAY_AREA_H
            self.vely = 0
        else:
            self.rect.y += self.vely * dt
        # print(f'world: ({self.world_coords.x}, {self.world_coords.y}) screen: ({self.rect.x}, {self.rect.y})')
        
        
        if self.is_walking:
            self.animate_walk()
        else:
            self.image = self.stand
            self.walk_anim_timer = 0
            self.walk_anim_frame = 0
    
    def collide_with_enemy(self, enemy):
        self.health -= enemy.damage
        if self.health < 1:
            self.kill()
    
    def collide_with_item(self, item):
        print('got an item!')
    
    def update(self):
        self.keyboard_input()
        self.move()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed=100, x=screen.get_size()[0] // 4, y=screen.get_size()[1] //4):
        super().__init__()
        self.image = pygame.image.load('enemy-sprite.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.25)
        self.rect = self.image.get_rect(center=(x,y))
        

        self.damage = 1
        self.velx = random.choice([speed, -speed])
        self.vely = 0
        self.patrol_radius = 1000
        self.home = [x,y]
        
    def move(self):
        # check boundaries
        # if self.rect.left <= self.home[0] - self.patrol_radius or self.rect.right >= self.home[0] + self.patrol_radius:
        #     if self.velx < 0:
        #         self.rect.left = self.home[0] - self.patrol_radius
        #     else:
        #         self.rect.right = self.home[0] + self.patrol_radius
        #     self.velx = -self.velx
        if self.rect.left <= self.home[0] - self.patrol_radius or self.rect.right >= self.home[0] + self.patrol_radius:
            if self.velx < 0:
                self.rect.left = self.home[0] - self.patrol_radius
            else:
                self.rect.right = self.home[0] + self.patrol_radius
            self.velx = -self.velx
        self.rect.x += self.velx * dt
    
    def update(self):
        self.move()

class BounceEnemy(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        
class Item(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.image = pygame.image.load('item-sprite.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.25)
        if x is None:
            x = random.randint(0, screen.get_size()[0])
        if y is None:
            y = random.randint(0, screen.get_size()[1])
        self.rect = self.image.get_rect(center=(x,y))

class ItemSpawner(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.time_between_spawns = 3
        self.spawn_timer = 0
        self.max_items = 5
    
    def increase_spawn_timer(self):
        if self.spawn_timer < self.time_between_spawns:
            self.spawn_timer += dt
        elif self.__len__() < self.max_items:
            self.spawn_item()
        else:
            self.spawn_timer = 0
    
    def spawn_item(self):
        self.add(Item())
        
    def update(self):
        super().update()
        self.increase_spawn_timer()

class Camera:
    def __init__(self):
        self.marginx = 300
        self.marginy = 100
        self.boundsx = (self.marginx, screen.get_size()[0] - self.marginx)
        self.boundsy = (self.marginy, screen.get_size()[1] - self.marginy)
        
        self.surf = pygame.Surface((self.boundsx[1]-self.boundsx[0], self.boundsy[1]-self.boundsy[0]))
        self.world_coords = self.surf.get_rect(topleft=(self.marginx, self.marginy))
        
    def panh(self):
        for item in items:
                item.rect.x -= p.sprite.velx * dt
                
        for enemy in enemies:
            enemy.home[0] -= p.sprite.velx * dt
            enemy.rect.x -= p.sprite.velx * dt
        
        world.rect.x -= p.sprite.velx * dt
        
        if self.world_coords.x <= 0:
            self.world_coords.x 
            
    def panv(self):
        for item in items:
                item.rect.y -= p.sprite.vely * dt
                
        for enemy in enemies:
            enemy.home[1] -= p.sprite.vely * dt
            enemy.rect.y -= p.sprite.vely * dt
            
        world.rect.y -= p.sprite.vely * dt
    
    def pan(self):
        # horizontal panning
        if p.sprite.rect.left < self.boundsx[0]:
            self.panh()
            self.world_coords.left += p.sprite.velx * dt
            p.sprite.rect.left = self.boundsx[0]
        elif p.sprite.rect.right > self.boundsx[1]:
            self.panh()
            self.world_coords.right += p.sprite.velx * dt
            p.sprite.rect.right = self.boundsx[1]
            
        # vertical panning
        if p.sprite.rect.top <= self.boundsy[0]:
            p.sprite.rect.top = self.boundsy[0]
            self.panv()
        elif p.sprite.rect.bottom >= self.boundsy[1]:
            p.sprite.rect.bottom = self.boundsy[1]
            self.panv()
            
    
    def display(self, surf:pygame.Surface):
        surf.blit(self.surf, (self.marginx,self.marginy))

# initialize player group
p = pygame.sprite.GroupSingle()
p.add(Player())
respawn_timer = 0.5
respawn_countdown = respawn_timer

# initialize enemy group
enemies = pygame.sprite.Group()
max_enemies = 5

# initialize item spawner
items = ItemSpawner()

# initialize camera
camera = Camera()

world = PlayArea()

score = 0
UPDATE_SCORE = pygame.USEREVENT + 1
pygame.time.set_timer(UPDATE_SCORE, 1000)

while not done: 
    # event checks
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        # if event.type == UPDATE_SCORE:
        #     score += 1
        #     print(score)
    
    #draw
    # bg
    screen.fill((30,30,30))
    
    # spawn enemies
    while enemies.__len__() < max_enemies:
        enemies.add(Enemy(x=random.randint(0,PLAY_AREA_W),y=random.randint(0,SCREEN_H)))
    
    # update functions
    p.update()
    enemies.update()
    items.update()
    
    # check if player sprite exists
    if not p.sprite:
        if respawn_countdown > 0:
            respawn_countdown -= dt
        else:
            # reset respawn countdown
            respawn_countdown = respawn_timer
            p.add(Player())
    else:
        camera.pan()
        # collision checks
        # with items
        collisions = pygame.sprite.spritecollide(p.sprite, items, True)
        for item in collisions:
            p.sprite.collide_with_item(item)
            
        # with enemies
        collisions = pygame.sprite.spritecollide(p.sprite, enemies, True)
        for enemy in collisions:
            p.sprite.collide_with_enemy(enemy)
            
    
    
    # camera.display(screen)
    world.display(screen)
    p.draw(screen)
    enemies.draw(screen)
    items.draw(screen)
    
    
    # update display
    pygame.display.flip()
    
    dt = clock.tick(framerate) / 1000
    
    
pygame.quit()