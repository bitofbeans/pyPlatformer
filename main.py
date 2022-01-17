# --- INITIALIZE ----------------------------------------------------------------------------- #
# Import modules
import pygame
import json
from itertools import repeat
from math import sin, pi

# Initialize pygame and create clock
pygame.init()
timer = 0
clock = pygame.time.Clock()
fps = 60

# Game Variables
tile_size = 50
game_over = 0

# Global Constants
hideUnknownTiles = True # When true, it hides the tiles that it can not recognize
screenWidth = 1000
screenHeight = 1000
offset = repeat((0, 0))
main_menu = True

# Player Variables
### optimised value / tile size it was optimised on
### new value * tile_size
playerWidth = tile_size*0.4 # 50 = 20
playerHeight = tile_size*0.7 # 50 = 35
gravity = 0.016*tile_size # 50 = 0.8
fallMax = 0.3*tile_size  # 50 = 15
jumpPower = -0.2*tile_size # 50 = -10
moveSpeed = 0.03*tile_size # 50 = 1.5
friction = 0.8

# Color Definitions
BLACK = (0,0,0)
WHITE = (255,255,255)

# Create game window
org_screen = pygame.display.set_mode((screenWidth,screenHeight))
screen = org_screen.copy()
pygame.display.set_caption('Platformer')

