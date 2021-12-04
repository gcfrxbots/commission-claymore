from Settings import *
from Initialize import *
# importing image object from PIL
import math
import sys
import ctypes
import shutil
import datetime
from obswebsocket import obsws, requests
from PIL import Image, ImageDraw



commands_CustomCommands = {
    "!ripandteartest": ('customcmds.startRipandtear', 'cmdArguments', 'user'),
}

def changeScene(sceneName):
    print("Switching...")
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()

    scenes = ws.call(requests.GetSceneList())
    names = []
    for s in scenes.getScenes():
        name = s['name']
        names.append(name)

    if sceneName not in names:
        print("Scene %s not found!" % sceneName)
        return

    print(u"Switching to {}".format(sceneName))
    ws.call(requests.SetCurrentScene(sceneName))

    ws.disconnect()


class bar:

    def __init__(self):
        self.progress = 0  # Out of 500, how full the bar is
        self.target = 0 # Out of 500, how full the bar should be
        self.imgname = "bar.gif"

    def drawBar(self, progress):
        self.progress = progress
        realProgress = 500 - round(self.progress)
        w, h = 50, 500
        shape = [(0, 500), (w, realProgress)]
        outlineShape = [(0, 0), (w - 1, h - 1)]

        # creating new Image object
        img = Image.new("RGBA", (w, h), (0, 255, 0, 0))

        # create rectangle image
        draw = ImageDraw.Draw(img)

        draw.rectangle(shape, fill="red")
        draw.rectangle(outlineShape, width=4, outline="black")
        return img

    def freezeImage(self):
        img = self.drawBar(self.progress)
        img.save(self.imgname)

    def find_duration(self, img_obj):
        img_obj.seek(0)  # move to the start of the gif, frame 0
        tot_duration = 0
        # run a while loop to loop through the frames
        while True:
            try:
                frame_duration = img_obj.info['duration']  # returns current frame duration in milli sec.
                tot_duration += frame_duration
                # now move to the next frame of the gif
                img_obj.seek(img_obj.tell() + 1)  # image.tell() = current frame
            except EOFError:
                return (tot_duration / 1000) - 0.9  # returns total duration in s

    def generateGif(self, target):
        self.target = target
        # target is out of 500 like Progress above

        # Create the frames
        frames = []

        difference = abs(self.target - self.progress)
        cycles = round((difference / 5) + 55)

        if self.target > self.progress:
            # POSITIVES
            for i in range(cycles):
                new_frame = self.drawBar(self.progress)
                frames.append(new_frame)
                if self.progress < self.target:
                    self.progress += 5
        else:
            # NEGATIVES
            for i in range(cycles):
                new_frame = self.drawBar(self.progress)
                frames.append(new_frame)
                if self.progress > self.target:
                    self.progress -= 5

        # Save into a GIF file
        frames[0].save(self.imgname, format='GIF',
                       append_images=frames[1:], save_all=True, duration=30, loop=0)

        timeToDelay = self.find_duration(Image.open(self.imgname))
        timeToDelay = round(timeToDelay, 1)
        if timeToDelay < 0.2:
            timeToDelay = 0.2
        time.sleep(timeToDelay)
        self.freezeImage()
        time.sleep(0.3)

drawBar = bar()

class CustomCommands():
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.isActive = False
        self.progress = 0.0  # PROGRESS OUT OF 500
        self.drainrate = settings["DRAIN RATE"]
        self.deleteBar()
        self.killvalue = 2
        self.triggerMsg = settings["TRIGGER MESSAGE"]
        self.RaTstartTime = None
        self.RaTendTime = None
        self.RaTisActive = False

    def deleteBar(self):
        w, h = 50, 500
        # creating new Image object
        img = Image.new("RGBA", (w, h), (255, 0, 0, 0))
        img.save("bar.png")
        shutil.copyfile("./Resources/emptybar.png", "barglow.png")

    def startRipandtear(self, args, user):
        if self.isActive:
            return
        if (user.lower() != settings["TRIGGER USER"].lower()) and (user != settings["CHANNEL"]):
            return
        changeScene(settings["INSTRUCTION SCENE"])
        time.sleep(settings["INSTRUCTION DURATION"])
        self.actuallyStartRipandtear()

    def actuallyStartRipandtear(self):
        self.startTime = datetime.datetime.now()
        self.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        self.isActive = True
        self.progress = 0
        drawBar.generateGif(0)
        shutil.copyfile("./Resources/barglow.png", "barglow.png")
        changeScene(settings["BAR SCENE"])
        chatConnection.sendMessage("Rip and Tear mode is active! Spam Kill in chat to make me kill!")

    def stopRipandtear(self):
        self.isActive = False
        self.startTime = None
        self.endTime = None
        self.progress = 0
        self.deleteBar()
        changeScene(settings["NORMAL SCENE"])
        chatConnection.sendMessage("Rip and Tear is now over, please stop saying Kill in chat.")

    def kill(self):
        if self.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            self.killvalue = 500 / ((users)*(difficulty*.8))
            self.progress += self.killvalue
            print(self.progress)

    def win(self):
        chatConnection.sendMessage("RIP AND TEAR MODE ENGAGED!")
        self.isActive = False
        self.startTime = None
        self.endTime = None
        self.deleteBar()
        changeScene(settings["RIP AND TEAR SCENE"])
        self.progress = 0
        self.RaTisActive = True
        self.RaTstartTime = datetime.datetime.now()
        self.RaTendTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["RIP AND TEAR DURATION"])

    def lose(self):
        chatConnection.sendMessage("Rip and tear failed...")
        changeScene(settings["FAIL SCENE"])
        self.isActive = False
        self.startTime = None
        self.endTime = None
        self.deleteBar()
        self.progress = 0
        time.sleep(settings["FAIL DURATION"])
        self.returnToNormal()

    def returnToNormal(self):
        changeScene(settings["NORMAL SCENE"])
        self.RaTisActive = False
        print("RaT DONE!")