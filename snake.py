from collections.abc import Callable
from enum import Enum
import random
import pygame

# game initilization
grid_size = 25
grid_max_x = 50
grid_max_y = 50
play_area_padding_squares = 2
SCREEN_W = (grid_max_x + play_area_padding_squares * 2) * grid_size
SCREEN_H = (grid_max_y + play_area_padding_squares * 2) * grid_size
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

is_running = True
clock = pygame.time.Clock()
framerate = 20
dt = clock.tick(framerate) / 1000

# colors
WHITE = (255, 255, 255)
DARK_BLUE = (30, 30, 50)
GREY = (100, 100, 100)
RED = (100, 50, 50)
GRID_LIGHT = (180, 230, 250)
GRID_DARK = (150, 200, 220)
BRIGHT_GREEN = (100,200,100)

# fonts
pygame.font.init()
font = pygame.font.SysFont("MultiType Pixel", grid_size)
font_bigger = pygame.font.SysFont("MultiType Pixel", grid_size * 3)

# events
START_GAME = pygame.event.custom_type()
GAME_OVER = pygame.event.custom_type()
SPAWN_APPLE = pygame.event.custom_type()
SPAWN_WALL = pygame.event.custom_type()

# classes
# enums
class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

class PlayArea:
    def __init__(self):
        self.color = GRID_LIGHT
        self.alt_color = GRID_DARK
        self.grid_square_image = pygame.Surface((grid_size, grid_size))
        self.grid_square_image.fill(self.alt_color)
        self.surf = pygame.Surface((grid_size * grid_max_x, grid_size * grid_max_y))
        self.surf.fill(self.color)
        self.rect = self.surf.get_rect(
            topleft=(
                play_area_padding_squares * grid_size,
                play_area_padding_squares * grid_size,
            )
        )

    def is_in_bounds(self, sprite):
        return self.rect.contains(sprite.rect)

    def generate_random_coords(self, exclude_rect: pygame.Rect = None):
        while True:
            generated_coords = (
                (random.randint(0, grid_max_x - 1) + play_area_padding_squares)
                * grid_size,
                (random.randint(0, grid_max_y - 1) + play_area_padding_squares)
                * grid_size,
            )
            if exclude_rect is None or (not exclude_rect.collidepoint(generated_coords)):
                return generated_coords

    def display(self):
        screen.blit(self.surf, self.rect)
        for column in range(grid_max_x):
            for row in range(grid_max_y):
                if column%2 ^ row%2:
                    screen.blit(self.grid_square_image, ((column+play_area_padding_squares)*grid_size, (row+play_area_padding_squares)*grid_size))


