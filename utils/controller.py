import time
import mouse
import random

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

if __name__ == "__main__":
    print("Run main.py file!")