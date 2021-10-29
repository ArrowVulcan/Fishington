import time
import math
import utils.controller as controller #type: ignore
from utils.image import image #type: ignore

#-------------------------#
#- Functions -------------#
#-------------------------#

def getDistance(pos1, pos2):
    dist = math.sqrt( math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2) )
    hor = ("right", "left")[pos1[0] > pos2[0]]
    ver = ("down", "up")[pos1[1] > pos2[1]]
    return dist, hor, ver

def move(location):

    reached = False

    keys = {
        "w": False,
        "a": False,
        "s": False,
        "d": False,
    }

    def key_walk(ver, hor):
        if ver == "down":
            controller.set_key(keys, "s", "w")
        else:
            controller.set_key(keys, "w", "s")

        if hor == "left":
            controller.set_key(keys, "a", "d")
        else:
            controller.set_key(keys, "d", "a")

#-------------------------#
#- Main ------------------#
#-------------------------#

    img = image(color=False)
    lilypad = img.set_template2("lilypad.jpg", True)
    fishes = img.set_template2("fishes.jpg", True)
    shop = img.set_template2("shop.jpg", True)

    while True:

        img = image(color=False)
        imgGray = img.grayImage

        if location == "fish":

            matchVals = img.match_template2(imgGray, lilypad)
            if matchVals[1] > 0.75:
                offset = -170
                #cv2.rectangle(imgGray, (matchVals[3][0], matchVals[3][1] + offset), (matchVals[4][0], matchVals[4][1] + offset), (0,0,255), 2)

                objX, objY = matchVals[5]
                #cv2.line(imgGray, (961, 607), (objX, objY+offset), (255, 0, 0), 5)
                dist, hor, ver = getDistance((961, 607), (objX, objY + offset))
                #print(dist, hor, ver)
                
                if dist > 150 and not reached:
                    key_walk(ver, hor)
                else:
                    reached = True
                    controller.clear_keys(keys)
                    break

        elif location == "sell":

            matchVals = img.match_template2(imgGray, fishes)
            if matchVals[1] > 0.75:
                offset = 190
                #cv2.rectangle(imgGray, (matchVals[3][0], matchVals[3][1] + offset), (matchVals[4][0], matchVals[4][1] + offset), (0,0,255), 2)

                objX, objY = matchVals[5]
                #cv2.line(imgGray, (961, 607), (objX, objY+offset), (255, 0, 0), 5)
                dist, hor, ver = getDistance((961, 607), (objX, objY + offset))
                #print(dist, hor, ver)

                if dist > 150 and not reached:
                    key_walk(ver, hor)
                else:
                    reached = True
                    controller.clear_keys(keys)

                    time.sleep(1)

                    img = image(color=False)
                    imgGray = img.grayImage

                    matchVals = img.match_template2(imgGray, fishes)
                    if matchVals[1] > 0.75:
                        controller.mouse_move(matchVals[3][0], matchVals[3][1], 0.5)
                        controller.mouse_click()
                        time.sleep(1)
                        break

if __name__ == "__main__":
    print("Run main.py file!")