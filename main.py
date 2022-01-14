# Import Pygame
import pygame
#from pygame.locals import *

# Initialize pygame and create clock
pygame.init()
clock = pygame.time.Clock()
fps = 60

# Game Variables
tile_size = 50

# Global Constants
hideUnknownTiles = True # When true, it hides the tiles that it can not recognize
screenWidth = 1000
screenHeight = 1000

# Player Variables
playerWidth = tile_size-30
playerHeight = tile_size-15
gravity = 0.8
fallMax = 15
jumpPower = -10
moveSpeed = 1.5
friction = 0.8

# Color Definitions
BLACK = (0,0,0)
WHITE = (255,255,255)

# Create game window
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Platformer')

# Image imports and data
sun_img = pygame.image.load('img/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size*2, tile_size*2))
bg_img = pygame.image.load('img/sky.png')
#bg_img = pygame.transform.scale(bg_img, (950+tile_size*2, 950+tile_size*2 ))

# Import outline image and outline data
outline_img = pygame.image.load('img/tile/outline.png')
pixelRes= outline_img.get_width()
scaler = (tile_size / pixelRes)+0.1
outline_img = pygame.transform.scale(outline_img,((pixelRes+2)*scaler,(pixelRes+2)*scaler))
scaler -=0.2

# --- PLAYER SPRITE
class Player():
         
    def __init__(self,x,y):
        # Create animation variables
        self.images_right = []
        self.images_left = []
        self.frame = 0
        self.counter = 0
        
        # Load animation frames function
        def imgLoad(img):
                img_right = pygame.image.load('img/player/'+ img +'.png')
                img_right = pygame.transform.scale(img_right,(tile_size*0.75,tile_size*0.75))
                img_left = pygame.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
        
        # Load all frames
        imgLoad('idle0')
        imgLoad('idle1')
        imgLoad('run0')
        imgLoad('run1')
        imgLoad('air0')
        imgLoad('air1')
        
        # Create player hitbox
        self.image = self.images_right[self.frame]
        self.rect = self.image.get_rect()
        self.collideRect =  pygame.rect.Rect((x, y), (playerWidth, playerHeight))
        self.collideRect.midbottom = self.rect.midbottom
        
        # Set Position and variables
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
        # Set delta x/y
        dx = 0
        dy = 0
        
        # Get keys pressed
        key = pygame.key.get_pressed()
        
        # --- Move player if keys pressed
         # Y axis
        if key[pygame.K_UP] and self.jumped == 0:
            self.jumped = 1
        elif key[pygame.K_UP]: self.jumped += 1
        if key[pygame.K_UP] and 1 <= self.jumped <= 6 and self.airtime < 6:
            self.velY = jumpPower
        if key[pygame.K_UP] == False: self.jumped = 0
    
        # X axis
        if key[pygame.K_LEFT]:
            self.velX -= moveSpeed
            self.direction = -1
            self.frame += 0.07
        if key[pygame.K_RIGHT]:
            self.velX += moveSpeed
            self.direction = 1
            self.frame += 0.07
        # Change X by velocity
        self.velX *= friction
        dx += int(self.velX)
        
        # Handle animation
             # animation frames
         #### idle = 0,1
         #### run = 2,3
         #### air = 4,5
        self.frame += 0.05
        self.counter = int(self.frame)
        
        if self.airtime > 1:
            if self.velY >= 0:
                if self.direction == 1:
                    self.image = self.images_right[5]
                else:
                    self.image = self.images_left[5]
            else:
                if self.direction == 1:
                    self.image = self.images_right[4]
                else:
                    self.image = self.images_left[4]
        elif (key[pygame.K_RIGHT]-key[pygame.K_LEFT]) != 0:
            if self.direction == 1:
                self.image = self.images_right[(self.counter % 2)+2]
            else:
                self.image = self.images_left[(self.counter % 2)+2]
        else:
            if self.direction == 1:
                self.image = self.images_right[(self.counter % 2)]
            else:
                self.image = self.images_left[(self.counter % 2)]

        # gravity and change y by velocity
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
                elif self.velX < 0:
                    dx = tile[1].right - self.collideRect.left
            # check for collision in y direction
            if tile[1].colliderect(self.collideRect.x, self.collideRect.y + dy, self.c_width, self.c_height):
                # check if above the ground/ if falling
                if self.velY >= 0:
                    dy = tile[1].top - self.collideRect.bottom
                    self.airtime = 0
                # check if below the ground/ if jumping
                elif self.velY < 0:
                    dy = tile[1].bottom - self.collideRect.top

                self.velY = 0
        
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
      self.tileTypes = [1,2,3]
      dirt_img = pygame.image.load('img/tile/dirt.png')
      grass_img = pygame.image.load('img/tile/grass.png')
      err = pygame.image.load('img/tile/unknown.png')
      self.errorImg = err
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
                  elif tile == 3:
                      blob = Enemy(col_count * tile_size, row_count * tile_size)
                      blob_group.add(blob)
                      col_count += 1
                      continue
                  else: 
                      # unknown tile
                      img = pygame.transform.scale(err,(tile_size,tile_size))
                      global hideUnknownTiles
                      if hideUnknownTiles == True:
                        col_count += 1
                        continue

                  img_rect = img.get_rect()
                  img_rect.x = col_count * tile_size
                  img_rect.y = row_count * tile_size
                  tile = (img,img_rect,tile)
                  self.tile_list.append(tile)
              col_count += 1
          row_count += 1
        
    def draw(self):
        for tile in self.tile_list:
            # draw each tiles outline
           tileImg = tile[2]
           if tileImg in self.tileTypes: # if not unknown image, draw outline
                rect = tile[1]
                screen.blit(outline_img,(rect.left-scaler, rect.top-scaler, rect.width, rect.height))
       
       
        for tile in self.tile_list:
            # draw each tile
           screen.blit(tile[0],tile[1])
           
           # RENDER HITBOX
           # pygame.draw.rect(screen,WHITE,tile[1],2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # inherit sprite constructor
        pygame.sprite.Sprite.__init__(self)
        
        # add animation frames
        self.images = []
        for i in range(0,4):
            img = pygame.image.load(f'img/enemy/blob{i}.png')
            img = pygame.transform.scale(img,(tile_size,tile_size))
            self.images.append(img)
        self.image = self.images[0]
        
        # set position and create hitbox
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collideRect =  pygame.rect.Rect((x, y), (tile_size-15, tile_size-25))
        self.collideRect.midbottom = self.rect.midbottom
        
        # variables
        self.move_dir = 1
        self.move_counter = 0
        self.frame = 0
        self.counter = 0
        
    def update(self):
        #increment animation frame
        self.frame += 0.1
        self.counter = int(self.frame)
        
        # move enemy
        self.rect.x += self.move_dir
        self.move_counter += 1
        if self.move_counter > 50:
            # flip direction after 50 frames
            self.move_dir *= -1
            self.move_counter *= -1
            
        # update hitbox position
        self.collideRect.midbottom = self.rect.midbottom   
            
        # animate
        self.image = self.images[(self.counter % 4)]
        # RENDER HITBOX
        # pygame.draw.rect(screen,WHITE,self.collideRect,2)
            
        
        
        
# set world data
world_data =[
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
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

blob_group = pygame.sprite.Group()

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
    screen.blit(sun_img,(tile_size*2,tile_size*2))
     #draw tiles
    world.draw()
     #enemy logic
    blob_group.draw(screen)
    blob_group.update()
     #player movement and rendering
    player.update()
    
    # --- update display
    pygame.display.update()

# end   
pygame.quit()