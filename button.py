import pygame


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()  # x  and y coordinates of the mouse

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:  # [0] - left, [1] - center, [2] - right
                action = True

        surface.blit(self.image, self.rect)

        return action
