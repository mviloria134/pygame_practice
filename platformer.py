import pygame
import random

# window settings
SCREEN_W = 1200
SCREEN_H = 900
screen = pygame.display.set_mode((SCREEN_W,SCREEN_H), flags=pygame.RESIZABLE|pygame.SCALED)

framerate = 60
clock = pygame.time.Clock()
dt = clock.tick(framerate) / 1000

is_running = True

# user events
RESPAWN_PLAYER = pygame.USEREVENT + 1
SPAWN_ENEMY    = pygame.USEREVENT + 2
SPAWN_PLATFORM = pygame.USEREVENT + 3

# other global constants
GRAVITY = 5000
FRICTION = 2000

# classes
class PlatformCollider:
    def __init__(self):
        self.is_grounded = False
        self.can_jump = False
    
    def collide_h(self):
        platforms_collided = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platforms_collided:
            if self.dirx > 0:
                self.rect.right = platform.rect.left
            else:
                self.rect.left = platform.rect.right
            
    def collide_v(self):
        platforms_collided = pygame.sprite.spritecollide(self, platforms, False)
        if pygame.sprite.collide_rect(self, ground.sprite): platforms_collided.append(ground.sprite)
        if not platforms_collided:
            self.is_grounded = False
            self.can_jump = False
        else:
            for platform in platforms_collided:         
                if self.vely >= 0:
                    if platform is not ground.sprite and self is player_spawner.sprite:
                        platform.collect()
                    self.rect.bottom = platform.rect.top
                    self.is_grounded = True
                    self.can_jump = True
                    self.vely = 0
                    return
                else:
                    self.vely = 0
                    self.rect.top = platform.rect.bottom

