from character import Character
from items import Item
import constants


class World:
    def __init__(self):
        self.map_tiles = []
        self.obstacle_tiles = []
        self.exit_tile = None
        self.item_list = []
        self.player = None
        self.level_length = None
        self.character_list = []

    def process_data(self, data, tile_list, item_images, mob_animations):
        self.level_length = len(data)
        # iterate trough each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tile_list[tile]
                image_rect = image.get_rect()
                image_x = x * constants.TILE_SIZE
                image_y = y * constants.TILE_SIZE
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]

                # filling the world map with player, enemies, coins, potions, boundaries
                if tile == 7:
                    self.obstacle_tiles.append(tile_data)
                elif tile == 8:
                    self.exit_tile = tile_data
                elif tile == 9:
                    coin = Item(image_x, image_y, 0, item_images[0])
                    self.item_list.append(coin)
                    tile_data[0] = tile_list[0]
                elif tile == 10:
                    potion = Item(image_x, image_y, 1, [item_images[1]])
                    self.item_list.append(potion)
                    tile_data[0] = tile_list[0]
                elif tile == 11:
                    player = Character(image_x, image_y, constants.FULL_HEALTH, mob_animations, 0, False, 0.9)
                    self.player = player
                    tile_data[0] = tile_list[0]
                elif 11 < tile < 17:
                    enemy = Character(image_x, image_y, constants.FULL_HEALTH, mob_animations, tile - 11, False, 0.8)
                    self.character_list.append(enemy)
                    tile_data[0] = tile_list[0]
                elif tile == 17:
                    enemy = Character(image_x, image_y, constants.BOSS_HEALTH, mob_animations, 6, True, 1.8)
                    self.character_list.append(enemy)
                    tile_data[0] = tile_list[0]

                # add image data to main tile list
                if tile >= 0:
                    self.map_tiles.append(tile_data)

    def update(self, screen_scroll):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])

    def draw(self, surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])
