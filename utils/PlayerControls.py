import pygame

"""
Button Layout: 

blue  | yellow
--------------
green | red
"""
# Blue Player (left side, player 1)
P1_Controls = {
    "joystick": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,

        "blue": pygame.K_t,
        "yellow": pygame.K_y,
        "green": pygame.K_g,
        "red": pygame.K_h,
    },
    # Alternative keyboard keys (for testing)
    "keyboard": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,

        "blue": pygame.K_t,
        "yellow": pygame.K_y,
        "green": pygame.K_g,
        "red": pygame.K_h,
    }
}


# Red Player (right side, player 2)
P2_Controls = {
    "joystick": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,

        "blue": pygame.K_t,
        "yellow": pygame.K_y,
        "green": pygame.K_g,
        "red": pygame.K_h,
    },
    # Alternative keyboard keys (for testing)
    "keyboard": {
        "up": pygame.K_u,
        "down": pygame.K_k,
        "left": pygame.K_h,
        "right": pygame.K_k,

        "blue": pygame.K_o,
        "yellow": pygame.K_p,
        "green": pygame.K_l,
        "red": pygame.K_SEMICOLON,
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


"""  
Class representing the input controls for a player
"""
class PlayerControls:
    def __init__(self, player = 1):
        self.player = player

        if player == 1:
            # print("player 1 controls")
            self.joystick = P1_Controls["joystick"]
            self.keyboard = P1_Controls["keyboard"]
        elif player == 2: 
            # print("player 2 controls")
            self.joystick = P2_Controls["joystick"]
            self.keyboard = P2_Controls["keyboard"]
        else: 
            raise Exception(f'Invalid player number {player} must be either: 1 or 2')

    
    """
    Is a single players key pressed
    """
    def is_pressed(self, events, button):
        code = self.keyboard[button]
        match = [ e for e in events if e.type == pygame.KEYDOWN and e.key == code ]
        return len(match) > 0 

    def has_input(self, events):
        # TODO: check for joystick input here as well
        codes = self.keyboard.values()
        return [ e for e in events if e.type == pygame.KEYDOWN and e.key in codes ] 
    
    #def get_pressed_key_codes(events):
        #codes = self.keyboard.values()
        #return [ e for e in events if e.type == pygame.KEYDOWN e in values ] 

    """
    Get a dict of all the keys pressed by a player
    """
    def get_player_input(self, events):
        return { key:self.is_code_pressed(events, code) for key,code in self.keyboard.items() }

    """
    is_code_pressed
    """
    def is_code_pressed(self, events, code):
        match = [ e for e in events if e.type == pygame.KEYDOWN and e.key == code ]
        return len(match) > 0 

    """
    Get a binary representation of the buttons pressed
    """
    def binary_buttons(self, events):
        return 0
