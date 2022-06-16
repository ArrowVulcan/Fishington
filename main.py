import libs.actions as actions

#-------------------------#
#- Classes ---------------#
#-------------------------#

class Bot():
    
    def __init__(self):
        self.queue = []
        self.fishes = 0
        self.maxFishes = 6

    def start(self, cls=None):
        print("[Bot] Fishing bot started.")
        
        if cls:
            self.add_to_queue(cls)
        
        while self.queue:
            self.queue.pop(0)()(self)

        print("[Bot] Fishing bot ended.")

    def add_to_queue(self, cls):
        self.queue.append(cls)

class SellFishes():

    @staticmethod
    def __call__(bot):
        print("> Selling fishes.")
        actions.sell_fishes()
        bot.fishes = 0
        print(f"> Fish: {bot.fishes}/{bot.maxFishes}")
        bot.add_to_queue(FindWater)

class TossFishingrod():
    
    @staticmethod
    def __call__(bot):
        print("> Tossing the rod.")
        actions.toss_fishingrod()
        bot.add_to_queue(CheckForHook)

class CheckForHook():

    @staticmethod
    def __call__(bot):
        print("> Checking for hook.")
        actions.check_for_hook()
        bot.add_to_queue(ReelInFish)

class ReelInFish():
    
    @staticmethod
    def __call__(bot):
        print("> Reel in the fish.")
        success = actions.reel_in_fish()
        if not success:
            bot.add_to_queue(TossFishingrod)
        else:
            bot.fishes += 1
            print(f"> Fish: {bot.fishes}/{bot.maxFishes}")
            bot.add_to_queue(CloseCatchInfo)

class CloseCatchInfo():

    @staticmethod
    def __call__(bot):
        print("> Closing catch window.")
        actions.close_catch_info()
        if bot.fishes == bot.maxFishes:
            bot.add_to_queue(SellFishes)
        else:
            bot.add_to_queue(TossFishingrod)

class FindWater():

    @staticmethod
    def __call__(bot):
        print("> Finding water.")
        actions.find_water()
        bot.add_to_queue(TossFishingrod)

#-------------------------#
#- Main ------------------#
#-------------------------#

def main():
    bot = Bot()
    bot.start(FindWater)

if __name__ == "__main__":
    main()