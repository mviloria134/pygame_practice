import pygame
from pygame.event import Event
from pygame.sprite import Sprite, Group
from dodger import load_image_from_file

pygame.init()

SCREEN_W = 1200
SCREEN_H = 900
SCREEN_Z = 500
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

framerate = 60
clock = pygame.time.Clock()
dt = clock.tick(framerate) / 1000

is_running = True

# def cache_image_scales_at_z(img:pygame.Surface, z_size:int):
#     cache = {}
    
#     for i in range(z_size):
#         cache[i] = 

def z_to_relative_scale(zpos:int):
    scale_per_z = 1 / SCREEN_Z
    
    return max(1 - (scale_per_z * zpos), scale_per_z )

print(z_to_relative_scale(1))

class Player(Sprite):
    _cache = {}
    def __init__(self, *groups):
        super().__init__(*groups)
        
        self.original_image = load_image_from_file('player-sprite.png')
        
        # self._cache
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
        
        self.z = 0
        self.accelz = 500
        self.dirx = 0
        self.accelx = 300
        
    def update(self):
        self.get_input()
        self.move()
    
    def get_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.z += self.accelz * dt
        if keys[pygame.K_s]:
            self.z -= self.accelz * dt
        if keys[pygame.K_a]:
            self.dirx = -1
        elif keys[pygame.K_d]:
            self.dirx = 1
        else:
            self.dirx = 0
    
    def move(self):
        self.get_input()
        
        self.image = pygame.transform.scale_by(self.original_image, z_to_relative_scale(self.z))
        self.rect = self.image.get_rect(center=(self.rect.center))
        
        self.rect.x += self.dirx * self.accelx * dt
        
        
player_group = Group(Player())

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            
            
    player_group.update()
    
    
    
    
    screen.fill((0,0,50))
    player_group.draw(screen)
    
    pygame.display.flip()
    
    dt = clock.tick(framerate) / 1000
            
pygame.quit()