# game entities
class Snake(pygame.sprite.Sprite):
    no_spawn_grid_square_radius = 10

    def __init__(self, *groups):
        super().__init__(*groups)
        self.size = grid_size

        self.direction = Direction.RIGHT

        self.snake_body_image = pygame.Surface((grid_size,grid_size))
        self.snake_body_image.fill(BRIGHT_GREEN)
        self.snake_head_image = pygame.image.load("item-sprite.png").convert_alpha()
        self.snake_head_image = pygame.transform.scale(self.snake_head_image, (self.size, self.size))
        self.image = pygame.transform.rotate(self.snake_head_image, -90)

        self.rect = self.image.get_rect(
            x=grid_max_x // 2 * grid_size, y=grid_max_x // 2 * grid_size
        )

        self.no_spawn_rect = pygame.Rect(
            0,
            0,
            self.no_spawn_grid_square_radius * grid_size * 2,
            self.no_spawn_grid_square_radius * grid_size * 2,
        )
        self.no_spawn_rect.center = self.rect.center

        self.snake_body = [[self.rect.x, self.rect.y]]
        self.crashed = False

    def handle_keyboard_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and self.direction != Direction.DOWN:
            self.direction = Direction.UP
            self.image = pygame.transform.rotate(self.snake_head_image, 0)
        elif keys[pygame.K_s] and self.direction != Direction.UP:
            self.direction = Direction.DOWN
            self.image = pygame.transform.rotate(self.snake_head_image, 180)
        elif keys[pygame.K_a] and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
            self.image = pygame.transform.rotate(self.snake_head_image, 90)
        elif keys[pygame.K_d] and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT
            self.image = pygame.transform.rotate(self.snake_head_image, -90)

    def change_direction(self):
        match self.direction:
            case Direction.UP:
                self.rect.y -= grid_size
            case Direction.DOWN:
                self.rect.y += grid_size
            case Direction.LEFT:
                self.rect.x -= grid_size
            case Direction.RIGHT:
                self.rect.x += grid_size

    def check_if_in_bounds(self):
        if not play_area.is_in_bounds(self):
            self.crashed = True
            pygame.event.post(pygame.event.Event(GAME_OVER))

    def did_collect_apple(self):
        return pygame.sprite.spritecollide(self, apple_group, True)

    def update_body(self):
        if self.crashed:
            return
        if self.did_collect_apple():
            pygame.event.post(pygame.event.Event(SPAWN_APPLE))
        else:
            self.snake_body.pop()
        self.snake_body.insert(0, [self.rect.x, self.rect.y])

    def collide_with_self(self):
        if len(self.snake_body) > 0:
            for part in self.snake_body[1:]:
                if self.rect.x == part[0] and self.rect.y == part[1]:
                    pygame.event.post(pygame.event.Event(GAME_OVER))

    def visualize_no_spawn(self):
        pygame.draw.rect(screen, (50, 0, 0), self.no_spawn_rect)

    def move(self):
        self.handle_keyboard_input()
        self.change_direction()
        self.check_if_in_bounds()
        self.update_body()
        self.collide_with_self()
        self.no_spawn_rect.center = self.rect.center

    def display(self):
        # self.visualize_no_spawn()
        screen.blit(self.image, self.snake_body[0])
        for part in self.snake_body[1:]:
            screen.blit(self.snake_body_image, part)

    def update(self):
        self.move()


