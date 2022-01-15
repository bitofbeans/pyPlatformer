# Import Pygame
from lib2to3.refactor import get_all_fix_names
import pygame
#from pygame.locals import *

# Initialize pygame and create clock
pygame.init()
clock = pygame.time.Clock()
fps = 60

# Game Variables
tile_size = 50
game_over = 0

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
        self.rect = pygame.rect.Rect(x, y, playerWidth, playerHeight)
        print(self.rect.x)
        
        # Set Position and variables
        self.x = x
        self.y = y
        self.c_width = playerWidth
        self.c_height = playerHeight
        self.velX = 0
        self.velY = 0
        self.jumped = 0
        self.direction = 0
        self.airtime = 0
    
    def update(self,game_over):
        # Set delta x/y
        dx = 0
        dy = 0
        
        if game_over != 0:
            
            # render player
            screen.blit(self.image, self.rect)
            return game_over
        
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
            if tile[1].colliderect(self.rect.x + dx, self.y, self.rect.width, self.rect.height):
                if self.velX >= 0:
                    dx = tile[1].left - self.rect.right
                elif self.velX < 0:
                    dx = tile[1].right - self.rect.left
            # check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.y + dy, self.rect.width, self.rect.height):
                # check if above the ground/ if falling
                if self.velY >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.airtime = 0
                # check if below the ground/ if jumping
                elif self.velY < 0:
                    dy = tile[1].bottom - self.rect.top
                self.velY = 0
        
        # check for collision with enemies
        if pygame.sprite.spritecollide(self, blob_group, False):
            game_over = -1
            
        # check for collision with lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            game_over = -1
        
        
        # update player position
        self.x += dx
        self.y += dy
        self.rect = pygame.rect.Rect(self.x+(playerWidth/2), self.y, playerWidth, playerHeight)
          
        # render player
        screen.blit(self.image, (self.x,self.y))
        
        # RENDER HITBOX
        #pygame.draw.rect(screen,(255,0,0),self.rect,2)
        #pygame.draw.rect(screen,WHITE,self.rect,2)
        return game_over


# --- WORLD SPRITE
class World():
    def __init__(self,data):
      # clear list
      self.tile_list = []
      
      # load images
      self.tileTypes = [1,2,3,6]
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
                      # add dirt
                      img = pygame.transform.scale(dirt_img,(tile_size,tile_size))
                      img_rect = img.get_rect()
                      img_rect.x = col_count * tile_size
                      img_rect.y = row_count * tile_size
                      tile = (img,img_rect,tile)
                      self.tile_list.append(tile)

                  elif tile == 2:
                      # add grass
                      img = pygame.transform.scale(grass_img,(tile_size,tile_size))
                      img_rect = img.get_rect()
                      img_rect.x = col_count * tile_size
                      img_rect.y = row_count * tile_size
                      tile = (img,img_rect,tile)
                      self.tile_list.append(tile)
                  elif tile == 3:
                      # create enemy 
                      blob = Enemy(col_count * tile_size, row_count * tile_size)
                      blob_group.add(blob)
                  elif tile == 6:
                      # create lava
                      lava = Lava(col_count * tile_size, row_count * tile_size)
                      lava_group.add(lava)
                  else: 
                      # unknown tile
                      img = pygame.transform.scale(err,(tile_size,tile_size))
                      global hideUnknownTiles
                      if hideUnknownTiles == False:
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

### --- ENEMY SPRITE
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
        self.x = x
        self.y = y
        self.rect = pygame.rect.Rect(x, y, tile_size-15, tile_size-25)


        # variables
        self.move_dir = 1
        self.move_counter = 0
        self.frame = 0
        self.counter = 0
        
    def render(self):
        screen.blit(self.image, (self.x,self.y+50))
    
    def update(self):
        #increment animation frame
        self.frame += 0.1
        self.counter = int(self.frame)
        
        # move enemy
        self.x += self.move_dir
        self.move_counter += 1
        if self.move_counter > 50:
            # flip direction after 50 frames
            self.move_dir *= -1
            self.move_counter *= -1
            
        # update hitbox position
        self.rect = (self.x+(15/2), self.y+tile_size-25, tile_size-15, tile_size-25)
            
        # animate
        self.image = self.images[(self.counter % 4)]
        screen.blit(self.image, (self.x,self.y))
        
        # RENDER HITBOX
        #pygame.draw.rect(screen,(255,0,0),self.rect,2)
        
            
### --- LAVA SPRITE
class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
        
            # add animation frames
            self.images = []
            for i in range(1,17):
                img = pygame.image.load(f'img/tile/lava{i}.png')
                img = pygame.transform.scale(img,(tile_size,tile_size))
                self.images.append(img)
            self.image = self.images[0]
            
            # set position and create hitbox
            self.x = x
            self.y = y
            self.rect = pygame.rect.Rect(x, y+tile_size-25, tile_size, tile_size-25)
            
            #animation variables
            self.frame = 0
            self.counter = 0
            
        def update(self):
            self.frame += 0.2
            self.counter = int(self.frame)
            self.image = self.images[(self.counter % 16)]
            self.hitbox = (self.rect.x, self.rect.y+(tile_size-25), tile_size, tile_size-25)
            screen.blit(self.image, (self.x,self.y))
            #RENDER HITBOX
            #pygame.draw.rect(screen,WHITE,self.hitbox,2)
            #pygame.draw.rect(screen,(255,0,0),self.rect,2)
     
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
lava_group = pygame.sprite.Group()

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

    # update groups
    if game_over == 0:
        lava_group.update()
        blob_group.update()
    
    #draw tiles
    world.draw()

    #player movement and rendering
    game_over = player.update(game_over)
    
    # --- update display
    pygame.display.update()

# end   
pygame.quit()