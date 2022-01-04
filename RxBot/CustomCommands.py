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
    "!ripandteartest": ('RIPANDTEAR.start', 'cmdArguments', 'user'),
    "!inspiretest": ('INSPIRE.start', 'cmdArguments', 'user'),
    "!cheertest": ('CHEER.start', 'cmdArguments', 'user'),
    "!legendtest": ('LEGENDARY.start', 'cmdArguments', 'user'),
}


def showScene(sceneName):
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()

    scenes = ws.call(requests.GetSceneList())
    print(scenes)
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


def showSource(sourceName):
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()

    print(u"Showing source {}".format(sourceName))
    ws.call(requests.SetSceneItemRender(sourceName, True))

    ws.disconnect()


def hideSource(sourceNameList):
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()
    for item in sourceNameList:
        ws.call(requests.SetSceneItemRender(item, False))

    ws.disconnect()


def playMedia(mediaName):
    print("Playing Media...")
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

    ws.call(requests.RestartMedia(mediaName))

    ws.disconnect()

def sendHotkey():
    hotkey = settings["HOTKEY TO SEND"]
    print("Sending Hotkey...")
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()


    ws.call(requests.TriggerHotkeyBySequence(hotkey, None))

    ws.disconnect()


def activateFilter(filterName):
    host = "localhost"
    port = 4444
    password = settings["OBS WS PASSWORD"]

    ws = obsws(host, port, password)
    ws.connect()

    ws.call(requests.SetSourceFilterVisibility("WG - ClaymoreEXPBar", str(filterName), True))

    ws.disconnect()




def lazyround(x):
    if not x:
        return x
    return 10 * round(x/10)


class bar:

    def __init__(self):
        self.progress = 0  # Out of 500, how full the bar is
        self.target = 0 # Out of 500, how full the bar should be
        self.imgname = "bar.gif"

        self.barimage = Image.open("Resources/barimage.png")
        left = 0
        top = 0
        right = 50
        bottom = 500
        self.croppedBarimage = self.barimage.crop((left, top, right, bottom))
        del self.barimage

    def deleteBar(self):
        w, h = 50, 500
        # creating new Image object
        img = Image.new("RGBA", (w, h), (255, 0, 0, 0))
        img.save("bar.png")
        shutil.copyfile("./Resources/emptybar.png", "barglow.png")

    def drawBar(self, progress):
        self.progress = progress
        realProgress = 500 - round(self.progress)
        w, h = 50, 500
        shape = [(0, 0), (w, realProgress)]
        outlineShape = [(0, 0), (w - 1, h - 1)]

        # creating new Image object
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        img.paste(self.croppedBarimage)
        # create rectangle image
        draw = ImageDraw.Draw(img)

        draw.rectangle(shape, fill=(0, 255, 0))
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

    def generateGif(self, target, force=False):
        target = round(target/5)
        if target > 100:
            target = 100
        activateFilter(target)


        # self.target = target
        # # target is out of 500 like Progress above
        # if not force:
        #     if lazyround(self.target) == lazyround(self.progress):  # Don't do anything if I don't need to redraw the bar.
        #         return
        # # Create the frames
        # frames = []
        #
        # difference = abs(self.target - self.progress)
        # cycles = round((difference / 5) + 55)
        #
        # if self.target > self.progress:
        #     # POSITIVES
        #     for i in range(cycles):
        #         new_frame = self.drawBar(self.progress)
        #         frames.append(new_frame)
        #         if self.progress < self.target:
        #             self.progress += 5
        # else:
        #     # NEGATIVES
        #     for i in range(cycles):
        #         new_frame = self.drawBar(self.progress)
        #         frames.append(new_frame)
        #         if self.progress > self.target:
        #             self.progress -= 5
        #
        # # Save into a GIF file
        # frames[0].save(self.imgname, format='GIF',
        #                append_images=frames[1:], save_all=True, duration=30, loop=0)
        #
        # timeToDelay = self.find_duration(Image.open(self.imgname))
        # timeToDelay = round(timeToDelay, 1)
        # if timeToDelay < 0.2:
        #     timeToDelay = 0.2
        # time.sleep(timeToDelay)
        # self.freezeImage()
        # time.sleep(0.3)


