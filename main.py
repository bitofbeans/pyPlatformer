# imports
import pygame
from pygame.locals import *

# initialize
pygame.init()

# create window
screenWidth = 1000
screenHeight = 1000
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Platformer')

run = True

while run:
    # escape condition
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
    
pygame.quit()