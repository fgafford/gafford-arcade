# found online: 
# https://thecodezine.com/easy-learn-python-space-shooter-game-building-using-pygame/
from __future__ import division
import pygame
import random
import time
from datetime import timedelta
from os import path
from PlayerControls import PlayerControls

## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

###############################
## to be placed in "constant.py" later
WIDTH = 1280
HEIGHT = 720
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


####### Difficutly Vars #######
# varialbe used to increase difficulty as game progresses
difficulty_mutiplier = 1
# the amount to increase the difficutly per interval
difficulty_increment = .1
# the interval (in seconds?) that increase the difficulty
difficulty_interval = 5
# maximum difficulty 
difficulty_max = 3


####### Game Varialbes ########
NUM_OF_LIVES = 3
NUM_OF_MISSILES = 3 

NUM_PLAYERS = 1
Player1 = PlayerControls(1) 
Player2 = PlayerControls(2) 
players = []

meteor_angle = 6
game_start_time = None
DEFAULT_SHOOT_RATE = 500
FAST_SHOOT_RATE = 250

###############################
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()  # For syncing the FPS
###############################

font_name = pygame.font.match_font('arial')


def main_menu():
    global screen
    global NUM_PLAYERS

    menu_song = pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "tmp-loading.png")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)

    screen.blit(title, (0, 0))

    while True:
        events = pygame.event.get()
        player_input = Player1.get_input(pygame)
        if player_input["1Player"]:
            NUM_PLAYERS = 1
            break
        if player_input["2Player"]:
            NUM_PLAYERS = 2
            break
        else:
            pygame.display.update()

def game_summary():
    global menu_display
    global screen
    global background_img

    global NUM_PLAYERS
    global players
    p1 = players[0]

    screen.blit(background_img, (0,0))
    draw_text(screen, "GAME OVER", 72, WIDTH/2, HEIGHT/4)

    if NUM_PLAYERS == 1:
        # Display Score 
        p1_x = WIDTH/2 
        p1_y = HEIGHT/2
        screen.blit(p1.image, (p1_x-25, p1_y))
        draw_text(screen, "Score:", 30, p1_x, p1_y+50)
        draw_text(screen, str(p1.score), 30, p1_x, p1_y+100)

    else:
        # P1 Score 
        p1_x = WIDTH/3 
        p1_y = HEIGHT/2
        screen.blit(p1.image, (p1_x-25, p1_y))
        draw_text(screen, "Blue Score:", 30, p1_x, p1_y+50)
        draw_text(screen, str(p1.score), 30, p1_x, p1_y+100)

        p2 = players[1]
        # P2 Score 
        p2_x = (WIDTH/3)*2
        p2_y = HEIGHT/2
        screen.blit(p2.image, (p2_x-25, p2_y))
        draw_text(screen, "Red Score:",  30, p2_x, p2_y+50)
        draw_text(screen, str(p2.score), 30, p2_x, p2_y+100)
        # Display winner banner

    pygame.display.update()

    # Stall a few seconds to make sure plyers see the game has ended
    time.sleep(1)

    # Loop here till button is pushed 
    while True:
        events = pygame.event.get()
        if Player1.has_input(pygame) or Player2.has_input(pygame):
            break
        else:
            a = 1 + 1
    
    # let linux keep the loop for now
    exit()


def draw_text(surf, text, size, x, y, align = 'midtop'):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    # True denotes the font to be anti-aliased
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    # print(text_rect.midtop)
    setattr(text_rect, align, (x, y))
    surf.blit(text_surface, text_rect)

def draw_player_stats(player, x, y, score_alignment = 'midtop'):
    # draw_text(screen, player.name, 18, x + 5, y + 5)
    draw_text(screen, str(player.score), 24, x, y + 10, score_alignment)
    draw_shield_bar(screen, x, y + 40, player.shield)
    draw_lives(screen, x, y + 60, player.lives - 1, player.mini_img)
    draw_missiles(screen, x, y + 90, player.missiles)

def get_game_start_time(percision = 0):
    raw = round(time.time() - game_start_time, percision)
    return str(timedelta(seconds=raw))

## check if the player collides with the mob
# gives back a list, True makes the mob element disappear
def check_player_hit(player):
    hits = pygame.sprite.spritecollide(
        player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            # running = False     ## GAME OVER 3:D
            player.hide()
            player.lives -= 1
            player.shield = 100

    ## if the player hit a power up
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.laser_upgrade()
        if hit.type == 'missile':
            player.add_missile()

    ## if player died and the explosion has finished, end game
    if player.lives == 0:
        game_summary()


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0)
    ## moving them to top
    # BAR_LENGTH = 100
    # BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(screen, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        screen.blit(img, img_rect)

