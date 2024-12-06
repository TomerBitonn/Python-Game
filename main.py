import pygame
from pygame import mixer
import csv
import constants
from weapon import Weapon
from items import Item
from world import World
from button import Button

# initialize Pygame
pygame.init()

# initialize mixer
mixer.init()


screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")  # Game Name


# create clock for maintaining frame rate
clock = pygame.time.Clock()


# define game variables
level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

# define player movement variable
moving_left = False
moving_right = False
moving_up = False
moving_down = False


# helper function to scale image
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))


# load music and sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

# load button images
restart_img = scale_img(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)
start_img = scale_img(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)

# load heart images
heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
full_heart = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)
half_heart = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)

# load coin images
coin_images = []
for i in range(4):
    img = scale_img(pygame.image.load(f"assets/images/items/coin_f{i}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

# load potion image
red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = list()
item_images.append(coin_images)
item_images.append(red_potion)

# load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

# load tile map images
tile_list = list()
for t in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{t}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)

# load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
    # load images
    animation_list = []
    for animation in animation_types:
        # reset temporary list of images
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)


# function for outputting text onto the screen
def draw_text(text, font, text_col, d_x, d_y):
    text_img = font.render(text, True, text_col)
    screen.blit(text_img, (d_x, d_y))


# function for display game info
def draw_info():

    font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))
    # draw lives
    half_heart_flag = False
    for j in range(5):
        if player.health >= ((j + 1) * 20):
            screen.blit(full_heart, (10 + j * 50, 0))
        elif (player.health % 20 > 0) and not half_heart_flag:
            screen.blit(half_heart, (10 + j * 50, 0))
            half_heart_flag = True
        else:
            screen.blit(heart_empty, (10 + j * 50, 0))

    # level
    draw_text("LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)

    # show score
    draw_text(f"x{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)


# function to reset level
def reset_level():
    arrow_group.empty()
    damage_text_group.empty()
    item_group.empty()
    fireball_group.empty()

    # create empty tile list
    data = []
    for t_r in range(constants.ROWS):
        tile_row = [-1] * constants.COLS
        data.append(tile_row)

    return data


# damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, t_x, t_y, t_damage, color):
        pygame.sprite.Sprite.__init__(self)

        font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

        self.image = font.render(t_damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (t_x, t_y)
        self.counter = 0

    def update(self):
        # reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # move damage text up
        self.rect.y -= 2
        # delete counter
        self.counter += 1
        if self.counter > 40:
            self.kill()


# class for handling screen fade
class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (constants.SCREEN_WIDTH // 2 + self.fade_counter,
                                                   0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter,
                                                   constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
        elif self.direction == 2:  # vertical screen fade
            pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))

        if self.fade_counter >= constants.SCREEN_WIDTH:
            fade_complete = True
        return fade_complete


# create empty tile list
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)

# load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)

# create player
player = world.player

# create player's weapon
bow = Weapon(bow_image, arrow_image)

# extract enemies from world data
enemy_list = world.character_list

# create sprite groups
arrow_group = pygame.sprite.Group()
damage_text_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 25, 0, coin_images, True)
item_group.add(score_coin)

# add the items from the level data
for item in world.item_list:
    item_group.add(item)

# create screen fade
intro_fade = ScreenFade(1, constants.BLACK, constants.FADE_SPEED)
death_screen = ScreenFade(2, constants.MENU_BG, constants.FADE_SPEED)

# create button
start_button = Button(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2 - 150, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2 + 150, exit_img)
restart_button = Button(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2 - 150, restart_img)
resume_button = Button(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2, resume_img)

# MAIN GAME LOOP
run = True
while run:

    # control frame rate
    clock.tick(constants.FPS)

    if not start_game:
        screen.fill(constants.MENU_BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        if pause_game:
            screen.fill(constants.MENU_BG)
            if resume_button.draw(screen):
                pause_game = False
            if exit_button.draw(screen):
                run = False
            # if restart_button.draw(screen):
                # continue later

        else:
            # background color
            screen.fill(constants.BG)

            # happens only if the player alive
            if player.alive:
                # calculate player movement and character speed
                dx = 0
                dy = 0
                if moving_right:
                    dx = constants.SPEED
                if moving_left:
                    dx = -constants.SPEED
                if moving_up:
                    dy = -constants.SPEED
                if moving_down:
                    dy = constants.SPEED

                # Move player
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

                # Update all objects
                world.update(screen_scroll)
                for enemy in enemy_list:
                    fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)
                    if enemy.alive:
                        enemy.update()
                player.update()
                arrow = bow.update(player)
                if arrow:
                    arrow_group.add(arrow)
                    shot_fx.play()
                for arrow in arrow_group:
                    damage, damage_pos = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
                    if damage:  # contact between the arrow and the enemy
                        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
                        damage_text_group.add(damage_text)
                        hit_fx.play()

            damage_text_group.update()
            fireball_group.update(screen_scroll, player)
            item_group.update(screen_scroll, player, coin_fx, heal_fx)

            # Draw player on screen
            world.draw(screen)

            for enemy in enemy_list:
                enemy.draw(screen)
            player.draw(screen)
            bow.draw(screen)
            for arrow in arrow_group:
                arrow.draw(screen)
            for fireball in fireball_group:
                fireball.draw(screen)
            damage_text_group.draw(screen)
            item_group.draw(screen)
            draw_info()
            score_coin.draw(screen)

            # check level complete
            if level_complete:
                start_intro = 1
                level += 1
                if level == constants.MAX_LEVEL:  # make a screen for the end of the game
                    run = False
                else:
                    world_data = reset_level()
                    # load in level data and create world
                    if level <= constants.MAX_LEVEL:
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                # create player and items
                world = World()
                world.process_data(world_data, tile_list, item_images, mob_animations)
                temp_hp = player.health
                temp_score = player.score
                player = world.player
                player.health = temp_hp
                player.score = temp_score
                enemy_list = world.character_list
                score_coin = Item(constants.SCREEN_WIDTH - 115, 25, 0, coin_images, True)
                item_group.add(score_coin)
                # add the items from the level data
                for item in world.item_list:
                    item_group.add(item)

            # show intro
            if start_intro:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            # show death screen
            if not player.alive:
                if death_screen.fade():
                    if exit_button.draw(screen):
                        run = False
                    if restart_button.draw(screen):
                        death_screen.fade_counter = 0
                        start_intro = True
                        world_data = reset_level()
                        # load in level data and create world
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        # create player and items
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        # player score stays the same after death
                        temp_score = player.score
                        player = world.player  # create the player
                        player.score = temp_score
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 115, 25, 0, coin_images, True)
                        item_group.add(score_coin)
                        # add the items from the level data
                        for item in world.item_list:
                            item_group.add(item)

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # take keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_ESCAPE:
                pause_game = True

        # keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    # keep player within window boundaries - OPTIONAL
    # player.boundaries()

    # update the display screen
    pygame.display.update()

# Quit Pygame
pygame.quit()
