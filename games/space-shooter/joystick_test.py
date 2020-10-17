# found online: 
# https://thecodezine.com/easy-learn-python-space-shooter-game-building-using-pygame/
import pygame
import time
from datetime import timedelta
from os import path
from PlayerControls import PlayerControls 

pygame.init()
screen = pygame.display.set_mode((500, 500))

Player1 = PlayerControls(1)
Player2 = PlayerControls(2)

running = True
menu_display = True
clock = pygame.time.Clock()
while running:

    clock.tick(30)  # will make the loop run at the same speed all the time

    #################### TEST HERE #################
    events = pygame.event.get()

    
    if Player1.has_input(events):
        print("Player 1:")
        print(Player1.get_player_input(events))

    if Player2.has_input(events):
        print("Player 2:")
        print(Player2.get_player_input(events))

    ################################################

    # Boilerplate for closing the game window
    for event in events:
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        ## Press ESC to exit game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        # ## event for shooting the bullets
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         print("space pressed")

    pygame.display.flip()

pygame.quit()
