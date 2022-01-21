import pygame
import json
from os import path

data_file= 'world_data.json'

pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 50
cols = 20
margin = 50
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')


#load images
sun_img = pygame.image.load('assets/deco/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('assets/deco/sky.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('assets/tile/dirt.png')
grass_img = pygame.image.load('assets/tile/grass.png')
blob_img = pygame.image.load('assets/enemy/blob0.png')
platform_x_img = pygame.image.load('assets/tile/platform_x.png')
platform_y_img = pygame.image.load('assets/tile/platform_y.png')
lava_img = pygame.image.load('assets/tile/lava1.png')
coin_img = pygame.image.load('assets/tile/coin1.png')
exit_img = pygame.image.load('assets/tile/exit.png')
save_img = pygame.image.load('assets/ui/save_button.png')
save_img = pygame.transform.scale(save_img, (40, 40))
load_img = pygame.image.load('assets/ui/load_button.png')
load_img = pygame.transform.scale(load_img, (40, 40))

#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
green = (144, 201, 120)
black = (0, 0, 0)

font = pygame.font.SysFont('Futura', 24, bold=True)

#create empty tile list
world_data = []
for row in range(20):
    r = [0] * 20
    world_data.append(r)

#create boundary
for tile in range(0, 20):
    world_data[19][tile] = 2
    world_data[0][tile] = 1
    world_data[tile][0] = 1
    world_data[tile][19] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_grid():
    for c in range(21):
        #vertical lines
        pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
        #horizontal lines
        pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))

def draw_world():
    for row in range(20):
        for col in range(20):
            if world_data[row][col] > 0:
                if world_data[row][col] == 1:
                    #dirt blocks
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 2:
                    #grass blocks
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 3:
                    #enemy blocks
                    img = pygame.transform.scale(blob_img, (tile_size, int(tile_size)))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 4:
                    #horizontally moving platform
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 5:
                     #vertically moving platform
                    img = pygame.transform.scale(platform_y_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 6:
                    #lava
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 7:
                     #coin
                    img = pygame.transform.scale(coin_img, (tile_size, tile_size))
                    screen.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 8:
                    #exit
                    img = pygame.transform.scale(exit_img, (tile_size, int(tile_size)))
                    screen.blit(img, (col * tile_size, row * tile_size))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

#json formatting
#thanks to jannismain
# https://gist.github.com/jannismain/e96666ca4f059c3e5bc28abb711b5c92
from typing import Union
class CompactJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that puts small containers on single lines."""

    CONTAINER_TYPES = (list, tuple, dict)
    """Container datatypes include primitives or other containers."""

    MAX_WIDTH = 70
    """Maximum width of a container that might be put on a single line."""

    MAX_ITEMS = 30
    """Maximum number of items in container that might be put on single line."""

    INDENTATION_CHAR = " "

    def __init__(self, *args, **kwargs):
        # using this class without indentation is pointless
        if kwargs.get("indent") is None:
            kwargs.update({"indent": 4})
        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    def encode(self, o):
        """Encode JSON object *o* with respect to single line lists."""
        if isinstance(o, (list, tuple)):
            if self._put_on_single_line(o):
                return "[" + ", ".join(self.encode(el) for el in o) + "]"
            else:
                self.indentation_level += 1
                output = [self.indent_str + self.encode(el) for el in o]
                self.indentation_level -= 1
                return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"
        elif isinstance(o, dict):
            if o:
                if self._put_on_single_line(o):
                    return "{ " + ", ".join(f"{self.encode(k)}: {self.encode(el)}" for k, el in o.items()) + " }"
                else:
                    self.indentation_level += 1
                    output = [self.indent_str + f"{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
                    self.indentation_level -= 1
                    return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"
            else:
                return "{}"
        elif isinstance(o, float):  # Use scientific notation for floats, where appropiate
            return format(o, "g")
        elif isinstance(o, str):  # escape newlines
            o = o.replace("\n", "\\n")
            return f'"{o}"'
        else:
            return json.dumps(o)

    def iterencode(self, o, **kwargs):
        """Required to also work with `json.dump`."""
        return self.encode(o)

    def _put_on_single_line(self, o):
        return self._primitives_only(o) and len(o) <= self.MAX_ITEMS and len(str(o)) - 2 <= self.MAX_WIDTH

    def _primitives_only(self, o: Union[list, tuple, dict]):
        if isinstance(o, (list, tuple)):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o)
        elif isinstance(o, dict):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o.values())

    @property
    def indent_str(self) -> str:
        return self.INDENTATION_CHAR*(self.indentation_level*self.indent)

#create load and save buttons
save_button = Button(screen_width // 2 + 50, screen_height - 50, save_img)
load_button = Button(screen_width // 2 - 150, screen_height - 50, load_img)
def loadData(input): 
    # File path for .json file
    data_file= 'world_data.json'

    # Load file
    with open(data_file, "r") as read_file:
            data = json.load(read_file)
    # return data
    return data[input]

# Load all world data from .json

#main game loop
run = True
while run:

    clock.tick(fps)

    #draw background
    screen.fill(white)
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (tile_size * 2, tile_size * 2))

    #load and save level
    if save_button.draw():
        
        # Load file
        with open(data_file, "r") as read_file:
            data = json.load(read_file)
        # change world data in file
        data[f"world{level}"] = world_data

        #print(data)
        json.dump(data, open(data_file, "w"), cls=CompactJSONEncoder)
        
    if load_button.draw():
        try:
            world_data = loadData(f"world{level}")
        except:
            # add empty world in place
            level = 1
            world_data = loadData(f"world{level}")
            continue
            # Load file
            with open(data_file, "r") as read_file:
                data = json.load(read_file)
            # change world data in file
            world_data = []
            for row in range(20):
                r = [0] * 20
                world_data.append(r)

            #create boundary
            for tile in range(0, 20):
                world_data[19][tile] = 2
                world_data[0][tile] = 1
                world_data[tile][0] = 1
                world_data[tile][19] = 1
            
            data[f"world{level}"] = world_data
            data[f"spawn{level}"] = [2,18]

            #print(data)
            json.dump(data, open(data_file, "w"), cls=CompactJSONEncoder)
        

    #show the grid and draw the level tiles
    draw_grid()
    draw_world()


    #text showing current level
    draw_text(f'Level: {level}', font, black, tile_size, screen_height - 40)
    draw_text('Press UP or DOWN to change level', font, black, screen_width // 2 + 100, screen_height - 40)

    #event handler
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #mouseclicks to change tiles
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
            pos = pygame.mouse.get_pos()
            x = pos[0] // tile_size
            y = pos[1] // tile_size
            #check that the coordinates are within the tile area
            if x < 20 and y < 20:
                #update tile value
                if pygame.mouse.get_pressed()[0] == 1:
                    world_data[y][x] += 1
                    if world_data[y][x] > 8:
                        world_data[y][x] = 0
                elif pygame.mouse.get_pressed()[2] == 1:
                    world_data[y][x] -= 1
                    if world_data[y][x] < 0:
                        world_data[y][x] = 8
        if event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        #up and down key presses to change level number
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            elif event.key == pygame.K_DOWN and level > 1:
                level -= 1

    #update game display window
    pygame.display.update()

pygame.quit()