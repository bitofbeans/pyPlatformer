# imports
import pygame
from pygame.locals import *

# initialize
pygame.init()

# global constants
screenWidth = 1000
screenHeight = 1000
BLACK = (0,0,0)
WHITE = (255,255,255)

# create window
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Platformer')

# game variables
tile_size = 50

# image imports
sun_img = pygame.image.load('img/sun.png')
sun_img = pygame.transform.scale(sun_img, (75, 75))
bg_img = pygame.image.load('img/sky.png')

# draw grid for entire map
def drawGrid():
  for line in range(0,int((screenWidth/tile_size)+1)):
      lineLen = line * tile_size
      pygame.draw.line(screen,WHITE,(0, lineLen), (screenWidth, lineLen))
      pygame.draw.line(screen,WHITE,(lineLen, 0), (lineLen, screenHeight))
      

# define world
class World():
    def __init__(self,data):
      # clear list
      self.tile_list = []
      
      # load images
      dirt_img = pygame.image.load('img/dirt.png')
      grass_img = pygame.image.load('img/grass.png')
      err = pygame.image.load('img/unknown.png')
      
      # extract tiles from data
      row_count = 0
      for row in data:
          col_count = 0
          for tile in row:
              if tile != 0:
                  if tile == 1:
                      img = pygame.transform.scale(dirt_img,(tile_size,tile_size))
                  elif tile == 2:
                      img = pygame.transform.scale(grass_img,(tile_size,tile_size))
                  else: img = pygame.transform.scale(err,(tile_size,tile_size))

                  img_rect = img.get_rect()
                  img_rect.x = col_count * tile_size
                  img_rect.y = row_count * tile_size
                  tile = (img,img_rect)
                  self.tile_list.append(tile)
              col_count += 1
          row_count += 1
        
    def draw(self):
        for tile in self.tile_list:
           # draw each tile
           screen.blit(tile[0],tile[1])

# set world data
world_data =[
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
# create world sprite from data
world = World(world_data)

# --- game loop
run = True
while run:
    
    # escape condition
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
    
    # --- render
    screen.blit(bg_img,(0,0))
    screen.blit(sun_img,(100,100))
    world.draw()
    drawGrid()
    
    # update display
    pygame.display.update()
    
    
      
    
    
    
    
pygame.quit()