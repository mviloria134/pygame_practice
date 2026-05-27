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

# colors
WHITE = (255,255,255)


# events
UPDATE_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(UPDATE_TIMER, 1000)
COLLECT_ITEM = pygame.USEREVENT + 2

class PlayArea:
    def __init__(self):
        self.surf = pygame.Surface((PLAY_AREA_W, PLAY_AREA_H))
        self.rect = self.surf.get_rect(bottomleft=(0,PLAY_AREA_H))
        self.surf.fill((0,0,50))
        
    def display(self, display_surf:pygame.Surface):
        display_surf.blit(self.surf, self.rect)

class Player(pygame.sprite.Sprite):
    size = (60,60)
    # world_coords = pygame.Rect((0,0), size)
    # world_coords.center = (screen.get_size()[0]//2 ,screen.get_size()[1]//2)
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
        self.rect.x += self.velx * dt
        self.rect.y += self.vely * dt
        self.rect.clamp_ip(world.rect)
        
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
    
    def update(self):
        self.keyboard_input()
        self.move()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed=100, x=screen.get_size()[0] // 4, y=screen.get_size()[1] //4):
        super().__init__()
        self.image = pygame.image.load('enemy-sprite.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.25)
        self.rect = self.image.get_rect(center=(x,y))
        self.rect.clamp_ip(world.rect)

        self.damage = 1
        self.velx = random.choice([speed, -speed])
        self.vely = 0
        self.patrol_radius = 1000
        self.home = [x,y]
        
    def move(self):
        if self.rect.left <= self.home[0] - self.patrol_radius or self.rect.right >= self.home[0] + self.patrol_radius:
            if self.velx < 0:
                self.rect.left = self.home[0] - self.patrol_radius
            else:
                self.rect.right = self.home[0] + self.patrol_radius
            self.velx = -self.velx
        
        self.rect.x += self.velx * dt
        if not world.rect.contains(self.rect):
            self.velx = -self.velx
    
    def update(self):
        self.move()

class BounceEnemy(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        
class Item(pygame.sprite.Sprite):
    extra_spawn_area = 100
    def __init__(self, x=None, y=None):
        super().__init__()
        self.image = pygame.image.load('item-sprite.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.25)
        if x is None:
            x = random.randint(0-self.extra_spawn_area, screen.get_size()[0]+self.extra_spawn_area)
        if y is None:
            y = random.randint(0-self.extra_spawn_area, screen.get_size()[1]+self.extra_spawn_area)
        self.rect = self.image.get_rect(center=(x,y))
        self.rect.clamp_ip(world.rect)

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

class HealthBar:
    size = 20
    def __init__(self, entity, attached_to_entity = False):
        self.entity = entity
        self.image = self.entity.image
        self.image = pygame.transform.scale(self.image, (self.size,self.size))
        self.attached_to_entity = attached_to_entity
        if self.attached_to_entity:
            self.rect = pygame.Rect(0,0,self.size*self.entity.health,self.size)
            self.rect.midbottom = entity.rect.midtop
        
        self.outer_padding_x = 10
        self.outer_padding_y = 10
        self.inner_padding = 10
        
    def display(self):
        if not self.attached_to_entity:
            y = 0
            for i in range(self.entity.health):
                screen.blit(self.image, (((self.size + self.inner_padding) * i) + self.outer_padding_x, y+self.outer_padding_y))
        else:
            self.rect.midbottom = self.entity.rect.midtop
            for i in range(self.entity.health):
                screen.blit(self.image, (self.rect.left + (i * self.size), self.rect.y-self.outer_padding_y))

class TimerDisplay:
    def __init__(self, initial_seconds=10, font_size=30):
        self.time_remaining = initial_seconds
        self.font = pygame.font.SysFont('MultiType Pixel', font_size)
        self.time_text = self.font.render(str(self.time_remaining), False, WHITE)
        self.rect = self.time_text.get_rect(topright=(screen.get_size()[0],0))
        
    def add_seconds(self, seconds):
        self.time_remaining += seconds
        self.update_text()
    
    def update_text(self):
        self.time_text = self.font.render(str(self.time_remaining), False, WHITE)
        self.rect = self.time_text.get_rect(topright=(screen.get_size()[0],0))
    
    def display(self):
        screen.blit(self.time_text, self.rect)
    
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

# UI Elements
player_healthbar = HealthBar(p.sprite)
game_timer = TimerDisplay()

world = PlayArea()

while not done: 
    # event checks
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == UPDATE_TIMER:
            game_timer.add_seconds(-1)
        if event.type == COLLECT_ITEM:
            game_timer.add_seconds(5)
    
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
            player_healthbar = HealthBar(p.sprite)
            
    else:
        camera.pan()
        # collision checks
        # with items
        collisions = pygame.sprite.spritecollide(p.sprite, items, True)
        for item in collisions:
            pygame.event.post(pygame.event.Event(COLLECT_ITEM))
            
        # with enemies
        collisions = pygame.sprite.spritecollide(p.sprite, enemies, True)
        for enemy in collisions:
            p.sprite.collide_with_enemy(enemy)
            
    
    
    # camera.display(screen)
    world.display(screen)
    p.draw(screen)
    enemies.draw(screen)
    items.draw(screen)
    
    # UI
    player_healthbar.display()
    game_timer.display()
    
    # update display
    pygame.display.flip()
    
    dt = clock.tick(framerate) / 1000
    
    
pygame.quit()