def draw_missiles(screen, x, y, count):
    x_offset = 15
    screen.blit(missile_powerup, (x,y))
    screen.blit(ui_numbers["x"], (x + x_offset , y+5))
    number = str(count)
    for num in number:
        x_offset += 20
        screen.blit(ui_numbers[num], (x+ x_offset , y+5))


def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self, player_controls, color):
        pygame.sprite.Sprite.__init__(self)

        self.player_controls = player_controls
        self.score = 0
        self.missiles = NUM_OF_MISSILES
        player_img = pygame.image.load(path.join(img_dir, f'player_{color}.png')).convert()
        self.laser_img = pygame.image.load(path.join(img_dir, f'player_{color}_laser.png')).convert()
        self.mini_img = pygame.image.load(path.join(img_dir, f'player_{color}_extra_life.png')).convert()
        #self.mini_img = pygame.transform.scale(player_img, (25, 19))
        self.mini_img.set_colorkey(BLACK)

        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.set_start_position()
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = DEFAULT_SHOOT_RATE
        self.last_shot = pygame.time.get_ticks()
        self.lives = NUM_OF_LIVES
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def reset(self):
        self.lives = NUM_OF_LIVES
        self.missiles = NUM_OF_MISSILES
        self.score = 0

    def update(self):
        ## time out for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.shoot_delay = DEFAULT_SHOOT_RATE
            self.power_time = pygame.time.get_ticks()

        ## unhide
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.set_start_position()

        self.speedx = 0  # makes the player static in the screen by default.
        # then we have to check whether there is an event hanlding being done for the arrow keys being
        ## pressed

        ## will give back a list of the keys which happen to be pressed down at that moment
        player_input = self.player_controls.get_input(pygame)
        if player_input["left"]:
            self.speedx = -5
        elif player_input['right']:
            self.speedx = 5

        #Fire weapons by holding spacebar
        if player_input['blue'] or player_input['red']:
            self.shoot()

        if player_input['yellow'] or player_input['green']:
            self.fire_missile()

        ## check for the borders at the left and right
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def set_start_position(self):
        global NUM_PLAYER
        if NUM_PLAYERS == 1:
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30
        if NUM_PLAYERS == 2:
            player_number = self.player_controls.get_player_number()
            if player_number == 1:
                # which player are we?
                self.rect.centerx = WIDTH / 3
                self.rect.bottom = HEIGHT - 30
            if player_number == 2:
                # which player are we?
                self.rect.centerx = (WIDTH / 3 ) * 2
                self.rect.bottom = HEIGHT - 30

    def shoot(self):
        ## to tell the laser where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                laser = Laser(self.rect.centerx, self.rect.top, self)
                all_sprites.add(laser)
                lasers.add(laser)
                shooting_sound.play()

            if self.power == 2:
                laser1 = Laser(self.rect.left, self.rect.centery, self)
                laser2 = Laser(self.rect.right, self.rect.centery, self)
                all_sprites.add(laser1)
                all_sprites.add(laser2)
                lasers.add(laser1)
                lasers.add(laser2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                self.shoot_delay = FAST_SHOOT_RATE
                laser1 = Laser(self.rect.left, self.rect.centery, self)
                all_sprites.add(laser1)
                lasers.add(laser1)

                laser2 = Laser(self.rect.right, self.rect.centery, self)
                all_sprites.add(laser2)
                lasers.add(laser2)

                shooting_sound.play()


    def fire_missile(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.missiles > 0:
            self.last_shot = now
            # Missile shoots from center of ship
            missile1 = Missile(self.rect.centerx, self.rect.top, self)
            lasers.add(missile1)
            all_sprites.add(missile1)
            missile_sound.play()
            self.missiles -= 1

    def add_to_score(self, points):
        self.score += points

    def laser_upgrade(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def add_missile(self):
        self.missiles += 1

    def hide(self):
        # TODO: make is so that we cannot shoot in this state
        self.hidden = True
        self.missiles = 3
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .98 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        # for randomizing the speed of the Mob
        min_meteor_speed = 5
        max_meteor_speed = 5
        self.speedy = 5
        # self.speedy = random.randrange(min_meteor_speed, max_meteor_speed)

        ## randomize the movements a little more
        self.speedx = random.randrange((meteor_angle * -1), meteor_angle)

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        # time when the rotation has to happen
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50:  # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        ## now what if the mob element goes out of the screen

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            # for randomizing the speed of the Mob
            self.speedy = random.randrange(1, 8)

## defines the sprite for Powerups


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'missile'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the laser according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()


## defines the sprite for lasers
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.image = player.laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the laser according to the current position of the player
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            # TODO add score to player
            self.kill()



class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.image = missile_powerup
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


###################################################
## Load all game images

background_raw = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_img = pygame.transform.scale( background_raw, (WIDTH, HEIGHT))

missile_img = pygame.image.load( path.join(img_dir, 'missile.png')).convert_alpha()
missile_powerup_raw = pygame.image.load( path.join(img_dir, 'missile_powerup.png')).convert_alpha()
missile_powerup = pygame.transform.scale( missile_powerup_raw, (12,30))
ui_numbers = {
        "x": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeralX.png')).convert_alpha(),  
        "0": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral0.png')).convert_alpha(),  
        "1": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral1.png')).convert_alpha(),  
        "2": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral2.png')).convert_alpha(),  
        "3": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral3.png')).convert_alpha(),  
        "4": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral4.png')).convert_alpha(),  
        "5": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral5.png')).convert_alpha(),  
        "6": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral6.png')).convert_alpha(),  
        "7": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral7.png')).convert_alpha(),  
        "8": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral8.png')).convert_alpha(),  
        "9": pygame.image.load( path.join(f'{img_dir}/numbers', 'numeral9.png')).convert_alpha(),  
        }

# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png',
    'meteorBrown_med1.png',
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]
meteor_count = 20

for image in meteor_list:
    meteor_images.append(pygame.image.load(
        path.join(img_dir, image)).convert())

## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    ## resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    ## player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

## load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load( path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load( path.join(img_dir, 'bolt_gold.png')).convert()
powerup_images['missile'] = missile_powerup.convert()


###################################################


###################################################
### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)  # simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))
###################################################

## TODO: make the game music loop over again and again. play(loops=-1) is not working
# Error :
# TypeError: play() takes no keyword arguments
#pygame.mixer.music.play()

#############################
## Game loop
running = True
menu_display = True
while running:
    if menu_display:
        main_menu()
        #Stop menu music
        pygame.mixer.music.stop()


        #### Game Init Code ####
        #Play the gameplay music
        pygame.mixer.music.load(
            path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        #pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
        # makes the gameplay sound in an endless loop
        pygame.mixer.music.play(-1)

        menu_display = False

        game_start_time = time.time()
        ########################


        ## group all the sprites together for ease of update
        all_sprites = pygame.sprite.Group()

        player1 = Player(Player1, 'blue')
        all_sprites.add(player1)
        players.append(player1)

        if(NUM_PLAYERS == 2):
            player2 = Player(Player2, 'red')
            all_sprites.add(player2)
            players.append(player2)

        ## spawn a group of mob
        mobs = pygame.sprite.Group()
        for i in range(meteor_count): 
            newmob()

        ## group for lasers
        lasers = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

    #1 Process input/events
    clock.tick(FPS)  # will make the loop run at the same speed all the time

    # gets all the events which have occured till now and keeps tab of them.
    events = pygame.event.get()
    for event in events:
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        ## Press ESC to exit game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # ## event for shooting the lasers
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         player1.shoot()      ## we have to define the shoot()  function

    #2 Update
    all_sprites.update()

    ## check if a laser hit a mob
    ## now we have a group of lasers and a group of mob
    hits = pygame.sprite.groupcollide(mobs, lasers, True, True)
    ## now as we delete the mob element when we hit one with a laser, we need to respawn them again
    ## as there will be no mob_elements left out
    for hit in hits:
        mob = hit
        laser = hits[hit][0]
        laser.player.add_to_score(50 - mob.radius)
        # player1.score += 50 - hit.radius  # give different scores for hitting big and small metoers
        random.choice(expl_sounds).play()
        # m = Mob()
        # all_sprites.add(m)
        # mobs.add(m)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()  # spawn a new mob

    ## ^^ the above loop will create the amount of mob objects which were killed spawn again
    #########################

    for player in players: 
        check_player_hit(player)

    #3 Draw/render
    screen.fill(BLACK)
    ## draw the stargaze.png image
    # screen.blit(background, background_rect)
    screen.blit(background_img, (0,0))

    all_sprites.draw(screen)

    # Display player stats over top everything else
    draw_player_stats(player1, 5, 0, 'topleft')

    if(NUM_PLAYERS == 2):
        draw_player_stats(player2, WIDTH - 100, 0, 'topleft')

    # draw game timer
    draw_text(screen, get_game_start_time(), 18, WIDTH / 2, 10)

    ## Done after drawing everything to the screen
    pygame.display.flip()


pygame.quit()
