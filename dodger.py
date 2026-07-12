import pygame
from enum import Enum

pygame.init()

SCREEN_W = 1200
SCREEN_H = 900
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

clock = pygame.time.Clock()
framerate = 60
dt = clock.tick(framerate) / 1000

# game states
class GameState(Enum):
    GAME_OVER = 0
    PLAYING = 1
    MAIN_MENU = 2

game_state = GameState.PLAYING

# events
START_GAME = pygame.event.custom_type()

# helper functions
def load_image_from_file(path:str, scale_to_size:tuple[int,int]=None, scale_by_factor:float=None) -> pygame.surface.Surface:
    image = pygame.image.load(path).convert_alpha()
    if scale_to_size:
        image = pygame.transform.scale(image, scale_to_size)
    elif scale_by_factor:
        image = pygame.transform.scale_by(image, scale_by_factor)
        
    return image

# entities
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        
        self.image = load_image_from_file('item-sprite.png', (50,50))
        self.image = pygame.transform.rotate(self.image, -90)
        self.rect = self.image.get_rect(center=(100, SCREEN_H//2))

class PlayerSpawner(pygame.sprite.GroupSingle):
    def __init__(self, sprite = None):
        super().__init__(sprite)
        self.respawn_seconds = 2
        self.respawn_timer = 0
    
    def update(self, *args, **kwargs):
        if self.sprite:
            super().update(*args, **kwargs)
        else:
            if self.respawn_timer < self.respawn_seconds:
                self.respawn_timer += dt
            else:
                self.respawn_timer = 0
                self.spawn_player()

    
    def spawn_player(self):
        if self.sprite:
            self.empty()
            
        self.add(Player())
    
    
# UI classes
class Background:
    def __init__(self, background_img_path:str):
        self.img = load_image_from_file(background_img_path, (SCREEN_W, SCREEN_H))
        
    def display(self):
        screen.blit(self.img, (0,0))
        
class ScrollingBackground(Background):
    def __init__(self, background_img_path:str, speed:int):
        super().__init__(background_img_path)              
        self.speed = speed
        self.xpos1 = 0
        self.xpos2 = SCREEN_W
        
    def update(self):
        self.scroll()
        
    def scroll(self):
        self.xpos1 -= self.speed * dt
        if self.xpos1 < -SCREEN_W:
            self.xpos1 = SCREEN_W
            
        self.xpos2 -= self.speed * dt
        if self.xpos2 < -SCREEN_W:
            self.xpos2 = SCREEN_W
        
    def display(self):
        screen.blit(self.img, (self.xpos1, 0))
        screen.blit(self.img, (self.xpos2, 0))
        
class Scene:
    def __init__(self):
        self.bgs = []
        
    def update(self):
        for bg in self.bgs:
            bg.update()
            
    def display(self):
        for bg in self.bgs:
            bg.display()
        
# initialize sprite groups
player_spawner = PlayerSpawner()

# initialize UI classes
in_game_bg = ScrollingBackground(background_img_path='background.png', speed=100)
in_game_fg = ScrollingBackground(background_img_path='bg cloudiness.png', speed=250)
in_game_scene = Scene()
in_game_scene.bgs.append(in_game_bg)
in_game_scene.bgs.append(in_game_fg)

# switch game states
def start_game():
    player_spawner.spawn_player()


# start game
pygame.event.post(pygame.event.Event(START_GAME))

    
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == START_GAME:
            game_state = GameState.PLAYING
            start_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                player_spawner.empty()
    
    if game_state == GameState.PLAYING:
        # update entities
        player_spawner.update()
        
        
        # update UI
        in_game_scene.update()
        
        # draw
        screen.fill((0,0,50))
        in_game_scene.display()
        player_spawner.draw(screen)
        
    pygame.display.flip()
    dt = clock.tick(framerate) / 1000
    