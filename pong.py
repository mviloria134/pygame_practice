import pygame
import random
from abc import ABC, abstractmethod

# initialize game
pygame.init()
is_running = True

# initialize screen
SCREEN_W = 1200
SCREEN_H = 900
screen = pygame.display.set_mode((SCREEN_W,SCREEN_H), flags=pygame.RESIZABLE|pygame.SCALED)
default_font = pygame.font.SysFont("MultiType Pixel", 72)

# set frame rate and clock
clock = pygame.time.Clock()
framerate = 60
dt = clock.tick(framerate) / 1000

# other global variables
p1_score = 0
p2_score = 0

# custom events
INCREMENT_P1       = pygame.USEREVENT + 1
INCREMENT_P2       = pygame.USEREVENT + 2
SPAWN_ITEM         = pygame.USEREVENT + 3
DEACTIVATE_GROW_P1 = pygame.USEREVENT + 4
DEACTIVATE_GROW_P2 = pygame.USEREVENT + 5
ANNOUNCEMENT_TIMER = pygame.USEREVENT + 6

# helper functions
def get_random_coords(xmin:int=0, xmax:int=SCREEN_W, ymin:int=0, ymax:int=SCREEN_H) -> tuple:
    return (random.randint(xmin, xmax), random.randint(ymin, ymax))

