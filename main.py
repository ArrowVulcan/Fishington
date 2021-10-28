import time
import random
from utils.image import image #type: ignore
import utils.controller as controller #type: ignore
import utils.pathing as pathing #type: ignore

#-------------------------#
#- Classes ---------------#
#-------------------------#

class FSM():
    
    def __init__(self):
        self.queue = []
        self.fishes = 0
        self.maxFishes = 6

    def start(self, cls=None):
        print("[FSM] Fishing bot started.")
        
        if cls:
            self.add_to_queue(cls)
        
        while self.queue:
            self.queue.pop(0)()(self)

        print("[FSM] Fishing bot ended.")

    def add_to_queue(self, cls):
        self.queue.append(cls)

class SellFishes():

    @staticmethod
    def __call__(fsm):
        print("> Selling fishes.")

        pathing.move("sell")
        
        delay = 0.2
        movements = [(460, 325), (962, 939), (1102, 791), (1765, 723)]
        zones = [(441, 305), (1097, 950), (1162, 814)]
        colors = [(255, 255, 255), (51, 41, 0), (137, 214, 255)]
        
        for ind, move in enumerate(movements):
            
            done_step = False

            while done_step == False:

                if ind < 3:
                    done_step = image.check_steps(ind, zones, colors)
                    time.sleep(0.4)
                
                if done_step == True:
                    break

                controller.mouse_move(move[0], move[1], delay)
                time.sleep(0.4)
                controller.mouse_click()
                time.sleep(0.4)

                if ind == 3:
                    break

        time.sleep(1)

        fsm.fishes = 0
        fsm.add_to_queue(FindWater)

class CheckBasket():

    @staticmethod
    def __call__(fsm):
        print("> Checking basket.")

        #newImage = image(1670, 965, 30, 25)
        #newImage.track_basket()
        #newImage.match_template()
        #basket = newImage.check_fishbasket(-0.13)

        #if basket:
        #    fsm.add_to_queue(SellFishes)
        #else:
        #    fsm.add_to_queue(FindWater)

        fsm.add_to_queue(SellFishes)

class TossFishingrod():
    
    @staticmethod
    def __call__(fsm):
        print("> Tossing the rod.")

        horizontal_spread = random.randint(-100, 100)
        vertical_spread = random.randint(-100, 100)
        strength = random.uniform(0.5, 1.0)

        controller.mouse_move(960 + horizontal_spread, 850 + vertical_spread)
        controller.mouse_click(strength)

        fsm.add_to_queue(CheckForHook)

class CheckForHook():

    @staticmethod
    def __call__(fsm):
        print("> Checking for hook.")

        while True:

            newImage = image(933, 429, 42, 64)
            newImage.set_template("hooked.jpg")
            newImage.match_template()
            #newImage.draw_rectangle(0.6, (255, 0, 0), 3)

            if newImage.maxVal >= 0.6:
                hook_speed = random.uniform(0.15, 0.45)
                time.sleep(hook_speed)
                controller.mouse_click()
                fsm.add_to_queue(ReelInFish)
                break

class ReelInFish():
    
    @staticmethod
    def __call__(fsm):
        print("> Reel in the fish.")

        baitFound = False
        left_padding = 60
        right_padding = 580
        middle_point = 309

        while True:

            newImage = image(634, 860, 619, 36)
            newImage.set_template("bait.jpg")
            newImage.match_template()

            newImage.lastFound = "START"

            if newImage.find_zone(106, 17): # 136
                newImage.lastFound = "START"
            elif newImage.find_zone(309, 17):
                newImage.lastFound = "CENTER"
            elif newImage.find_zone(513, 17): #483
                newImage.lastFound = "END"

            if newImage.maxVal >= 0.8:
                baitFound = True
                if (newImage.lastFound == "START") and newImage.maxLoc[0] > left_padding:
                    controller.mouse_hold(False)
                elif (newImage.lastFound == "START") and newImage.maxLoc[0] < left_padding:
                    controller.mouse_hold(True)
                elif (newImage.lastFound == "END") and newImage.maxLoc[0] < right_padding:
                    controller.mouse_hold(True)
                elif (newImage.lastFound == "END") and newImage.maxLoc[0] > right_padding:
                    controller.mouse_hold(False)
                elif (newImage.lastFound == "CENTER") and newImage.maxLoc[0] >= middle_point:
                    controller.mouse_hold(False)
                elif (newImage.lastFound == "CENTER") and newImage.maxLoc[0] <= middle_point:
                    controller.mouse_hold(True)
            elif baitFound:
                controller.mouse_hold(False)
                time.sleep(2)
                newImage2 = image(1180, 673, 65, 60)
                newImage2.set_template("x.jpg")
                newImage2.match_template()

                if newImage2.maxVal >= 0.8:
                    fsm.fishes += 1
                    fsm.add_to_queue(CloseCatchInfo)
                    break
                else:
                    print("Failed to catch!")
                    time.sleep(1)
                    fsm.add_to_queue(TossFishingrod)
                    break

class CloseCatchInfo():

    @staticmethod
    def __call__(fsm):
        print("> Closing catch window.")

        isFound = False
        isClosed = False

        while True:

            newImage = image(1180, 673, 65, 60)
            newImage.set_template("x.jpg")
            newImage.match_template()

            if newImage.maxVal >= 0.8:
                isFound = True
                time.sleep(1)
                controller.mouse_move(1190, 705)
                time.sleep(1)
                controller.mouse_click(0.5)
                time.sleep(1)
                isClosed = True
            else:
                isFound = False
            
            if not isFound and isClosed:
                if fsm.fishes >= fsm.maxFishes:
                    fsm.add_to_queue(SellFishes)
                else:
                    fsm.add_to_queue(TossFishingrod)
                break

class FindWater():

    @staticmethod
    def __call__(fsm):
        print("> Finding water.")

        pathing.move("fish")
        fsm.add_to_queue(TossFishingrod)

#-------------------------#
#- Main ------------------#
#-------------------------#

def main():
    fsm = FSM()
    fsm.start(FindWater)

if __name__ == "__main__":
    main()