from Settings import *
from Initialize import *
# importing image object from PIL
import math
import sys
import ctypes
import datetime
from obswebsocket import obsws, requests
from PIL import Image, ImageDraw



commands_CustomCommands = {
    "!ripandteartest": ('customcmds.startRipandtear', 'cmdArguments', 'user'),
    "!test": ('customcmds.startTest', 'cmdArguments', 'user'),
}

def changeScene(sceneName):
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
        exit()

    print(u"Switching to {}".format(sceneName))
    ws.call(requests.SetCurrentScene(sceneName))

    ws.disconnect()


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

    def drawBar(self):

        realProgress = 500 - round(self.progress)
        w, h = 50, 500
        shape = [(0, 500), (w, realProgress)]
        outlineShape = [(0, 0), (w-1, h-1)]

        # creating new Image object
        img = Image.new("RGBA", (w, h), (255, 0, 0, 0))

        # create rectangle image
        img1 = ImageDraw.Draw(img)

        img1.rectangle(shape, fill=settings["FILL COLOR"])
        img1.rectangle(outlineShape, width=4, outline="black")
        img.save("bar.png")

    def deleteBar(self):
        w, h = 50, 500
        # creating new Image object
        img = Image.new("RGBA", (w, h), (255, 0, 0, 0))
        img.save("bar.png")

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
        self.drawBar()
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
        self.isActive = False
        self.startTime = None
        self.endTime = None
        self.deleteBar()
        changeScene(settings["FAIL SCENE"])
        self.progress = 0
        time.sleep(settings["FAIL DURATION"])
        self.returnToNormal()

    def returnToNormal(self):
        changeScene(settings["NORMAL SCENE"])
        self.RaTisActive = False
        print("RaT DONE!")