import pygame
from random import randint
import random
import math

# constants
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

screen = pygame.display.set_mode((800,800))
framerate = 60
clock = pygame.time.Clock()
dt = clock.tick(framerate) / 1000

ball_list = []

# helper functions
def distance_between(coord1:list, coord2:list):
    return math.sqrt( math.pow(coord1[0]-coord2[0],2) + math.pow(coord1[1]-coord2[1],2) )

# classes
class Ball:
    def __init__(self, radius=None, color=WHITE, x=None, y=None, velx = None, vely = None):
        self.radius = randint(5,100) if radius is None else radius
        self.color = color
        if x is None:
            self.x = randint(0,800-2*self.radius)
        else:
            self.x = x
            
        if y is None:
            self.y = randint(0,800-2*self.radius)
        else:
            self.y = y
            
        if velx is None:
            self.velx = random.uniform(-500,500)
        else:
            self.velx = velx
            
        if vely is None:
            self.vely = random.uniform(-500,500)
        else:
            self.vely = vely
            
        self.hitbox = pygame.draw.ellipse(screen, self.color, [self.x, self.y, 2*self.radius, 2*self.radius])
    
    def get_center(self):
        return [self.x + self.radius, self.y + self.radius]
    
    def move(self, other_ball=None):
        self.colliding = False
        self.x += self.velx * dt
        self.y += self.vely * dt
        # check bounds
        if self.x < 0 or self.x > screen.get_size()[0] - self.radius*2:
            if self.velx < 0:
                self.x = 0
            else:
                self.x = 800 - self.radius*2
            self.velx = -self.velx
        if self.y < 0 or self.y > screen.get_size()[1] - self.radius*2:
            if self.vely < 0:
                self.y = 0
            else:
                self.y = 800 - self.radius*2
            self.vely = -self.vely
        
        # update pos
        if other_ball is not None:
            if distance_between(self.get_center(), other_ball.get_center()) <= self.radius + other_ball.radius:
                self.color = RED
                self.vely = -self.vely
                self.velx = -self.velx
                other_ball.vely = -self.vely
                other_ball.velx = -self.velx
                self.x += 5 * self.velx * dt
                self.y += 5 * self.vely * dt
            else:
                self.color = GREEN
        
        
        # draw ellipse at new pos
        # screen.blit(pygame.Surface((2*self.radius, 2*self.radius)), self.hitbox)
        self.hitbox = pygame.draw.ellipse(screen, self.color, [self.x, self.y, 2*self.radius, 2*self.radius])


# variables
# ball = Ball(radius=10, x=400, y=400, velx=.1, vely=1)

ball_list = []

for i in range(10):
    ball_rand = Ball(color=(randint(0,255),randint(0,255),randint(0,255)))
    ball_list.append(ball_rand)
    
ball1 = Ball(radius=10)
# ball2 = Ball()


pygame.init()
pygame.display.set_caption('Test Game zzzz')

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball_list.append(Ball(color=(randint(0,255),randint(0,255),randint(0,255))))
            if event.key == pygame.K_DOWN:
                ball_list.pop()
            if event.key == pygame.K_c:
                ball_list = []
    
    screen.fill(BLACK)
    
    # ball.move()
    ball1.move()
    for b in ball_list:
        b.move(ball1)
    # ball2.move(ball1)
    
    # update
    pygame.display.update()
    
    dt = clock.tick(framerate) / 1000
            
pygame.quit()