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
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound
pygame.mouse.set_visible(False)

for mode in pygame.display.list_modes():
  print(mode)

