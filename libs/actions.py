import os
import cv2
import mss
import numpy
import ctypes
import math
import time
import random
from pynput import mouse, keyboard

PLAYER_POSITION = (961, 607)
SCREEN_SIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

#-------------------------#
#- Mouse -----------------#
#-------------------------#

mouse_controller = mouse.Controller()

def mouse_speed():
    return random.uniform(0.046, 0.094)

def click_speed():
    return random.uniform(0.08, 0.16)

def mouse_move(pos):
    time.sleep(mouse_speed())
    mouse_controller.position = (pos[0], pos[1])

def mouse_click(count=1, delay=0):
    time.sleep(click_speed())
    mouse_controller.press(mouse.Button.left)
    time.sleep(click_speed() + delay)
    mouse_controller.release(mouse.Button.left)

def mouse_hold(hold=True):
    if hold:
        mouse_controller.press(mouse.Button.left)
    else:
        mouse_controller.release(mouse.Button.left)

#-------------------------#
#- Keyboard --------------#
#-------------------------#

keyboard_controller = keyboard.Controller()

key_list = {
    "w": False,
    "a": False,
    "s": False,
    "d": False,
    "space": False
}

def set_key(key, check):
    if check:
        check_key(check)

    if not check_key(key):
        key_list[key] = True

        if key == "space":
            keyboard_controller.press(keyboard.Key.space)
        else:
            keyboard_controller.press(key)

def check_key(key):
    if key_list[key]:
        key_list[key] = not key_list[key]

        if key == "space":
            keyboard_controller.release(keyboard.Key.space)
        else:
            keyboard_controller.release(key)
    else:
        return False

def clear_keys():
    for key in key_list:
        check_key(key)

def key_walk(ver, hor):

    if ver == "down":
        set_key("s", "w")
    else:
        set_key("w", "s")

    if hor == "left":
        set_key("a", "d")
    else:
        set_key("d", "a")

#-------------------------#
#- Classes ---------------#
#-------------------------#

class ScreenCapture():
    
    def __init__(self, left=0, top=0, width=SCREEN_SIZE[0], height=SCREEN_SIZE[1], color=True):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color

        with mss.mss() as sct:
            self.image = sct.grab({"left": self.left, "top": self.top, "width": self.width, "height": self.height})
        self.image = numpy.array(self.image)
        
        if not color:
            self.original = self.image.copy()
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

#-------------------------#
#- Functions -------------#
#-------------------------#

def template_matching(capture, template):
    
    if len(template.shape) == 3:
        image_height, image_width, _ = template.shape
    else:
        image_height, image_width = template.shape
    
    result = cv2.matchTemplate(capture, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    center = ( int(max_loc[0] + (image_width/2) ), int(max_loc[1] + (image_height/2) ) )
    start_point = max_loc
    end_point = (max_loc[0] + image_width, max_loc[1] + image_height)

    positions = {
        "start": start_point,
        "end": end_point,
        "center": center
    }

    return (max_val, positions)

def load_image(name, color=True):
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    return cv2.imread(os.path.join(image_path, name), (cv2.IMREAD_GRAYSCALE, cv2.IMREAD_COLOR)[color])

def getDistance(pos1, pos2):
    dist = math.sqrt( math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2) )
    hor = ("right", "left")[pos1[0] > pos2[0]]
    ver = ("down", "up")[pos1[1] > pos2[1]]
    return dist, hor, ver

def find_zone(image, x, y, **color):

    if color:
        return (image[y, x][0] == color["color"][2] and image[y, x][1] == color["color"][1] and image[y, x][2] == color["color"][0])
    else:
        return (image[y, x][0] == 79 and image[y, x][1] == 207 and image[y, x][2] == 23) or (image[y, x][0] == 50 and image[y, x][1] == 74 and image[y, x][2] == 206)

def find_water():

    capture = ScreenCapture(color=False)
    lilypad = load_image("lilypad.jpg", False)
    offset = -170

    while True:

        capture = ScreenCapture(color=False)

        threshold, positions = template_matching(capture.image, lilypad)

        if threshold >= 0.8:

            center_position_with_offset = (positions["center"][0], positions["center"][1] + offset)

            dist, hor, ver = getDistance(PLAYER_POSITION, center_position_with_offset)

            if dist > 150:
                key_walk(ver, hor)
            else:
                clear_keys()
                break