# classes

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups, player_number:int):
        super().__init__(*groups)
        distance_from_wall = 100
        self.player_number = player_number
        self.vel = 800
        self.width = 20
        self.height = 150
        
        self.image = pygame.surface.Surface(size=(self.width,self.height))
        self.image.fill((255,255,255))
        
        self.rect = self.image.get_rect(midleft=(distance_from_wall, screen.get_size()[1]//2)) if not player_number else self.image.get_rect(midright=(screen.get_size()[0]-distance_from_wall, screen.get_size()[1]//2))
        
    def move(self):
        keys = pygame.key.get_pressed()
        if not self.player_number:
            if keys[pygame.K_w]:
                self.rect.y -= self.vel * dt
            if keys[pygame.K_s]:
                self.rect.y += self.vel * dt
        else:
            if keys[pygame.K_UP]:
                self.rect.y -= self.vel * dt
            if keys[pygame.K_DOWN]:
                self.rect.y += self.vel * dt
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > screen.get_size()[1]:
            self.rect.bottom = screen.get_size()[1]
            
    def change_size(self, w:int=None, h:int=None):
        if w is None:
            w=self.width
        if h is None:
            h=self.height
        
        self.image = pygame.transform.scale(self.image, (w,h))
        self.rect = self.image.get_rect(center=(self.rect.center))
            
                
    def update(self):
        self.move()

class Ball(pygame.sprite.Sprite):
    def __init__(self, *groups, vely=None, velx=None, x=None, y=None, is_multiball=False):
        super().__init__(*groups)
        if x is None:
            self.spawnx = screen.get_size()[0]//2
        else:
            self.spawnx = x
        if y is None:
            self.spawny = 50
        else:
            self.spawny = y 
            
        if is_multiball:
            self.image = pygame.image.load('player-sprite.png').convert_alpha()
            self.image = pygame.transform.scale_by(self.image, 0.1)
        else:
            self.image = pygame.image.load('enemy-sprite.png').convert_alpha()
            self.image = pygame.transform.scale_by(self.image, 0.3)
            
        self.rect = self.image.get_rect(midtop = (self.spawnx,self.spawny))
        
        if vely is None:
            self.vely = random.randint(100,1000)
        else:
            self.vely = vely
        if velx is None:
            self.velx = 500 * random.choice([-1,1])
        else:
            self.velx = velx
        
        self.last_player_hit = -1
        
    def move(self):
        # going off left side
        if self.rect.left < 0:
            pygame.event.post(pygame.event.Event(INCREMENT_P2))
            self.kill()
        # going off right side
        elif screen.get_size()[0] < self.rect.right:
            pygame.event.post(pygame.event.Event(INCREMENT_P1))
            self.kill()
            
        if screen.get_size()[1] < self.rect.bottom or self.rect.top < 0:
            self.vely = -self.vely
            self.image = pygame.transform.flip(self.image, 0, 1)
        self.rect.x += self.velx * dt
        self.rect.y += self.vely * dt
    
    def collide_with_player(self, player:Player):
        # print(f'collided with player {player.player_number+1}')
        self.last_player_hit = player.player_number
        
        if self.rect.left <= player.rect.right or self.rect.right >= player.rect.left:
            self.velx = -self.velx
            # player 2
            if player.player_number:
                self.rect.right = player.rect.left
            # player 1
            else:
                self.rect.left = player.rect.right
                
    def get_player(self):
        return players.sprites()[self.last_player_hit]

    def update(self):
        collision = pygame.sprite.spritecollideany(self, players)
        if collision:
            self.collide_with_player(collision)
        self.move()
        
class BallSpawner(pygame.sprite.GroupSingle):
    def __init__(self, sprite = None):
        super().__init__(sprite)
        self.spawn_cooldown = 3.0
        self.respawn_timer = self.spawn_cooldown
        
    def respawn_ball(self):        
        if self.respawn_timer <= 0:
            self.add(Ball())
            self.respawn_timer = self.spawn_cooldown
        else:
            self.respawn_timer -= dt

class MultiballSpawner(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

class ItemSpawner(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.max_items = 5
        self.seconds_between_spawns = 1
        
    def set_spawn_timer(self):
        pygame.time.set_timer(pygame.event.Event(SPAWN_ITEM), self.seconds_between_spawns * 1000)
    
    def spawn_item(self):
        if (self.__len__() < self.max_items):
            type_to_spawn = random.randint(0,2)
            coords = get_random_coords(screen.get_size()[0]//4, screen.get_size()[0]//4 * 3, screen.get_size()[1]//4,screen.get_size()[1]//4 * 3)
            match type_to_spawn:
                case 0:
                    self.add(BallSpeedUpItem(coords=coords))
                case 1:
                    self.add(GrowItem(coords=coords))
                case 2:
                    self.add(MultiballItem(coords=coords))

class Item(pygame.sprite.Sprite, ABC):
    def __init__(self, *groups, coords:tuple):
        super().__init__(*groups)
        
        self.image = pygame.surface.Surface((50,50))
        self.rect = self.image.get_rect(center=coords)
    
    @property
    @abstractmethod
    def name(self):
        return 'default item'
    
    @abstractmethod
    def activate(self, ball:Ball):
        item_announcer.announce(self.name, ball.last_player_hit+1)
        
class BallSpeedUpItem(Item):
    def __init__(self, *groups, coords):
        super().__init__(*groups, coords=coords)
        self.color = (0,100,0)
        self.image.fill(self.color)
    
    @property
    def name(self):
        return "Speed Up"
        
    def activate(self, ball):
        super().activate(ball)
        ball.velx *= 2
        ball.vely *= 2

class GrowItem(Item):
    def __init__(self, *groups, coords):
        super().__init__(*groups, coords=coords)
        self.color = (0,0,100)
        self.image.fill(self.color)
        self.duration = 10
    
    @property
    def name(self):
        return "Grow"
        
    def activate(self, ball):
        super().activate(ball)
        player = ball.get_player()
        player.change_size(h=player.height * 2)
        if player.player_number:
            pygame.time.set_timer(DEACTIVATE_GROW_P2, self.duration * 1000, 1)
        else:
            pygame.time.set_timer(DEACTIVATE_GROW_P1, self.duration * 1000, 1)

class MultiballItem(Item):
    def __init__(self, *groups, coords):
        super().__init__(*groups, coords=coords)
        self.color = (100,100,0)
        self.image.fill(self.color)
        
    @property
    def name(self):
        return "Multiball"
    
    def activate(self, ball):
        super().activate(ball)
        multi_spawner.add(Ball(velx=ball.velx, vely=ball.vely + random.randint(50,100), x=ball.rect.centerx, y=ball.rect.centery, is_multiball=True))

# UI classes
class Score:
    def __init__(self, x:int, y:int):
        self.posx = x
        self.posy = y
        self.score = 0
        self.text_surface = default_font.render(str(self.score), False, (255,255,255))
        
    def display(self):
        self.text_surface = default_font.render(str(self.score), False, (255,255,255))
        screen.blit(self.text_surface, (self.posx,self.posy))
    
class Scoreboard:
    def __init__(self, paddingx:int, paddingy:int):
        self.paddingx = paddingx
        self.paddingy = paddingy
        self.scores = [Score(paddingx, paddingy), Score(screen.get_size()[0]-paddingx-32, paddingy)]
    
    def display(self):
        for score in self.scores:
            score.display()

class ItemAnnouncer:
    def __init__(self):
        self.posx = screen.get_size()[0] // 2
        self.posy = 75
        self.display_seconds = 1
        self.text_surface = default_font.render('', False, (255,255,255))
        self.rect = self.text_surface.get_rect(midtop = (self.posx,self.posy))
        
    def announce(self, item_name:str, player_number:int):
        self.text_surface = default_font.render(f'Player {player_number} got a {item_name} !', False, (255,255,255))
        self.rect = self.text_surface.get_rect(midtop = (self.posx,self.posy))
        pygame.time.set_timer(ANNOUNCEMENT_TIMER, self.display_seconds * 1000, 1)
    
    def display(self):
        screen.blit(self.text_surface, self.rect)
    
    def turn_off(self):
        self.text_surface = default_font.render('', False, (255,255,255))

# helper functions

            
# initialize sprites        
ball_spawner = BallSpawner(Ball())
multi_spawner = MultiballSpawner()
players = pygame.sprite.Group([Player(player_number=i) for i in range(2)])
item_spawner = ItemSpawner()
item_spawner.set_spawn_timer()

# initialize UI
scoreboard = Scoreboard(50,20)
item_announcer = ItemAnnouncer()

while is_running:
    # event checks
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        # scorekeeping
        if event.type == INCREMENT_P1:
            scoreboard.scores[0].score += 1
        if event.type == INCREMENT_P2:
            scoreboard.scores[1].score += 1
        
        # item events
        if event.type == SPAWN_ITEM:
            item_spawner.spawn_item()
        if event.type == DEACTIVATE_GROW_P1:
            players.sprites()[0].change_size()
        if event.type == DEACTIVATE_GROW_P2:
            players.sprites()[1].change_size()
        if event.type == ANNOUNCEMENT_TIMER:
            item_announcer.turn_off()
    
    # update players
    players.update()
    if ball_spawner.sprite:
        ball_spawner.update()
    else:
        ball_spawner.respawn_ball()
    multi_spawner.update()
    
    # update items
    if ball_spawner.sprite and item_spawner.sprites():
        collected_items = pygame.sprite.spritecollide(ball_spawner.sprite, item_spawner, True)
        for item in collected_items:
            item.activate(ball_spawner.sprite)
    if multi_spawner.sprites() and item_spawner.sprites():
        collected = pygame.sprite.groupcollide(multi_spawner, item_spawner, False, True)
        for ball, items in collected.items():
            for item in items:
                item.activate(ball)
                
    
    # draw bg
    screen.fill((0,0,40))
    
    # draw sprites
    ball_spawner.draw(screen)
    multi_spawner.draw(screen)
    item_spawner.draw(screen)
    players.draw(screen)
    
    # draw UI
    scoreboard.display()
    item_announcer.display()
    
    # flip screen
    pygame.display.flip()
    
    
    dt = clock.tick(framerate) / 1000

pygame.quit()