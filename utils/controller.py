import time
import mouse
import random
import pydirectinput

#-------------------------#
#- Mouse -----------------#
#-------------------------#

def mouse_speed():
    return random.uniform(0.046, 0.094)

def click_speed():
    return random.uniform(0.08, 0.16)

def mouse_move(x, y, inc=0):
    mouse.move(x, y, True, mouse_speed() + inc)
    time.sleep(click_speed())

def mouse_click(delay=0):
    time.sleep(click_speed())
    mouse.press()
    time.sleep(click_speed() + delay)
    mouse.release()

def mouse_hold(hold=True):
    if hold:
        mouse.press()
    else:
        mouse.release()

#-------------------------#
#- Keyboard --------------#
#-------------------------#

def set_key(list, key, check):
    if check:
        check_key(list, check)

    if not check_key(list, key):
        list[key] = True
        pydirectinput.keyDown(key)

def check_key(list, key):
    if list[key]:
        list[key] = not list[key]
        pydirectinput.keyUp(key)
    else:
        return False

def clear_keys(list):
    for key in list:
        check_key(list, key)

if __name__ == "__main__":
    print("Run main.py file!")