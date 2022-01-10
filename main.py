# imports
import pygame
from pygame.locals import *

# initialize and set clock
pygame.init()
clock = pygame.time.Clock()
fps = 60

# global constants
screenWidth = 1000
screenHeight = 1000
BLACK = (0,0,0)
WHITE = (255,255,255)

# game variables
tile_size = 50

# create game window
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Platformer')

# image imports
sun_img = pygame.image.load('img/sun.png')
sun_img = pygame.transform.scale(sun_img, (75, 75))
bg_img = pygame.image.load('img/sky.png')
bg_img = pygame.transform.scale(bg_img, (screenWidth, screenWidth))

# --- PLAYER SPRITE
class Player():
    def __init__(self,x,y):
        # load player image, scale it, get dimensions
        self.images_right = []
        self.index = 0
        self.counter = 0
        img = pygame.image.load('img/guy.png')
        self.image = pygame.transform.scale(img,(tile_size,tile_size))
        self.rect = self.image.get_rect()
        
        # set pos to x and y
        self.rect.x = x
        self.rect.y = y
        self.velY = 0
        self.jumped = False
        
        
    def update(self):
        
        # set delta x/y
        dx = 0
        dy = 0
        
        # get keys
        key = pygame.key.get_pressed()
         
        # move player if keys pressed
        if key[pygame.K_UP] and self.jumped == False:
            self.velY = -15
            self.jumped = True
        elif key[pygame.K_UP] == False: self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 5  
        elif key[pygame.K_RIGHT]:
            dx += 5
        
        # gravity
        self.velY += 1
        if self.velY > 10: self.velY = 10
        dy += self.velY
        
        # check for collision
        
        # update player position
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.bottom > screenHeight:
          self.rect.bottom = screenHeight
        
        
        # load player image
        img = pygame.image.load('img/guy.png')
        
        # scale player
        self.image = pygame.transform.scale(img,(tile_size,tile_size))
        
        # render player
        screen.blit(self.image, self.rect)


# --- WORLD SPRITE
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
        # for every tile,
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

# --- create sprites
player = Player(100, screenHeight - tile_size*2)
world = World(world_data)


# --- game loop
run = True
while run:
    # --- tick fps
    clock.tick(fps)
    
    # escape condition
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
    
    # --- game logic
     #render bg
    screen.blit(bg_img,(0,0))
    screen.blit(sun_img,(100,100))
     #draw tiles
    world.draw()
     #player movement and rendering
    player.update()
    
    # --- update display
    pygame.display.update()
    

 
# end   
pygame.quit()