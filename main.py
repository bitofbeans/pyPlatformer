# imports
import pygame
from pygame.locals import *

# initialize and set clock
pygame.init()
clock = pygame.time.Clock()
fps = 60

# global constants
hideUnknownTiles = True # when true, it hides the tiles that it can not recognize
screenWidth = 1000
screenHeight = 1000
playerWidth = 20
playerHeight = 50
gravity = 0.8
fallMax = 15
jumpPower = -10
moveSpeed = 1.5
friction = 0.8

BLACK = (0,0,0)
WHITE = (255,255,255)

# game variables
tile_size = 50

# create game window
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Platformer')

# image imports
sun_img = pygame.image.load('img/sun.png')
sun_img = pygame.transform.scale(sun_img, (125, 125))
bg_img = pygame.image.load('img/sky.png')
# bg_img = pygame.transform.scale(bg_img, (screenWidth, screenWidth))

# --- PLAYER SPRITE
class Player():
    def __init__(self,x,y):
        # load animation frames
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1,6):
            print(f'img/guy{num}.png')
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right,(tile_size,tile_size))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        # create player hitbox
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.collideRect =  pygame.rect.Rect((x, y), (playerWidth, playerHeight))
        self.collideRect.midbottom = self.rect.midbottom
        # set variables
        self.rect.x = x
        self.rect.y = y
        self.c_width = playerWidth
        self.c_height = playerHeight
        self.velX = 0
        self.velY = 0
        self.jumped = 0
        self.direction = 0
        self.airtime = 0
        
    def update(self):
        # set delta x/y
        dx = 0
        dy = 0
        walk_cool = 4
        
        # get keys
        key = pygame.key.get_pressed()
        
        # move player if keys pressed
        if key[pygame.K_UP] and self.jumped == 0:
            self.jumped = 1
        elif key[pygame.K_UP]: self.jumped += 1
        if key[pygame.K_UP] and 1 <= self.jumped <= 6 and self.airtime < 6:
            self.velY = jumpPower
        elif key[pygame.K_UP] == False: self.jumped = 0
        
        if key[pygame.K_LEFT]:
            self.velX -= moveSpeed
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            self.velX += moveSpeed
            self.counter += 1
            self.direction = 1
        if (key[pygame.K_RIGHT]-key[pygame.K_LEFT]) == 0 or self.airtime != 0:
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]
            
        self.velX *= friction
        dx += int(self.velX)
        
        # handle animation
        if self.counter > walk_cool:
            self.counter = 0
            self.index = ((self.index) % 4)+1
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]
        
        # gravity
        self.velY += gravity
        if self.velY > fallMax: self.velY = fallMax
        dy += self.velY
        
        # check for collision
        self.airtime += 1
        for tile in world.tile_list:
            # check for collision in x direction
            if tile[1].colliderect(self.collideRect.x + dx, self.collideRect.y, self.c_width, self.c_height):
                if self.velX >= 0:
                    dx = tile[1].left - self.collideRect.right
                # check if below the ground/ if jumping
                elif self.velX < 0:
                    dx = tile[1].right - self.collideRect.left
            # check for collision in y direction
            if tile[1].colliderect(self.collideRect.x, self.collideRect.y + dy, self.c_width, self.c_height):
                # check if above the ground/ if falling
                if self.velY >= 0:
                    dy = tile[1].top - self.collideRect.bottom
                # check if below the ground/ if jumping
                elif self.velY < 0:
                    dy = tile[1].bottom - self.collideRect.top
                self.velY = 0
                self.airtime = 0
        
        # update player position
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.bottom > screenHeight:
          self.rect.bottom = screenHeight
    
        # position hitbox
        self.collideRect.midbottom = self.rect.midbottom
          
        # render player
        screen.blit(self.image, self.rect)
        
        # RENDER HITBOX
        # pygame.draw.rect(screen,(255,0,0),self.collideRect,2)


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
                  else: 
                      img = pygame.transform.scale(err,(tile_size,tile_size))
                      global hideUnknownTiles
                      if hideUnknownTiles == True:
                        col_count += 1
                        continue

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
           
           # RENDER HITBOX
           # pygame.draw.rect(screen,WHITE,tile[1],2)

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