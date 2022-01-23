# --- INITIALIZE ----------------------------------------------------------------------------- #
# Import modules
import pygame
from pygame import mixer
import json
from itertools import repeat
from math import sin, pi

# Initialize pygame and create clock
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
timer = 0
clock = pygame.time.Clock()
fps = 60

# Game Variables
tile_size = 50
game_over = 0
score = 0

# Global Constants
hideUnknownTiles = False # When true, it hides the tiles that it can not recognize
screenWidth = 1000
screenHeight = 1000
offset = repeat((0, 0))
main_menu = True
max_levels = 7

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
BLUE = (0,0,255)

# Create game window
org_screen = pygame.display.set_mode((screenWidth,screenHeight))
screen = org_screen.copy()
pygame.display.set_caption('Platformer')

# Image imports
bg_img = pygame.image.load('assets/deco/sky.png')
border_img = pygame.image.load('assets/deco/border.png')
border_img = pygame.transform.scale(border_img, (screenWidth, 1328.125))

# Define font
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font = pygame.font.SysFont('Bauhaus 93', 70)

# Import outline image and outline data
outline_img = pygame.image.load('assets/tile/outline.png')
pixelRes= outline_img.get_width()
scaler = (tile_size / pixelRes)+(0.002*tile_size)
outline_img = pygame.transform.scale(outline_img,((pixelRes+2)*scaler,(pixelRes+2)*scaler))
scaler -=0.2

# Load Sounds
coinFX = pygame.mixer.Sound('assets/music/coin2.wav')
coinFX.set_volume(0.5)
jumpFX = pygame.mixer.Sound('assets/music/jump2.wav')
jumpFX.set_volume(0.5)
hitFX = pygame.mixer.Sound('assets/music/hit2.wav')
hitFX.set_volume(0.5)

# --- FUNCTIONS ----------------------------------------------------------------------------- #
# draw text 
def drawText(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x,y))

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
        
# Load data from .json
def loadData(input): 
    try:
        # File path for .json file
        data_file= 'world_data.json'

        # Load file
        with open(data_file, "r") as read_file:
                data = json.load(read_file)
        returned = data[input]
    except:
        data_file= 'world_backup.json'

        # Load file
        with open(data_file, "r") as read_file:
                data = json.load(read_file)
        returned = data[input]
                
    # return data
    return returned

# Load world from .json
def loadWorld(input):
    spawn_point = loadData(f"spawn{input}")
    spawn_point[0], spawn_point[1] = spawn_point[0]*tile_size, spawn_point[1]*tile_size
    world_data = loadData(f"world{input}")
    return world_data, spawn_point

def reset_level(world_num):
    # clear sprites
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    # reload new world
    world_data, spawn_point = loadWorld(world_num)
    world = World(world_data)
    # reset player
    player.reset(spawn_point[0], spawn_point[1])
    
    return world

# --- SPRITES ----------------------------------------------------------------------------- #

# --- BUTTON SPRITE ------------------------- #
class Button():
    def __init__(self, x, y, name, scale):
        # set image
        button = pygame.image.load('assets/ui/'+str(name)+'.png')
        button = pygame.transform.scale(button, scale)
        buttonPress = pygame.image.load('assets/ui/'+str(name)+'_press.png')
        buttonPress = pygame.transform.scale(buttonPress, scale)
        self.images = [button, buttonPress]
        self.image = button                   
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
                img_right = pygame.image.load('assets/player/'+ img +'.png')
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
            img_right = pygame.image.load(f'assets/player/ghost{number}.png')
            img_right = pygame.transform.scale(img_right,(tile_size, tile_size))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_deadr.append(img_right)
            self.images_deadl.append(img_left)
        
        # Create player hitbox
        self.image = self.images_right[0]
        self.rect = pygame.rect.Rect(x, y, playerWidth, playerHeight)
        
        # Set Position and variables
        self.reset(x,y)
    
    def update(self,game_over):
        ### --- update player --- ###
        def gameOver(gameover):
            # game over
            self.frame=0
            self.velX = 5 *-self.direction
            self.velY = -1
            global offset
            offset = shake()
            hitFX.play()
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
                return game_over
        
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
            if self.jumped == 1 or self.airtime == 0:
                jumpFX.play()
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
                        self.airtime = 0
                        self.velY = jumpPower
                        self.jumped = 0
                        dy = Enemy.rect.top - self.rect.bottom
                        dy += self.velY
            
            
        # check for collision with lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            # if touching lava, die
            game_over = gameOver(-1)
            
        # check for collision with exit
        if pygame.sprite.spritecollide(self, exit_group, False):
            # if touching exit, win
            game_over = 1
        
        # update player position
        self.x += dx
        self.y += dy
        self.rect = pygame.rect.Rect(self.x+(playerWidth/2), self.y, playerWidth, playerHeight)
          
        # render player
        screen.blit(self.image, (self.x,self.y-3))
        
        # RENDER HITBOX
        #pygame.draw.rect(screen,WHITE,self.rect,2)
        
        # return the variables and feed it back in
        return game_over
    
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
      dirt_img = pygame.image.load('assets/tile/dirt.png')
      grass_img = pygame.image.load('assets/tile/grass.png')
      err = pygame.image.load('assets/tile/unknown.png')
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
                  elif tile == 7:
                      # create lava
                      coin = Coin(col_count * tile_size, row_count * tile_size)
                      coin_group.add(coin)
                  elif tile == 8:
                      # create enemy 
                      exit = Exit(col_count * tile_size, row_count * tile_size)
                      exit_group.add(exit)
                      
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
            img = pygame.image.load(f'assets/enemy/blob{i}.png').convert()
            img = pygame.transform.scale(img,(tile_size,tile_size))
            self.images.append(img)
        self.image = self.images[0]
        
        # set position and create hitbox
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect = pygame.rect.Rect(x, y, tile_size*0.7, tile_size*0.5)

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
        hitFX.play()
    
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
            self.rect = pygame.rect.Rect(self.x+(tile_size*0.7 / 4), self.y+tile_size*0.5, tile_size*0.7, tile_size*0.5)
        else:
            # slowly fade out
            self.image.set_alpha(self.alpha)
            self.alpha -=15
            if self.alpha < 0:
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
                img = pygame.image.load(f'assets/tile/lava{i}.png')
                img = pygame.transform.scale(img,(tile_size,tile_size))
                self.images.append(img)
            self.image = self.images[0]
            
            # set position and create hitbox
            self.x = x
            self.y = y
            self.rect = pygame.rect.Rect(x, y+tile_size*0.5, tile_size, tile_size*0.5)
            
            #animation variables
            self.frame = 0
            self.counter = 0
            
        def update(self):
            # animate lava
            self.frame += 0.2
            self.counter = int(self.frame)
            self.image = self.images[(self.counter % 16)]
            
            # set hitbox
            self.hitbox = pygame.rect.Rect(self.rect.x, self.rect.y+tile_size*0.5, tile_size, tile_size*0.5)
            
            #render lava
            screen.blit(self.image, (self.x,self.y))
            #RENDER HITBOX
            #pygame.draw.rect(screen,(255,0,0),self.rect,2)