class Player(pygame.sprite.Sprite, PlatformCollider):
    def __init__(self, *groups, pos:tuple=None):
        super().__init__(*groups)
        self.posx, self.posy = map(lambda n: n//2, screen.get_size()) if pos is None else pos
        self.velx = 0
        self.top_speed = 800
        self.accelx = 0
        self.walk_accel = 100
        self.dirx = 0
        self.vely = 0
        self.jump_power = 1500
        
        self.invincibility_seconds = 0.5
        self.invincibility_timer = 0
        self.knockback_direction = 0
        
        self.image = pygame.image.load("player-sprite.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.25)
        self.rect = self.image.get_rect(center=(self.posx,self.posy))
    
    def move(self):
        # get user input
        self.keyboard_input()
        
        # update horizontal position
        self.velx = min(max(-self.top_speed, self.velx + self.accelx), self.top_speed)
        if self.velx < 0:
            self.velx += FRICTION * dt
        elif self.velx > 0:
            self.velx -= FRICTION * dt

        self.collide_enemy_h()
        self.rect.x += self.velx * dt
        
        self.collide_h()
        
        # update vertical position
        self.vely += GRAVITY * dt
        self.rect.y += (self.vely * dt)
        self.collide_v()
        
    def keyboard_input(self):
        keys = pygame.key.get_pressed()
        
        # horizontal movement
        if keys[pygame.K_a]:
            self.accelx = -self.walk_accel
        elif keys[pygame.K_d]:
            self.accelx = self.walk_accel
        else:
            self.accelx = 0
            
        # vertical movement
        if keys[pygame.K_SPACE] and self.can_jump:
            self.vely -= self.jump_power
            self.is_grounded = False
            self.can_jump = False
            
    def collide_enemy_h(self):
        collided = pygame.sprite.spritecollide(self, enemy_spawner, False)
        if self.invincibility_timer >= self.invincibility_seconds:
            if collided:
                self.invincibility_timer = 0
                self.knockback(obj=collided[0])
        else:
            self.invincibility_timer += clock.get_time() / 1000
        
    def knockback(self, obj:pygame.sprite.Sprite=None):
        if obj:
            if obj.rect.right <= self.rect.right:
                self.knockback_direction = 1
            elif obj.rect.left >= self.rect.left:
                self.knockback_direction = -1
            
            self.velx += self.knockback_direction * obj.knockback_strength
        
        
    def update(self):
        self.move()

class PlayerSpawner(pygame.sprite.GroupSingle):
    def __init__(self, sprite = None):
        super().__init__(sprite)
        self.respawn_timer = 2

class Enemy(pygame.sprite.Sprite, PlatformCollider):
    def __init__(self, *groups, pos:tuple=(400,0)):
        super().__init__(*groups)
        self.velx = 300
        self.vely = 0
        self.dirx = random.choice([-1,1])
        self.knockback_strength = 4000
        
        self.image = pygame.image.load('enemy-sprite.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.5)
        self.rect = self.image.get_rect(center=pos)
        
    def move(self):
        self.follow_player()
        self.rect.x += self.dirx * self.velx * dt
        self.collide_h()
        self.collide_enemy_h()
        
        self.vely += GRAVITY * dt
        self.rect.y += (self.vely/2) * dt
        if self.rect.y > ground.sprite.rect.top:
            self.kill()
        self.collide_v()
        self.collide_enemy_v()
    
    def follow_player(self):
        player = player_spawner.sprite
        if player.rect.right < self.rect.left:
            self.dirx = -1
        elif player.rect.left > self.rect.right:
            self.dirx = 1
        else:
            self.dirx = 0
            
    def collide_enemy_h(self):
        enemies_collided = pygame.sprite.spritecollide(self, enemy_spawner, False)
        for enemy in enemies_collided:
            if enemy is self:
                continue
            if self.dirx > 0:
                self.rect.right = enemy.rect.left
            else:
                self.rect.left = enemy.rect.right
            
    def collide_enemy_v(self):
        enemies_collided = pygame.sprite.spritecollide(self, enemy_spawner, False)
        if pygame.sprite.collide_rect(self, ground.sprite): enemies_collided.append(ground.sprite)
        for enemy in enemies_collided:
            if enemy is self:
                continue       
            if self.vely > 0:
                self.rect.bottom = enemy.rect.top
                self.is_grounded = True
                self.can_jump = True
            else:
                self.rect.top = enemy.rect.bottom
            self.vely = 0
    
    def update(self):
        self.move()

class EnemySpawner(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        
        self.spawn_time_min = 1
        self.spawn_time_max = 5
        self.max_enemies = 5
    
    def set_spawn_timer(self):
        pygame.time.set_timer(SPAWN_ENEMY, random.randint(self.spawn_time_min,self.spawn_time_max) * 1000, 1)
    
    def spawn_enemies(self):
        if self.__len__() < self.max_enemies:
            self.add(Enemy())
            self.set_spawn_timer()

class Platform(pygame.sprite.Sprite):
    color_collected = (100,200,100)
    def __init__(self, *groups, size:tuple=(100,50), pos:tuple=(0,0), color=(0,50,0)):
        super().__init__(*groups)
        self.size = size
        self.pos = pos
        self.color = color
        self.is_collected = False
        self.despawn_timer = 3
        
        self.image = pygame.surface.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=self.pos)
    
    def collect(self):
        self.image.fill(self.color_collected)
        self.is_collected = True
    
    def update(self):
        if self.is_collected:
            self.despawn_timer -= dt
            if self.despawn_timer <= 0:
                self.kill()

class Platform_Spawner(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.max_platforms = 5
       
        
class Camera():
    def __init__(self, cam_bounds:tuple=(200,200)):
        self.bounds = cam_bounds
        self.surf = pygame.Surface((screen.get_size()[0]-self.bounds[0]*2, screen.get_size()[1]-self.bounds[1]*2))
        self.surf.fill((255,255,255))
        
    
    def is_in_camera_bounds(self):
        player = player_spawner.sprite
        return self.bounds[0] <= player.rect.left and player.rect.right <= screen.get_size()[0]-self.bounds[0]
    
    def pan(self):
        player = player_spawner.sprite
        if  not self.is_in_camera_bounds():
            shift = player.velx * dt
            for platform in platforms.sprites():
                platform.rect.x -= shift
            for enemy in enemy_spawner.sprites():
                enemy.rect.x -= shift
            
            if shift < 0:
                player.rect.left = self.bounds[0]
            else:
                player.rect.right = screen.get_size()[0]-self.bounds[0]
                
    def display(self):
        screen.blit(self.surf, self.bounds)
            

# initialize entities
player_spawner = PlayerSpawner(Player())
enemy_spawner = EnemySpawner()
enemy_spawner.spawn_enemies()

ground = pygame.sprite.GroupSingle(Platform(size=(screen.get_size()[0],screen.get_size()[1]//5), pos=((screen.get_size()[0]//2,screen.get_size()[1])), color=Platform.color_collected))
platforms = Platform_Spawner()
platforms.add(Platform(pos=(100,600)))
platforms.add(Platform(pos=(400,700)))
platforms.add(Platform(pos=(600,750)))


camera = Camera()

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        if event.type == SPAWN_ENEMY:
            enemy_spawner.spawn_enemies()
    
    # update
    player_spawner.update()
    if enemy_spawner.sprites():
        enemy_spawner.update()
    else:
        enemy_spawner.spawn_enemies()
    ground.update()
    platforms.update()
    camera.pan()
    
    
    # draw
    screen.fill((0,0,50))
    camera.surf.fill((40,0,0))
    camera.display()
    player_spawner.draw(screen)
    enemy_spawner.draw(screen)
    platforms.draw(screen)
    ground.draw(screen)
    
    # refresh screen
    pygame.display.flip()
    
    dt = clock.tick(framerate) / 1000
            

pygame.quit()