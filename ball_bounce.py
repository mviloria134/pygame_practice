import pygame

pygame.init()

SCREEN_W = 1200
SCREEN_H = 900
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
is_running = True
clock = pygame.time.Clock()
framerate = 60
dt = clock.tick(framerate) / 1000

# colors
WHITE    = (255,255,255)
BLACK    = (0,0,0)
RED      = (255,0,0)
GREEN    = (0,255,0)
BLUE     = (0,0,255)
YELLOW   = (255,255,0)
CYAN     = (0,255,255)
MAGENTA  = (255,0,255)
PINK     = (255,200,255)

GRAVITY = 20

class Ball:
    def __init__(self, x, y, r, velx, vely, color=WHITE):
        self.x = x
        self.y = y
        self.r = r
        self.velx = velx
        self.vely = vely
        self.color = color
        self.rect = pygame.draw.circle(screen,self.color,(x,y),r)
        
    def move(self):
        if self.rect.bottom >= screen.get_size()[1] or self.rect.top <= 0:
            self.vely = -self.vely
        if self.rect.right >=  screen.get_size()[0] or self.rect.left <= 0:
            self.velx = -self.velx
        self.vely += GRAVITY
        self.x += self.velx * dt
        self.y += self.vely * dt
    
    def draw(self):
        self.rect = pygame.draw.circle(screen,self.color,(self.x,self.y),self.r)

class Player:
    def __init__(self, x, y, r, move_speed, color=BLUE):
        self.x = x
        self.y = y
        self.r = r
        self.move_speed = move_speed
        self.color = color
        
        self.rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)
        
    def move(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.y -= self.move_speed * dt
        if keys[pygame.K_s]:
            self.y += self.move_speed * dt
        if keys[pygame.K_a]:
            self.x -= self.move_speed * dt
        if keys[pygame.K_d]:
            self.x += self.move_speed * dt
            
    def draw(self):
        self.rect = pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)

ball = Ball(600, 450, 20, 520, -520)
ball2 = Ball(200, 400, 10, 900, 1000, RED)
player = Player(400, 200, 50, 600)

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
    
    screen.fill(PINK)
    
    # update
    ball.move()
    ball2.move()
    player.move()
    
    # draw
    ball.draw()
    ball2.draw()
    player.draw()
    
    pygame.display.update()
    
    dt = clock.tick(framerate) / 1000


pygame.quit()