def toss_fishingrod():
    horizontal_spread = random.randint(-100, 100)
    vertical_spread = random.randint(-100, 100)
    strength = random.uniform(0.5, 1.0)

    mouse_move((960 + horizontal_spread, 850 + vertical_spread))
    mouse_click(delay=strength)

def check_for_hook():
    
    capture = ScreenCapture(820, 325, 240, 200, color=False)
    
    hook = load_image("hooked.jpg", False)
    
    while True:

        capture = ScreenCapture(820, 325, 240, 200, color=False)

        threshold, positions = template_matching(capture.image, hook)

        if threshold >= 0.6:

            hook_speed = random.uniform(0.15, 0.45)
            time.sleep(hook_speed)
            mouse_click()
            break

def reel_in_fish():

    bait_found = False
    left_padding = 145
    middle_point = 365
    right_padding = 585

    capture = ScreenCapture(600, 740, 730, 160, color=False)
    bait = load_image("bait.jpg", False)

    while True:

        capture = ScreenCapture(600, 740, 730, 160, color=False)

        threshold, positions = template_matching(capture.image, bait)

        last_found = "center"

        if find_zone(capture.original, left_padding, 144):
            last_found = "start"
        elif find_zone(capture.original, middle_point, 144):
            last_found = "center"
        elif find_zone(capture.original, right_padding, 144):
            last_found = "end"

        if threshold >= 0.8:
            bait_found = True

            if last_found == "start" and positions["start"][0] > left_padding:
                mouse_hold(False)
            elif last_found == "start" and positions["start"][0] < left_padding:
                mouse_hold(True)
            elif last_found == "end" and positions["start"][0] < right_padding:
                mouse_hold(True)
            elif last_found == "end" and positions["start"][0] > right_padding:
                mouse_hold(False)
            elif last_found == "center" and positions["start"][0] >= middle_point:
                mouse_hold(False)
            elif last_found == "center" and positions["start"][0] <= middle_point:
                mouse_hold(True)

        elif bait_found:
            mouse_hold(False)
            time.sleep(2)
            capture = ScreenCapture(1120, 600, 180, 200, color=False)
            close = load_image("x.jpg", False)

            threshold, positions = template_matching(capture.image, close)

            if threshold >= 0.8:
                return True
            else:
                return False

def close_catch_info():

    capture = ScreenCapture(1120, 600, 180, 200, color=False)
    close = load_image("x.jpg", False)

    is_found = False
    is_closed = False

    while True:

        capture = ScreenCapture(1120, 600, 180, 200, color=False)

        threshold, positions = template_matching(capture.image, close)

        if threshold >= 0.8:
            is_found = True

            capture = ScreenCapture(color=False)

            threshold, positions = template_matching(capture.image, close)

            time.sleep(1)
            mouse_move(positions["center"])
            time.sleep(1)
            mouse_click(delay=0.5)
            time.sleep(1)
            is_closed = True
        else:
            is_found = False

        if not is_found and is_closed:
            break

def sell_fishes():

    capture = ScreenCapture(color=False)
    fishes = load_image("fishes.jpg", False)
    shop = load_image("shop.jpg", False)

    reached = False

    while True:

        capture = ScreenCapture(color=False)

        threshold, positions = template_matching(capture.image, fishes)

        if threshold >= 0.75:
            offset = 190
            objX, objY = positions["center"]
            dist, hor, ver = getDistance((961, 607), (objX, objY + offset))
            
            #print(dist, hor, ver)

            if dist > 150 and not reached:
                key_walk(ver, hor)
            else:
                reached = True
                clear_keys()

                time.sleep(1)

                threshold, positions = template_matching(capture.image, shop)

                if threshold >= 0.75:
                    set_key("space", "space")
                    clear_keys()
                    time.sleep(1)

                    movements = [(470, 349), (962, 939), (1102, 811), (1765, 723)]
                    for move in movements:
                        mouse_move(move)
                        time.sleep(0.4)
                        mouse_click(delay=0.5)

                    time.sleep(1)
                    break

if __name__ == "__main__":
    print("Run main.py file!")