class Apple(pygame.sprite.Sprite):
    score = 10

    def __init__(self, *groups):
        super().__init__(*groups)
        self.size = grid_size

        self.image = pygame.image.load("enemy-sprite.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

        while True:
            self.rect = self.image.get_rect(topleft=play_area.generate_random_coords())
            if not pygame.sprite.spritecollideany(self, wall_group):
                break


class Wall(pygame.sprite.Sprite):
    size = grid_size * 2
    color = GREY

    image = pygame.Surface((size, size))
    image.fill(color)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = self.image.get_rect(
            topleft=play_area.generate_random_coords(snake_group.sprite.no_spawn_rect)
        )
        while True:
            if (
                pygame.sprite.spritecollideany(self, apple_group)
                or self.rect.right > screen.get_size()[0]
                or self.rect.bottom > screen.get_size()[1]
            ):
                self.rect.topleft = play_area.generate_random_coords(
                    snake_group.sprite.no_spawn_rect
                )
            else:
                break

    def collide_with_snake(self):
        snake = snake_group.sprite

        if self.rect.colliderect(snake.rect):
            pygame.event.post(pygame.event.Event(GAME_OVER))

    def update(self):
        self.collide_with_snake()


# UI classes
class Scoreboard:
    def __init__(self):
        self.reset()
        self.rect = self.text_render.get_rect(topleft=(0, 0))

    def update_score_text(self):
        self.text = f"Score: {self.score}"
        self.text_render = font.render(self.text, False, (255, 255, 255))

    def add_score(self, amount):
        self.score += amount
        self.update_score_text()

    def reset(self):
        self.score = 0
        self.update_score_text()

    def display(self):
        screen.blit(self.text_render, self.rect)


class ClickableButton(pygame.sprite.Sprite):
    def __init__(
        self,
        *groups,
        text: str = "",
        posx=1 * grid_size,
        posy=1 * grid_size,
        click_behavior: Callable = None,
    ):
        super().__init__(*groups)
        self.inactive_color = (0, 50, 0)
        self.active_color = (0, 255, 0)
        self.on_click = click_behavior
        self.text = text

        self.image = font_bigger.render(self.text, False, WHITE, self.inactive_color)
        if not text:
            self.image = pygame.transform.scale(
                self.image, (5 * grid_size, 3 * grid_size)
            )
        self.rect = self.image.get_rect(x=posx, y=posy)

    def is_active(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def hover_over(self):
        if self.is_active():
            self.image = font_bigger.render(self.text, False, WHITE, self.active_color)
        else:
            self.image = font_bigger.render(
                self.text, False, WHITE, self.inactive_color
            )

    def click(self):
        if self.is_active():
            self.on_click()

    def update(self):
        self.hover_over()


class ClickableButtonContainer(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

    def has_active_button(self):
        for button in self.sprites():
            if button.is_active():
                return True
        return False

    def hover(self):
        if self.has_active_button():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def update(self):
        super().update()
        self.hover()


class GameOverScreen:
    def __init__(self):
        self.game_over_text = font_bigger.render("GAME OVER", False, WHITE)
        self.game_over_rect = self.game_over_text.get_rect(
            midtop=(SCREEN_W // 2, SCREEN_H // 4)
        )
        self.update_final_score()

        distance_from_buttons = 3 * grid_size
        distance_between_buttons = 1 * grid_size

        self.retry_button = ClickableButton(
            text="Try Again?",
            click_behavior=lambda: pygame.event.post(pygame.event.Event(START_GAME)),
        )
        self.retry_button.rect.midtop = (
            self.score_rect.centerx,
            self.score_rect.bottom + distance_from_buttons,
        )

        self.quit_button = ClickableButton(
            text="Quit",
            click_behavior=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
        )
        self.quit_button.rect.midtop = (
            self.retry_button.rect.centerx,
            self.retry_button.rect.bottom + distance_between_buttons,
        )

        self.buttons = ClickableButtonContainer(self.quit_button, self.retry_button)

    def update_final_score(self):
        self.score_text = font_bigger.render(f"Score: {scoreboard.score}", False, WHITE)
        self.score_rect = self.score_text.get_rect(
            midtop=(self.game_over_rect.centerx, self.game_over_rect.bottom)
        )

    def display(self):
        self.buttons.update()
        screen.blit(self.game_over_text, self.game_over_rect)
        screen.blit(self.score_text, self.score_rect)
        self.buttons.draw(screen)


# initialize entities
play_area = PlayArea()

snake_group = pygame.sprite.GroupSingle()
apple_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()

scoreboard = Scoreboard()
game_over_screen = GameOverScreen()




# game states
class GameState(Enum):
    IN_GAME = 1
    GAME_OVER = 2


game_state = GameState.IN_GAME


def start_game():
    snake_group.empty()
    snake_group.add(Snake())

    apple_group.empty()
    apple_group.add(Apple(), Apple())

    wall_group.empty()
    wall_group.add(Wall(), Wall())
    pygame.time.set_timer(SPAWN_WALL, 5000)

    scoreboard.reset()


start_game()
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # user input events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state is GameState.GAME_OVER:
                for button in game_over_screen.buttons.sprites():
                    button.click()

        # game state switch events
        if event.type == START_GAME:
            game_state = GameState.IN_GAME
            start_game()
        if event.type == GAME_OVER:
            game_state = GameState.GAME_OVER
            game_over_screen.update_final_score()

        # in game events
        if event.type == SPAWN_APPLE:
            apple_group.add(Apple())
            scoreboard.add_score(Apple.score)

        if event.type == SPAWN_WALL:
            wall_group.add(Wall())

    if game_state is GameState.IN_GAME:
        # update
        snake_group.update()
        wall_group.update()

        # draw
        screen.fill(DARK_BLUE)
        play_area.display()
        snake_group.sprite.display()
        apple_group.draw(screen)
        wall_group.draw(screen)

        scoreboard.display()

    elif game_state is GameState.GAME_OVER:
        screen.fill(RED)
        game_over_screen.display()

    # update display
    pygame.display.flip()

    dt = clock.tick(framerate) / 1000

pygame.quit()