class common:
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.isActive = False
        self.progress = 0.0  # PROGRESS OUT OF 500
        self.drainrate = settings["DRAIN RATE"]
        self.killvalue = 2
        self.activeStartTime = None
        self.activeEndTime = None
        self.isWinActive = False
        self.currentlyActiveMode = None
        self.spamMsg = ""
        self.returnToNormal()
        self.hotkeyTrigger = settings["HOTKEY TRIGGER PHRASE"].strip()

    def hideAllSources(self):
        sourceNameList = []
        for item in settings:
            if "SOURCE" in item:
                sourceNameList.append(settings[item])

        hideSource(sourceNameList)

    def returnToNormal(self):
        self.hideAllSources()
        self.isWinActive = False

    def win(self):
        if self.currentlyActiveMode == "Rip and Tear":
            RIPANDTEAR.win()
        elif self.currentlyActiveMode == "Inspire":
            INSPIRE.win()
        elif self.currentlyActiveMode == "Cheer":
            CHEER.win()
        elif self.currentlyActiveMode == "Legendary":
            LEGENDARY.win()
        elif not self.currentlyActiveMode:
            return

    def lose(self):
        self.returnToNormal()
        showSource(settings["FAIL SOURCE"])
        self.isActive = False
        self.startTime = None
        self.endTime = None
        drawBar.deleteBar()
        self.progress = 0
        time.sleep(settings["FAIL DURATION"])
        self.returnToNormal()

    def trigger(self):
        if self.currentlyActiveMode == "Rip and Tear":
            RIPANDTEAR.trigger()
        elif self.currentlyActiveMode == "Inspire":
            INSPIRE.trigger()
        elif self.currentlyActiveMode == "Cheer":
            CHEER.trigger()
        elif self.currentlyActiveMode == "Legendary":
            LEGENDARY.trigger()
        elif not self.currentlyActiveMode:
            return

