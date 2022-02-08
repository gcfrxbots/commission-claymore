from threading import Thread
from Initialize import *
initSetup()
from Authenticate import *
from CustomCommands import COMMON, RIPANDTEAR, INSPIRE, CHEER, LEGENDARY, commands_CustomCommands, drawBar, showSource, sendHotkey, testbits, exp

# https://github.com/obsproject/obs-websocket/releases/tag/4.9.1

class runMiscControls:

    def __init__(self):
        pass

    def getUser(self, line):
        seperate = line.split(":", 2)
        user = seperate[1].split("!", 1)[0]
        return user

    def getMessage(self, line):
        seperate = line.split(":", 2)
        message = seperate[2]
        return message

    def formatTime(self):
        return datetime.datetime.today().now().strftime("%I:%M")


def runcommand(command, cmdArguments, user, mute):
    global settings
    commands = {**commands_CustomCommands}
    cmd = None
    arg1 = None
    arg2 = None

    for item in commands:
        if item == command:
            if commands[item][0] == "MOD":  # MOD ONLY COMMANDS:
                if (user in core.getmoderators()):
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    chatConnection.sendToChat("You don't have permission to do this.")
                    return
            elif commands[item][0] == "STREAMER":  # STREAMER ONLY COMMANDS:
                if user == settings['CHANNEL']:
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    chatConnection.sendToChat("You don't have permission to do this.")
                    return
            else:
                cmd = commands[item][0]
                arg1 = commands[item][1]
                arg2 = commands[item][2]
            break
    if not cmd:
        return

    #try:  # Run all commands as a try/except, so the bot doesn't crash if one bot errors out.
    output = eval(cmd + '(%s, %s)' % (arg1, arg2))
    #except Error as e:
        # print("Error running the command %s with the args %s" % (command, cmdArguments))
        # print(e)
    #else:
    if not output:
        return

    chatConnection.sendToChat(user + " >> " + output)


def main():
    global settings
    chatConnection.start()
    while True:
        result = chatConnection.ws.recv()
        resultDict = json.loads(result)
        #print(resultDict)
        if debugMode:
            print(resultDict)
        if "event" in resultDict.keys() and not chatConnection.active:
            if "is_live" in resultDict["event"]:
                print(">> Connection to chat successful!")
                channel = resultDict["event"]["streamer"]["username"]
                #settings["CHANNEL"] = channel
                chatConnection.active = True
                if chatConnection.puppet:
                    chatConnection.puppetlogin()

        if "event" in resultDict.keys():  # Any actual event is under this
            eventKeys = resultDict["event"].keys()

            if "reward" in eventKeys:
                rewardTitle = resultDict["event"]["reward"]["title"]
                rewardPrompt = resultDict["event"]["reward"]["prompt"]
                rewardCost = resultDict["event"]["reward"]["cost"]
                user = resultDict["event"]["sender"]["displayname"]
                print("(" + misc.formatTime() + ")>> " + user + " redeemed reward title %s, prompt %s, for %s points." % (rewardTitle, rewardPrompt, rewardCost))

            if "subscriber" in eventKeys:
                try:
                    subUsername = resultDict["event"]["subscriber"]["username"]
                    subMonths = resultDict["event"]["months"]
                    subLevel = resultDict["event"]["sub_level"]
                    print("(" + misc.formatTime() + ")>> " + subUsername + " subscribed with level %s for %s months." % (subLevel, subMonths))
                except:
                    pass

            if "donations" in eventKeys:
                    bitsAmount = round(resultDict["event"]["donations"][0]["amount"])
                    user = resultDict["event"]["sender"]["displayname"]
                    message = resultDict["event"]["message"]
                    print("(" + misc.formatTime() + ")>> " + user + " cheered %s bits with the message %s" % (bitsAmount, message))
                    exp(user, int(bitsAmount))
                
            if "message" in eventKeys:  # Got chat message, display it then process commands
                try:
                    message = resultDict["event"]["message"]
                    if message:
                        user = resultDict["event"]["sender"]["displayname"]
                        command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                        cmdarguments = message.replace(command or "\r" or "\n", "")[1:]
                        print("(" + misc.formatTime() + ")>> " + user + ": " + message)

                        if command[0] == "!":
                            runcommand(command, cmdarguments, user, False)
                        # Spam words
                        if COMMON.spamMsg in command and COMMON.isActive:
                            COMMON.trigger()

                        if RIPANDTEAR.triggerMsg in message and RIPANDTEAR.triggerMsg.strip():
                            RIPANDTEAR.start(None, user)
                        if INSPIRE.triggerMsg in message and INSPIRE.triggerMsg.strip():
                            INSPIRE.start(None, user)
                        if CHEER.triggerMsg in message and CHEER.triggerMsg.strip():
                            CHEER.start(None, user)
                        if LEGENDARY.triggerMsg in message and LEGENDARY.triggerMsg.strip():
                            LEGENDARY.start(None, user)

                        if COMMON.hotkeyTrigger in message and COMMON.hotkeyTrigger:
                            sendHotkey()
                except PermissionError:
                    pass

        if "disclaimer" in resultDict.keys():  # Should just be keepalives?
            if resultDict["type"] == "KEEP_ALIVE":
                response = {"type": "KEEP_ALIVE"}
                chatConnection.sendRequest(response)

        if "error" in resultDict.keys():
            print("CHAT CONNECTION ERROR : " + resultDict["error"])
            if resultDict['error'] == "USER_AUTH_INVALID":
                print("Channel Auth Token Expired or Invalid - Reauthenticating...")
                authChatConnection.main("main")
            elif resultDict['error'] == "PUPPET_AUTH_INVALID":
                print("Bot Account Auth Token Expired or Invalid -  Reauthenticating...")
                authChatConnection.main("main")
            else:
                print("Please report this error to rxbots so we can get it resolved.")
                print("Try running RXBOT_DEBUG.bat in the RxBot folder to get more info on this error to send to me.")


def console():  # Thread to handle console input
    while True:
        consoleIn = input("")

        command = ((consoleIn.split(' ', 1)[0]).lower()).replace("\r", "")
        cmdArguments = consoleIn.replace(command or "\r" or "\n", "").strip()
        # Run the commands function
        if command:
            if command[0] == "!":
                runcommand(command, cmdArguments, "CONSOLE", True)

            if command.lower() in ["quit", "exit", "leave", "stop", "close"]:
                print("Shutting down")
                os._exit(1)

def tick():
    cachedTime = datetime.datetime.now()
    drain = 0
    while True:
        time.sleep(0.2)
        if COMMON.isActive:
            drain += 1
            if drain > (COMMON.drainrate * 8):
                drain = 0
                if 500 > COMMON.progress > 0:
                    COMMON.progress -= 10

            if COMMON.endTime < datetime.datetime.now():
                if COMMON.progress >= 500:
                    COMMON.win()
                else:
                    COMMON.lose()

            if datetime.datetime.now() > cachedTime + datetime.timedelta(milliseconds=drawBar.bardelay):
                cachedTime = datetime.datetime.now()
                drawBar.generateGif(COMMON.progress)

        if COMMON.isWinActive:
            if COMMON.activeEndTime < datetime.datetime.now():
                COMMON.returnToNormal()


if __name__ == "__main__":
    misc = runMiscControls()

    t1 = Thread(target=main)
    t2 = Thread(target=console)
    t3 = Thread(target=tick)

    t1.start()
    t2.start()
    t3.start()