# --- COIN SPRITE ------------------------- #            
class Coin(pygame.sprite.Sprite):
        def __init__(self, x, y):
            # use pygame sprite constructor
            pygame.sprite.Sprite.__init__(self)
        
            # add animation frames
            self.images = []
            for i in range(1,5):
                img = pygame.image.load(f'assets/tile/coin{i}.png')
                img = pygame.transform.scale(img,(tile_size,tile_size))
                self.images.append(img)
            self.image = self.images[0]
            
            # set position and create hitbox
            self.x = x
            self.y = y
            self.rect = pygame.rect.Rect(self.x+((tile_size*0.5) / 2), self.y+((tile_size*0.5) / 2), tile_size*0.5, tile_size*0.5)
            #animation variables
            self.frame = 0
            self.counter = 0
            
        def update(self):
            # animate lava
            self.frame += 0.15
            self.counter = int(self.frame)
            self.image = self.images[(self.counter % 4)]
            
            # set hitbox
            self.rect = pygame.rect.Rect(self.x+((tile_size*0.5) / 2), self.y+((tile_size*0.5) / 2), tile_size*0.5, tile_size*0.5)
            
            #render lava
            screen.blit(self.image, (self.x,self.y))
            #RENDER HITBOX
            #pygame.draw.rect(screen,(255,0,0),self.rect,2)


# --- EXIT SPRITE ------------------------- #
class Exit(pygame.sprite.Sprite):
        def __init__(self, x, y):
            # use pygame sprite constructor
            pygame.sprite.Sprite.__init__(self)
            # load image
            img = pygame.image.load('assets/tile/exit.png')
            img = pygame.transform.scale(img,(tile_size,tile_size))
            self.image = img
            # position
            self.x = x
            self.y = y
            self.rect = pygame.rect.Rect(x+(tile_size*0.75/2), y, tile_size*0.75, tile_size)
            
        def update(self):
            #render exit
            screen.blit(self.image, (self.x,self.y))
            
     
# --- CREATE SPRITES ----------------------------------------------------------------------------- #
 #load world
world_num = 1
world_data, spawn_point = loadWorld(world_num)
 #make player
player = Player(spawn_point[0], spawn_point[1])
 # sprite groups
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
# dummy coin
score_coin = Coin(tile_size-40, 0)
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
        
        # update lava and exits
        lava_group.update()
        exit_group.update()
        #draw tiles
        world.draw()
        # update groups
        blob_group.update()
        coin_group.update()
        #player movement and rendering
          # update player, but also get the game_over and world_num variable
        game_over = player.update(game_over)
        # if player has died
        if game_over == -1:
            if player.velY == 0:
                restart_button.y += ((screenHeight / 2)- restart_button.y) / 7
                restart_button.rect.y += ((screenHeight / 2)- restart_button.rect.y) / 7
            # restart button pressed
            if restart_button.draw():
                # reset player
                world = reset_level(world_num)
                game_over = 0
                score = 0 
                restart_button.y = 890
                restart_button.rect.y = 890 + 7.7*2
        # if player has won
        if game_over == 1:
            if world_num+1 > max_levels:
                # end of the game -----------------------
                if restart_button.draw():
                    # restart to main menu
                    world_num = 1
                    world = reset_level(world_num)
                    game_over = 0
                    main_menu = True
                    score = 0 
            else: 
                # --- NEXT WORLD --- #
                world_num += 1
                world = reset_level(world_num)
                game_over = 0
        # coin collision
        if game_over == 0:
            coin_collision = pygame.sprite.spritecollide(player, coin_group, True)
            if coin_collision:
                score += len(coin_collision)
                coinFX.play()
            score_coin.update()
            drawText('x ' + str(score), font_score, WHITE, tile_size, 17)
            
    # --- Render Screen -------------- #
    org_screen.blit(screen, next(offset))
    
    # --- Update Display ------------- #
    pygame.display.update()

# --- END ----------------------------------------------------------------------------- #
pygame.quit()