class ripAndTear():
    def __init__(self):
        self.triggerMsg = settings["RAT TRIGGER MESSAGE"]
        self.spamMsg = settings["RAT SPAM MESSAGE"]

    def start(self, args, user):
        if COMMON.isActive:
            return
        if (user.lower() != settings["TRIGGER USER"].lower()) and (user != settings["CHANNEL"]):
            return
        self.actuallyStart()

    def actuallyStart(self):
        COMMON.currentlyActiveMode = "Rip and Tear"
        COMMON.spamMsg = settings["RAT SPAM MESSAGE"]
        COMMON.startTime = datetime.datetime.now()
        COMMON.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        COMMON.isActive = True
        COMMON.progress = 0
        showSource(settings["RAT BAR SOURCE"])
        chatConnection.sendToChat("Rip and Tear mode is active! Spam %s in chat to fill the bar!" % COMMON.spamMsg)
        drawBar.generateGif(0, True)
        shutil.copyfile("./Resources/barglow.png", "barglow.png")


    def stop(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        COMMON.progress = 0
        drawBar.deleteBar()
        COMMON.returnToNormal()
        chatConnection.sendToChat("Rip and Tear is now over, please stop saying %s in chat." % COMMON.spamMsg)

    def trigger(self):
        if COMMON.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            COMMON.triggervalue = 500 / ((users)*(difficulty*.8))
            COMMON.progress += COMMON.triggervalue

    def win(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        drawBar.deleteBar()
        COMMON.hideAllSources()
        showSource(settings["RAT ACTIVE SOURCE"])
        COMMON.progress = 0
        COMMON.isWinActive = True
        COMMON.activeStartTime = datetime.datetime.now()
        COMMON.activeEndTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["ACTIVE DURATION"])

class inspire():
    def __init__(self):
        self.triggerMsg = settings["INSPIRE TRIGGER MESSAGE"]
        self.spamMsg = settings["INSPIRE SPAM MESSAGE"]

    def start(self, args, user):
        if COMMON.isActive:
            return
        if (user.lower() != settings["TRIGGER USER"].lower()) and (user != settings["CHANNEL"]):
            return
        self.actuallyStart()

    def actuallyStart(self):
        COMMON.currentlyActiveMode = "Inspire"
        COMMON.spamMsg = settings["INSPIRE SPAM MESSAGE"]
        COMMON.startTime = datetime.datetime.now()
        COMMON.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        COMMON.isActive = True
        COMMON.progress = 0
        showSource(settings["INSPIRE BAR SOURCE"])
        chatConnection.sendToChat("Inspire mode is active! Spam %s in chat to fill the bar!" % COMMON.spamMsg)
        drawBar.generateGif(0, True)
        shutil.copyfile("./Resources/barglow.png", "barglow.png")


    def stop(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        COMMON.progress = 0
        drawBar.deleteBar()
        COMMON.returnToNormal()
        chatConnection.sendToChat("Inspire mode is now over, please stop saying %s in chat." % COMMON.spamMsg)

    def trigger(self):
        if COMMON.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            COMMON.triggervalue = 500 / ((users)*(difficulty*.8))
            COMMON.progress += COMMON.triggervalue

    def win(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        drawBar.deleteBar()
        COMMON.hideAllSources()
        showSource(settings["INSPIRE ACTIVE SOURCE"])
        COMMON.progress = 0
        COMMON.isWinActive = True
        COMMON.activeStartTime = datetime.datetime.now()
        COMMON.activeEndTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["ACTIVE DURATION"])

class cheer():
    def __init__(self):
        self.triggerMsg = settings["CHEER TRIGGER MESSAGE"]
        self.spamMsg = settings["CHEER SPAM MESSAGE"]

    def start(self, args, user):
        if COMMON.isActive:
            return
        if (user.lower() != settings["TRIGGER USER"].lower()) and (user != settings["CHANNEL"]):
            return
        self.actuallyStart()

    def actuallyStart(self):
        COMMON.currentlyActiveMode = "Cheer"
        COMMON.spamMsg = settings["CHEER SPAM MESSAGE"]
        COMMON.startTime = datetime.datetime.now()
        COMMON.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        COMMON.isActive = True
        COMMON.progress = 0
        showSource(settings["CHEER BAR SOURCE"])
        chatConnection.sendToChat("Cheer mode is active! Spam %s in chat to fill the bar!" % COMMON.spamMsg)
        drawBar.generateGif(0, True)
        shutil.copyfile("./Resources/barglow.png", "barglow.png")


    def stop(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        COMMON.progress = 0
        drawBar.deleteBar()
        COMMON.returnToNormal()
        chatConnection.sendToChat("Cheer mode is now over, please stop saying %s in chat." % COMMON.spamMsg)

    def trigger(self):
        if COMMON.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            COMMON.triggervalue = 500 / ((users)*(difficulty*.8))
            COMMON.progress += COMMON.triggervalue

    def win(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        drawBar.deleteBar()
        COMMON.hideAllSources()
        showSource(settings["CHEER ACTIVE SOURCE"])
        COMMON.progress = 0
        COMMON.isWinActive = True
        COMMON.activeStartTime = datetime.datetime.now()
        COMMON.activeEndTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["ACTIVE DURATION"])

class legendary():
    def __init__(self):
        self.triggerMsg = settings["LEGENDARY TRIGGER MESSAGE"]
        self.spamMsg = settings["LEGENDARY SPAM MESSAGE"]

    def start(self, args, user):
        if COMMON.isActive:
            return
        if (user.lower() != settings["TRIGGER USER"].lower()) and (user != settings["CHANNEL"]):
            return
        self.actuallyStart()

    def actuallyStart(self):
        COMMON.currentlyActiveMode = "Legendary"
        COMMON.spamMsg = settings["LEGENDARY SPAM MESSAGE"]
        COMMON.startTime = datetime.datetime.now()
        COMMON.endTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["BAR DURATION"])
        COMMON.isActive = True
        COMMON.progress = 0
        showSource(settings["LEGENDARY BAR SOURCE"])
        chatConnection.sendToChat("Legendary mode is active! Spam %s in chat to fill the bar!" % COMMON.spamMsg)
        drawBar.generateGif(0, True)
        shutil.copyfile("./Resources/barglow.png", "barglow.png")


    def stop(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        COMMON.progress = 0
        drawBar.deleteBar()
        COMMON.returnToNormal()
        chatConnection.sendToChat("Legendary mode is now over, please stop saying %s in chat." % COMMON.spamMsg)

    def trigger(self):
        if COMMON.isActive:
            users = len(core.getAllUsers())
            difficulty = settings["DIFFICULTY"]

            COMMON.triggervalue = 500 / ((users)*(difficulty*.8))
            COMMON.progress += COMMON.triggervalue

    def win(self):
        COMMON.isActive = False
        COMMON.startTime = None
        COMMON.endTime = None
        drawBar.deleteBar()
        COMMON.hideAllSources()
        showSource(settings["LEGENDARY ACTIVE SOURCE"])
        COMMON.progress = 0
        COMMON.isWinActive = True
        COMMON.activeStartTime = datetime.datetime.now()
        COMMON.activeEndTime = datetime.datetime.now() + datetime.timedelta(seconds=settings["ACTIVE DURATION"])

drawBar = bar()
COMMON = common()
RIPANDTEAR = ripAndTear()
INSPIRE = inspire()
CHEER = cheer()
LEGENDARY = legendary()
