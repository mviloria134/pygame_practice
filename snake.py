from enum import Enum
import random
import pygame

# game initilization
grid_size = 20
grid_max_x = 60
grid_max_y = 50
screen = pygame.display.set_mode((grid_max_x*grid_size, grid_max_y*grid_size))

# colors
WHITE = (255,255,255)

# fonts
pygame.font.init()
font = pygame.font.SysFont("MultiType Pixel", grid_size) 
font_bigger = pygame.font.SysFont('MultiType Pixel', grid_size*3)

# events
SPAWN_APPLE = pygame.USEREVENT + 1
GAME_OVER = pygame.USEREVENT + 2

# util funcs
def is_not_in_bounds(sprite):
    return sprite.rect.left < 0 or sprite.rect.right > grid_max_x*grid_size or sprite.rect.top < 0 or sprite.rect.bottom > grid_max_y*grid_size

# classes
class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

class Snake(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.size = grid_size
        
        self.direction = Direction.RIGHT
        
        self.image = pygame.image.load('item-sprite.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size,self.size))
        
        self.rect = self.image.get_rect(x=grid_max_x//2 * grid_size, y=grid_max_x//2 * grid_size)
        
        self.snake_body = [[self.rect.x,self.rect.y]]

    def keyboard_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w] and self.direction != Direction.DOWN:
            self.direction = Direction.UP
        elif keys[pygame.K_s] and self.direction != Direction.UP:
            self.direction = Direction.DOWN
        elif keys[pygame.K_a] and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
        elif keys[pygame.K_d] and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT
    
    def move(self):
        match self.direction:
            case Direction.UP:
                self.rect.y -= grid_size
            case Direction.DOWN:
                self.rect.y += grid_size
            case Direction.LEFT:
                self.rect.x -= grid_size
            case Direction.RIGHT:
                self.rect.x += grid_size

        # check if in bounds
        if is_not_in_bounds(self):
            pygame.event.post(pygame.event.Event(GAME_OVER))
        
        self.snake_body.insert(0, [self.rect.x, self.rect.y])
        
        if pygame.sprite.spritecollide(self, apple_group, True):
            pygame.event.post(pygame.event.Event(SPAWN_APPLE))
        else:
            self.snake_body.pop()
            
    def collide_with_self(self):
        if len(self.snake_body) > 0:
            for part in self.snake_body[1:]:
                if self.rect.x == part[0] and self.rect.y == part[1]:
                    pygame.event.post(pygame.event.Event(GAME_OVER))
        
    def display(self):
        for part in self.snake_body:
            screen.blit(self.image, part)
            
    def update(self):
        self.keyboard_input()
        self.move()
        self.collide_with_self()

class Apple(pygame.sprite.Sprite):
    score = 10
    def __init__(self, *groups):
        super().__init__(*groups)
        self.size = grid_size
        
        self.image = pygame.image.load('enemy-sprite.png')
        self.image = pygame.transform.scale(self.image, (self.size,self.size))
        self.rect = self.image.get_rect(topleft=(random.randint(0,grid_max_x-1)*grid_size, random.randint(0,grid_max_y-1)*grid_size))

# UI classes
class Scoreboard:
    def __init__(self):
        self.score = 0
        self.text = f"Score: {self.score}"
        self.text_render = font.render(self.text, False, (255,255,255))
        self.rect = self.text_render.get_rect(topleft=(0,0))
    
    def display(self):
        # self.rect.x += 100 * dt
        # if is_not_in_bounds(self):
        #     self.rect.topleft = (0,0)
        self.text = f"Score: {self.score}"
        self.text_render = font.render(self.text, False, (255,255,255))
        screen.blit(self.text_render, self.rect)

class GameOverScreen:
    def __init__(self):
        self.game_over_text = font_bigger.render('GAME OVER', False, WHITE)
        self.update_final_score()
        
        self.game_over_rect = self.game_over_text.get_rect(midtop=(grid_size*grid_max_x//2, grid_size*grid_max_y//4))
        self.score_rect = self.score_text.get_rect(midtop=(grid_size*grid_max_x//2, self.game_over_rect.bottom))
        
    def update_final_score(self):
        self.score_text = font_bigger.render(f'Score: {scoreboard.score}', False, WHITE)
    
    def display(self):
        screen.blit(self.game_over_text, self.game_over_rect)
        screen.blit(self.score_text, self.score_rect)

# initialize entities
snake = Snake()
snake_group = pygame.sprite.GroupSingle(snake)
apple_group = pygame.sprite.Group(Apple(), Apple())

scoreboard = Scoreboard()
game_over_screen = GameOverScreen()

is_running = True
clock = pygame.time.Clock()
framerate = 20
dt = clock.tick(framerate) / 1000

# game states
class GameState(Enum):
    IN_GAME = 1
    GAME_OVER = 2
game_state = GameState.IN_GAME

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == SPAWN_APPLE:
            apple_group.add(Apple())
            scoreboard.score += Apple.score
        if event.type == GAME_OVER:
            game_state = GameState.GAME_OVER
            game_over_screen.update_final_score()
    
    if game_state is GameState.IN_GAME:
        # update
        snake.update()
        
        # draw
        screen.fill((0,0,50))
        apple_group.draw(screen)
        snake.display()
        scoreboard.display()
        
    elif game_state is GameState.GAME_OVER:
        screen.fill((50,0,0))
        game_over_screen.display()
    
    # update display
    pygame.display.flip()
    
    dt = clock.tick(framerate) / 1000
            
pygame.quit()