# Image imports
sun_img = pygame.image.load('img/deco/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size*2, tile_size*2))
bg_img = pygame.image.load('img/deco/sky.png')
border_img = pygame.image.load('img/deco/border.png')
border_img = pygame.transform.scale(border_img, (screenWidth, 1328.125))

# Import outline image and outline data
outline_img = pygame.image.load('img/tile/outline.png')
pixelRes= outline_img.get_width()
scaler = (tile_size / pixelRes)+(0.002*tile_size)
outline_img = pygame.transform.scale(outline_img,((pixelRes+2)*scaler,(pixelRes+2)*scaler))
scaler -=0.2
# --- FUNCTIONS ----------------------------------------------------------------------------- #

# Shake Function
def shake():
    s = -1
    for _ in range(0, 3):
        for x in range(0, 10, 5):
            for y in range(0, 10, 5):
                yield (x*s, y*s)
        for x in range(10, 0, 5):
            for y in range(0, 10, 5):
                yield (x*s, y*s)
        s *= -1
    while True:
        yield (0, 0)
        
# Load world from .json
def loadData(input): 
    # File path for .json file
    data_file= 'world_data.json'

    # Load file
    with open(data_file, "r") as read_file:
            data = json.load(read_file)
    # return data
    return data[input]

# Load all world data from .json
def loadWorld(input):
    spawn_point = loadData(f"spawn{input}")
    spawn_point[0], spawn_point[1] = spawn_point[0]*tile_size, spawn_point[1]*tile_size
    world_data = loadData(f"world{input}")
    return world_data, spawn_point

# --- SPRITES ----------------------------------------------------------------------------- #

# --- BUTTON SPRITE ------------------------- #
class Button():
    def __init__(self, x, y, name, scale):
        # set image
        button = pygame.image.load('img/ui/'+str(name)+'.png')
        button = pygame.transform.scale(button, scale)
        buttonPress = pygame.image.load('img/ui/'+str(name)+'_press.png')
        buttonPress = pygame.transform.scale(buttonPress, scale)
        self.images = [button, buttonPress]
        self.image = button
        # get image rect
        self.rect = self.image.get_rect()
        # position
        self.rect.x = x + 7.7
        self.rect.y = y + 7.7*2
        # trim button rect
        self.rect.height = self.rect.height - (6.7*4)
        self.rect.width = self.rect.width - (6.7*3)
        # position
        self.x = x
        self.y = y
        #clicked
        self.clicked = False
        # animate
        self.frame = 0
        
    def draw(self):
        action = False
        #get mouse pos
        pos = pygame.mouse.get_pos()
        self.frame = 0
        # check mouse touching and clicking
        if self.rect.collidepoint(pos):
            self.frame = 1
            if pygame.mouse.get_pressed()[0] == True and self.clicked == False:
                # button clicked
                action = True
                self.clicked = True
        # if not clicking mouse
        if pygame.mouse.get_pressed()[0] == False:
            self.clicked = False
        
        
        # draw button
        self.image = self.images[self.frame]
        screen.blit(self.image, (self.x, self.y))
        
        # return if button pressed
        return action
        
# --- PLAYER SPRITE ------------------------- #
class Player():
         
    def __init__(self,x,y):
        # Create animation variables
        self.images_right = []
        self.images_left = []
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
        # Load ghost frames
        self.images_deadr = []
        self.images_deadl = []
        for number in range(1,6):
            img_right = pygame.image.load(f'img/player/ghost{number}.png')
            img_right = pygame.transform.scale(img_right,(tile_size, tile_size))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_deadr.append(img_right)
            self.images_deadl.append(img_left)
        
        # Create player hitbox
        self.image = self.images_right[0]
        self.rect = pygame.rect.Rect(x, y, playerWidth, playerHeight)
        
        # Set Position and variables
        self.reset(x,y)
    
    def update(self,game_over, world_num):
        ### --- update player --- ###
        def gameOver(gameover):
            # game over
            self.frame=0
            self.velX = 5 *-self.direction
            self.velY = -1
            global offset
            offset = shake()
            return gameover
        
        # Set delta x/y
        dx = 0
        dy = 0
        # if dead, fly ghost up
        if game_over != 0:
            if game_over == -1:
                # render player
                self.frame += 0.2
                if int(self.frame) > 4: self.frame = 4
                self.counter = int(self.frame)
                if self.direction == 1:
                    self.image = self.images_deadl[self.counter%5]
                else:
                    self.image = self.images_deadr[self.counter%5]
                self.velX *= 0.9
                self.velY -= 0.15
                self.x += self.velX
                self.y += self.velY
                if self.y < -50:
                    self.y = -50
                    self.velY = 0
                    self.velX = 0
                screen.blit(self.image, (self.x,self.y-3))
                return game_over, world_num
        
        # if alive, continue onward
        # Get keys pressed
        key = pygame.key.get_pressed()
        
        # --- Move player if keys pressed
         # Y axis
        if key[pygame.K_UP] and self.jumped == 0:
            self.jumped = 1
        elif key[pygame.K_UP]: self.jumped += 1
        if key[pygame.K_UP] and 1 <= self.jumped <= 6 and self.airtime < 6:
            # jump
            self.velY = jumpPower
        if key[pygame.K_UP] == False: self.jumped = 0
       
        # X axis
        if key[pygame.K_LEFT]:
            # move left
            self.velX -= moveSpeed
            self.direction = -1
            self.frame += 0.07
        if key[pygame.K_RIGHT]:
            # move right
            self.velX += moveSpeed
            self.direction = 1
            self.frame += 0.07
        # Change X by velocity
        self.velX *= friction
        dx += int(self.velX)
        
        # Handle animation -----------
             # animation frames
         #### idle = 0,1
         #### run = 2,3
         #### air = 4,5
        self.frame += 0.05
        self.counter = int(self.frame)
        
        if self.airtime > 1:
            #if in air
            if self.velY >= 0:
                # and falling
                if self.direction == 1:
                    #right
                    self.image = self.images_right[5]
                else:
                    #left
                    self.image = self.images_left[5]
            else:
                #and falling
                if self.direction == 1:
                    #right
                    self.image = self.images_right[4]
                else:
                    #left
                    self.image = self.images_left[4]
        elif (key[pygame.K_RIGHT]-key[pygame.K_LEFT]) != 0:
            #if moving
            if self.direction == 1:
                #right
                self.image = self.images_right[(self.counter % 2)+2]
            else:
                #left
                self.image = self.images_left[(self.counter % 2)+2]
        else:
            #idle
            if self.direction == 1:
                #right
                self.image = self.images_right[(self.counter % 2)]
            else:
                #left
                self.image = self.images_left[(self.counter % 2)]
        # -----------------------------------
        
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
         # returns all of the enemies we are touching
        hits = pygame.sprite.spritecollide(self, blob_group, False)
        # for each enemy we are touching,
        for Enemy in hits:
                # if the slime we are touching is living
                if Enemy.alive:
                    if self.velY < 3:
                        # if we didnt jump on it, game over
                        game_over = gameOver(-1)
                    else:
                        # if we jumped on top of it, kill the slime
                        Enemy.die()
            
            
        # check for collision with lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            # if touching lava, die
            game_over = gameOver(-1)
        
        
        # update player position
        self.x += dx
        self.y += dy
        self.rect = pygame.rect.Rect(self.x+(playerWidth/2), self.y, playerWidth, playerHeight)
          
        # render player
        screen.blit(self.image, (self.x,self.y-3))
        
        # RENDER HITBOX
        #pygame.draw.rect(screen,WHITE,self.rect,2)
        
        # return the variables and feed it back in
        return game_over, world_num
    
    def reset(self, x, y):
        # Set Position and variables
        # reset
        self.x = x
        self.y = y
        self.rect = pygame.rect.Rect(self.x+(playerWidth/2), self.y, playerWidth, playerHeight)
        self.velX = 0
        self.velY = 0
        self.jumped = 0
        self.direction = 1
        self.airtime = 0 
        self.frame = 0
        self.counter = 0
        

# --- WORLD SPRITE ------------------------- #
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

# --- ENEMY SPRITE ------------------------- #
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # inherit sprite constructor
        pygame.sprite.Sprite.__init__(self)
        
        # add animation frames
        self.images = []
        for i in range(0,5):
            img = pygame.image.load(f'img/enemy/blob{i}.png').convert()
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
        self.alive = True
        self.alpha = 255

    def die(self):
        # alive bool = false 
        self.alive = False
        self.image = self.images[4]
    
    def update(self):
    
        if self.alive:
            #increment animation frame
            self.frame += 0.1
            self.counter = int(self.frame)
            
            # animate image
            self.image = self.images[(self.counter % 4)]
            
            # move enemy
            self.x += self.move_dir
            self.move_counter += 1
            if self.move_counter > 50:
                # flip direction after 50 steps past origin
                self.move_dir *= -1
                self.move_counter *= -1
                
            # update hitbox position
            self.rect = (self.x+(15/2), self.y+tile_size-25, tile_size-15, tile_size-25)
        else:
            # slowly fade out
            self.image.set_alpha(self.alpha)
            self.alpha -=15
            if self.alpha >255:
                # if we are faded out all the way, remove slime
                blob_group.remove(self)

        # render inside the update function for more control
        screen.blit(self.image, (self.x,self.y))
        
        # RENDER HITBOX
        #pygame.draw.rect(screen,(255,0,0),self.rect,2)
        
            
# --- LAVA SPRITE ------------------------- #
class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
            # use pygame sprite constructor
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
            # animate lava
            self.frame += 0.2
            self.counter = int(self.frame)
            self.image = self.images[(self.counter % 16)]
            
            # set hitbox
            self.hitbox = (self.rect.x, self.rect.y+(tile_size-25), tile_size, tile_size-25)
            
            #render lava
            screen.blit(self.image, (self.x,self.y))
            #RENDER HITBOX
            #pygame.draw.rect(screen,WHITE,self.hitbox,2)
            #pygame.draw.rect(screen,(255,0,0),self.rect,2)
     
# --- CREATE SPRITES ----------------------------------------------------------------------------- #
 #load world
world_num = 1
default_wrld = world_num
world_data, spawn_point = loadWorld(world_num)

 #make player
player = Player(spawn_point[0], spawn_point[1])
 # sprite groups
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
 # world
world = World(world_data)
 #create buttons
restart_button = Button(screenWidth//2 - 50, 890, 'restart_button', (100, 100))
start_button = Button(screenWidth//2 - 150, screenHeight//2, 'start_button', (100, 100))
exit_button = Button(screenWidth//2 + 50, screenHeight//2, 'exit_button', (100, 100))

# --- GAME LOOP ----------------------------------------------------------------------------- #
run = True
while run:
    # --- Tick FPS ------------------ #
    dt = clock.tick(fps)/1000
    timer += dt
    
    # --- Escape Condition ------------ #
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
    
    # --- Game Logic/Rendering -------- #
     #render bg
    screen.blit(bg_img,(0,0))
    
    if main_menu == True:
        # --- Main Menu --- #
        rad = (timer*pi)/180
        screen.blit(border_img,(0,
                                (sin(rad*150)*20)-200))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else: 
        # --- Game Physics --- #
        screen.blit(sun_img,(tile_size*2,tile_size*2))
        # update groups
        lava_group.update()
        blob_group.update()
        #draw tiles
        world.draw()
        #player movement and rendering
          # update player, but also get the game_over and world_num variable
        game_over, world_num = player.update(game_over, world_num)
        # if player has died
        if game_over == -1:
            # restart button pressed
            if restart_button.draw():
                # reset player
                player.reset(spawn_point[0], spawn_point[1])
                game_over = 0
        ### --- WORLD SWITCHING --- ###
        if world_num != default_wrld:
            # --- if world has changed
            # reset default world
            default_wrld = world_num
            # delete all of past world data
            del world
            # clear sprites
            blob_group.empty()
            lava_group.empty()
            
            # reload new world
            world_data, spawn_point = loadWorld(world_num)
            world = World(world_data)
            # reset player
            player.reset(spawn_point[0], spawn_point[1])
            
            
    # --- Render Screen -------------- #
    org_screen.blit(screen, next(offset))
    
    # --- Update Display ------------- #
    pygame.display.update()

# --- END ----------------------------------------------------------------------------- #
pygame.quit()