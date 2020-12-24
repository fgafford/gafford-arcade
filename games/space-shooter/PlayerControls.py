import pygame

"""
Button Layout: 

blue  | yellow
-------------- green | red
"""
# Blue Player (left side, player 1)
P1_Controls = {
    "joystick": {
        "up": "1-",
        "down": "1+",
        "left": "0-",
        "right": "0+",

        "blue": 3,
        "yellow": 1,
        "green": 2,
        "red": 0,

        "1Player": 8,
        "2Player": 7,
    },
    # Alternative keyboard keys (for testing)
    "keyboard": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,

        "blue": pygame.K_r,
        "yellow": pygame.K_t,
        "green": pygame.K_f,
        "red": pygame.K_g,

        "1Player": pygame.K_1,
        "2Player": pygame.K_2,
     }
}


# Red Player (right side, player 2)
P2_Controls = {
    "joystick": {
        "up": "1-",
        "down": "1+",
        "left": "0-",
        "right": "0+",

        "blue": 0,
        "yellow": 3,
        "green": 1,
        "red": 2
    },
    # Alternative keyboard keys (for testing)
    "keyboard": {
        "up": pygame.K_u,
        "down": pygame.K_j,
        "left": pygame.K_h,
        "right": pygame.K_k,

        "blue": pygame.K_o,
        "yellow": pygame.K_p,
        "green": pygame.K_l,
        "red": pygame.K_SEMICOLON
    }
}


buttons = [
    "up",
    "down",
    "left",
    "right",

    "blue",
    "yellow",
    "green",
    "red"
]

########## Helper function #############
def get_keyboard_input(game): 
    return game.key.get_pressed()
########################################

"""  
Class representing the input controls for a player
"""
class PlayerControls:
    def __init__(self, player = 1):
        pygame.joystick.init()
        self.player = player

        self.joysticks_present = pygame.joystick.get_count() > 0

        if player == 1:
            # Player 1 actually has the 2nd joystick for input
            self.keyboard_controls = P1_Controls["keyboard"]
            self.joystick_controls = P1_Controls["joystick"]
            if self.joysticks_present:
                self.joystick = pygame.joystick.Joystick(1)

        elif player == 2: 
            # Player 1 actually has the 2nd joystick for input
            self.keyboard_controls = P2_Controls["keyboard"]
            self.joystick_controls = P2_Controls["joystick"]
            if self.joysticks_present:
                self.joystick = pygame.joystick.Joystick(0)
        else: 
            raise Exception(f'Invalid player number {player} must be either: 1 or 2')

        if self.joysticks_present:
            self.joystick.init()

    def get_player_number(self):
        return self.player
    
    """
    Is a single players key pressed
    """
    def is_joystick_pressed(self, button):
        return self.joystick.get_button(button)

    def is_keyboard_pressed(self, game, button):
        code = self.keyboard_controls[button]
        k_input = get_keyboard_input(game)
        return k_input[code]

    def is_pressed(self, game, button):
        return self.is_joystick_pressed(button) or \
                self.is_keyboard_pressed(game, button)

    def has_input(self, game):
        return (hasattr(self, 'joystick') and self.has_joystick_input(game)) or self.has_keyboard_input(game)

    def has_joystick_input(self, game):
        buttons = [ i  for i in range(self.joystick.get_numbuttons()) if self.joystick.get_button(i) == True ]
        if len(buttons) > 0:
            return True
        else:
            axes = self.get_joystick_udlf()
            for i in axes:
                if i == True:
                   return True
            return False

        buttons = [ i  for i in range(self.joystick.get_numbuttons()) if self.joystick.get_button(i) == True ]

    def has_keyboard_input(self, game):
        codes = self.keyboard_controls.values()
        k_input = get_keyboard_input(game)
        presses = [ c for c in codes if k_input[c] ]
        return len(presses) > 0 

    """
    get an array version of the pressed keys (1s and 0s)
    following format:
    index : key 
    0 : up
    1 : down
    2 : left
    3 : right
    4 : blue
    5 : yellow
    6 : green 
    7 : read
    8 : 1Player (only for 1st player)
    9 : 2Player (only for 1st player)
    """
    def get_pressed_joystick_as_array(self):
        udlf = self.get_joystick_udlf()
        buttons = self.get_pressed_color_joystick_buttons()
        player_buttons = self.get_pressed_player_joystick_buttons()
        return udlf + buttons + player_buttons

    """
    Get a dict of all the joystick keys pressed by a player
    """
    def get_pressed_joystick_keys(self):
        if not self.joysticks_present:
            return { button:False for button in self.joystick_controls.keys() }

        j_input = self.get_pressed_joystick_as_array()
        return { button:j_input[i] for i,button in enumerate(self.joystick_controls) }
    
    def get_pressed_color_joystick_buttons(self):
        if not self.joysticks_present:
            return [False,False,False,False]
        buttons = [ self.joystick.get_button(b) for b in range(self.joystick.get_numbuttons()) ]
        return [ buttons[self.joystick_controls['blue']], \
                 buttons[self.joystick_controls['yellow']], \
                 buttons[self.joystick_controls['green']], \
                 buttons[self.joystick_controls['red']] ] 

    def get_pressed_player_joystick_buttons(self):
        if not self.joysticks_present:
            return [False, False]
        if '1Player' not in self.joystick_controls:
            return [False, False]
        buttons = [ self.joystick.get_button(b) for b in range(self.joystick.get_numbuttons()) ]
        return [ buttons[self.joystick_controls['1Player']], \
                 buttons[self.joystick_controls['2Player']] ] 

    """
    get_joystick_udlf

    get the udlf (up,down,left,right) joystick positions 
    """
    def get_joystick_udlf(self):
        # get the config (0-)
        if not self.joysticks_present:
            return [False,False,False,False]
        config = list(self.joystick_controls.values())[0:4]
        return [ self.get_joystick_axis_pressed(c[0], c[1]) for c in config ]  

    """
    Given an axix (eg. 0,1,2) and a direction (above or below 0) (eg. "-" or "+")
    determin if the axis is enguaged
    """
    def get_joystick_axis_pressed(self, axis, dir):
        value = self.joystick.get_axis(int(axis))
        if dir == "-":
            return value < 0
        elif dir == "+":
            return value > 0
        else:
            # Bad input here.... so its a False
            return False


    """
    Get a dict of all the keyboard keys pressed by a player
    """
    def get_pressed_keyboard_keys(self, game):
        k_input = get_keyboard_input(game)
        return { key:k_input[code] for key,code in self.keyboard_controls.items() }

    """
    Get all input for the player
    """
    def get_input(self, game):
        # TODL: ned to check hoystick or keyboard andmerge dics here
        if not self.joysticks_present: 
           return self.get_pressed_keyboard_keys(game)

        return self.get_pressed_joystick_keys()

    """
    is_code_pressed
    """
    def is_code_pressed(self, game, code):
        k_input = get_keyboard_input(game)
        return k_input[code]

    """
    Get a binary representation of the buttons pressed
    """
    def binary_buttons(self, game):
        return 0
