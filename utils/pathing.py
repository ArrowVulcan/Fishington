import pydirectinput
import math
import cv2
import mss
import numpy
import os
import utils.controller as controller #type: ignore
from utils.image import image #type: ignore
import time

#-------------------------#
#- Functions -------------#
#-------------------------#

def template(name, bw=False):
    img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    return cv2.imread(os.path.join(img_path, name), (cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE)[bw] )

def getDistance(pos1, pos2):
    dist = math.sqrt( math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2) )
    hor = ("right", "left")[pos1[0] > pos2[0]]
    ver = ("down", "up")[pos1[1] > pos2[1]]
    return dist, hor, ver

def match_template(obj, img):
    imageHeight, imageWidth = img.shape # Get width and height of template image
    tmp = cv2.matchTemplate(obj, img, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(tmp)
    bottomRight = (int(maxLoc[0] + imageWidth), int(maxLoc[1] + imageHeight)) # Get the bottom right location
    center = ( int(maxLoc[0] + (imageWidth/2) ), int(maxLoc[1] + (imageHeight/2) ) )
    return [minVal, maxVal, minLoc, maxLoc, bottomRight, center]

def screen(bw=False):
    with mss.mss() as sct:
        scr = sct.grab({"left": 0, "top": 0, "width": 1920, "height": 1080}) # Capture screen / Screenshot

    image = numpy.array(scr)
    return cv2.cvtColor(image, (cv2.IMREAD_COLOR, cv2.COLOR_BGR2GRAY)[bw])

def move(location):

    shopFound = False
    reached = False

    keys = {
        "w": False,
        "a": False,
        "s": False,
        "d": False,
    }

    def check_key(key):
        if keys[key]:
            keys[key] = not keys[key]
            pydirectinput.keyUp(key)
        else:
            return False

    def set_key(key):
        if not check_key(key):
            keys[key] = True
            pydirectinput.keyDown(key)

    def key_walk(ver, hor):
        if ver == "down":
            check_key("w")
            set_key("s")
        else:
            check_key("s")
            set_key("w")

        if hor == "left":
            check_key("d")
            set_key("a")
        else:
            check_key("a")
            set_key("d")

    def clear_keys():
        check_key("w")
        check_key("a")
        check_key("s")
        check_key("d")

#-------------------------#
#- Main ------------------#
#-------------------------#

    lilypad = template("lilypad.jpg", True)
    fishes = template("fishes.jpg", True)
    shop = template("shop.jpg", True)

    while True:

        imgGray = screen(True)

        if location == "fish":

            matchVals = match_template(imgGray, lilypad)
            if matchVals[1] > 0.75:
                offset = -170
                #cv2.rectangle(imgGray, (matchVals[3][0], matchVals[3][1] + offset), (matchVals[4][0], matchVals[4][1] + offset), (0,0,255), 2)

                objX, objY = matchVals[5]
                #cv2.line(imgGray, (961, 607), (objX, objY+offset), (255, 0, 0), 5)
                dist, hor, ver = getDistance((961, 607), (objX, objY + offset))
                print(dist, hor, ver)
                
                if dist > 150 and not reached:
                    key_walk(ver, hor)
                else:
                    reached = True
                    clear_keys()
                    break

        elif location == "sell":

            matchVals = match_template(imgGray, fishes)
            if matchVals[1] > 0.75:
                offset = 190
                #cv2.rectangle(imgGray, (matchVals[3][0], matchVals[3][1] + offset), (matchVals[4][0], matchVals[4][1] + offset), (0,0,255), 2)

                objX, objY = matchVals[5]
                #cv2.line(imgGray, (961, 607), (objX, objY+offset), (255, 0, 0), 5)
                dist, hor, ver = getDistance((961, 607), (objX, objY + offset))
                print(dist, hor, ver)

                if dist > 150 and not reached:
                    key_walk(ver, hor)
                else:
                    reached = True
                    clear_keys()

                    time.sleep(1)

                    matchVals = match_template(imgGray, shop)
                    if matchVals[1] > 0.75:
                        shopFound = True
                        controller.mouse_move(matchVals[3][0], matchVals[3][1], 0.5)
                        controller.mouse_click()
                        time.sleep(1)
                        break

if __name__ == "__main__":
    print("Run main.py file!")