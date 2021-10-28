import os
import cv2
import mss
import numpy
import ctypes

screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

class image:

    def __init__(self, left=0, top=0, width=screensize[0], height=screensize[1], color=True):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color

        with mss.mss() as sct:
            self.screen = sct.grab({"left": self.left, "top": self.top, "width": self.width, "height": self.height}) # Capture screen / Screenshot
            #self.screenFull = sct.grab({"left": 0, "top": 0, "width": screensize[0], "height": screensize[1]}) # Capture screen / Screenshot (Full size)

        self.image = numpy.array(self.screen)
        #self.imageFull = numpy.array(self.screenFull)
        #self.imageFull = self.imageFull[:-self.height]
        self.grayImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # Creat a grayscale version of the image
        #self.grayImageFull = cv2.cvtColor(self.imageFull, cv2.COLOR_BGR2GRAY) # Creat a grayscale version of the full image

    def set_template(self, name):
        #print( os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images') )
        img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        self.template = cv2.imread(os.path.join(img_path, name), cv2.IMREAD_GRAYSCALE )

    def set_template2(self, name, bw=False):
        img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        self.template = cv2.imread(os.path.join(img_path, name), (cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE)[bw] )
        return self.template

    def track_basket(self):
        with mss.mss() as sct:
            grab = sct.grab({"left": 1704, "top": 967, "width": 30, "height": 20})
        self.template = numpy.array(grab)
        self.template = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("template", self.template)
        #cv2.resizeWindow('template', 200, 200)

    def match_template(self):
        self.imageHeight, self.imageWidth = self.template.shape # Get width and height of template image
        self.match = cv2.matchTemplate(self.grayImage, self.template, cv2.TM_CCOEFF_NORMED)
        #self.matchFull = cv2.matchTemplate(self.grayImageFull, self.template, cv2.TM_CCOEFF_NORMED)
        self.minVal, self.maxVal, self.minLoc, self.maxLoc = cv2.minMaxLoc(self.match)
        #self.minValFull, self.maxValFull, self.minLocFull, self.maxLocFull = cv2.minMaxLoc(self.matchFull)
        self.bottomRight = (int(self.maxLoc[0] + self.imageWidth), int(self.maxLoc[1] + self.imageHeight)) # Get the bottom right location
        self.center = ( int(self.maxLoc[0] + (self.imageWidth/2) ), int(self.maxLoc[1] + (self.imageHeight/2) ) )

    def match_template2(self, obj, img):
        imageHeight, imageWidth = img.shape # Get width and height of template image
        tmp = cv2.matchTemplate(obj, img, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(tmp)
        bottomRight = (int(maxLoc[0] + imageWidth), int(maxLoc[1] + imageHeight)) # Get the bottom right location
        center = ( int(maxLoc[0] + (imageWidth/2) ), int(maxLoc[1] + (imageHeight/2) ) )
        return [minVal, maxVal, minLoc, maxLoc, bottomRight, center]

    def BGR_to_RGB(self, color):
        color = list(color) # Convert tuple to list
        convertColor = color[-1], color[1], color[0] # Shift first and last value (from BGR to RGB)
        color = tuple(convertColor) # Convert it back to a tuple
        return color

    #def get_match_position(self):
    #    return ( self.maxLocFull[0] + int(self.imageWidth/2), self.maxLocFull[1] + int(self.imageHeight/2) ) # Get center-point location of the matched image.

    def check_fishbasket(self, threshold=0.9):
        self.threshold = threshold
        #print( self.maxVal, self.threshold )
        return (self.maxVal <= self.threshold) # Check if the accuracy value is over the threshold

    def find_zone(self, x, y, **color):
        imgZone = self.image[y, x]
        #print( (imgZone[0], color["color"][2], imgZone[1], color["color"][1], imgZone[2], color["color"][0]) )
        if color:
            return (imgZone[0] == color["color"][2] and imgZone[1] == color["color"][1] and imgZone[2] == color["color"][0])
        else:
            return (imgZone[0] == 79 and imgZone[1] == 207 and imgZone[2] == 23) or (imgZone[0] == 50 and imgZone[1] == 74 and imgZone[2] == 206)

    def draw_rectangle(self, threshold=0.9, color=(0,0,255), width=2):
        self.threshold = threshold
        #print( self.maxVal, self.threshold )
        color = self.BGR_to_RGB(color) # Convert BGR to RGB
        if self.maxVal <= self.threshold: # Check if the accuracy value is over the threshold
            cv2.rectangle((self.grayImage, self.image)[self.color], self.maxLoc, self.bottomRight, color, width)

    def make_window(self, title="Wnd"):
        cv2.imshow(title, (self.grayImage, self.image)[self.color])
        #cv2.resizeWindow(title, 200, 200)

    @staticmethod
    def check_steps(step, zones, colors):
        img = image(color=True)
        return img.find_zone(zones[step][0], zones[step][1], color=colors[step])

if __name__ == "__main__":
    print("Run main.py file!")