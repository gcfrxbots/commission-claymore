from Settings import *
from Initialize import *
# importing image object from PIL
import math
import datetime
from PIL import Image, ImageDraw



commands_CustomCommands = {
    "!ripandteartest": ('customcmds.startRipandtear', 'cmdArguments', 'user'),
}


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
        if (user != settings["TRIGGER USER"]) and (user != settings["CHANNEL"]):
            return
        self.startTime = datetime.datetime.now()
        self.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        self.isActive = True
        self.progress = 0
        self.drawBar()
        os.system("RunHotkey_BarScene.exe")
        chatConnection.sendMessage("Rip and Tear mode is active! Spam Kill in chat to make me kill!")

    def stopRipandtear(self):
        self.isActive = False
        self.startTime = None
        self.endTime = None
        self.progress = 0
        self.deleteBar()
        os.system("RunHotkey_NormalScene.exe")
        chatConnection.sendMessage("Rip and Tear is now over, please stop saying Kill in chat.")

    def kill(self):
        if self.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            self.killvalue = 500 / ((users)*(difficulty*.8))
            self.progress += self.killvalue
            print(self.progress)

            if self.progress >= 500:
                self.win()


    def win(self):
        chatConnection.sendMessage("RIP AND TEAR MODE ENGAGED!")
        self.isActive = False
        self.startTime = None
        self.endTime = None
        os.system("RunHotkey_RipAndTearScene.exe")
        time.sleep(5)
        self.progress = 0
        self.deleteBar()
        self.RaTisActive = True
        self.RaTstartTime = datetime.datetime.now()
        self.RaTendTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["RIP AND TEAR DURATION"])

    def returnToNormal(self):
        os.system("RunHotkey_NormalScene.exe")
        self.RaTisActive = False
        print("RaT DONE!")