from threading import Thread
from Initialize import *
initSetup()
from CustomCommands import COMMON, RIPANDTEAR, INSPIRE, CHEER, LEGENDARY, commands_CustomCommands, drawBar, showSource, sendHotkey


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
                    chatConnection.sendMessage("You don't have permission to do this.")
                    return
            elif commands[item][0] == "STREAMER":  # STREAMER ONLY COMMANDS:
                if (user == settings['CHANNEL']):
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    chatConnection.sendMessage("You don't have permission to do this.")
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

    chatConnection.sendMessage(user + " >> " + output)


def watchChat():  # Thread to handle twitch/IRC input
    s = chatConnection.openSocket()
    chatConnection.joinRoom(s)
    readbuffer = ""
    while True:
        readbuffer = readbuffer + s.recv(1024).decode("utf-8")
        temp = readbuffer.split("\n")
        readbuffer = temp.pop()
        for line in temp:
            if "PING" in line:
                s.send(bytes("PONG :tmi.twitch.tv\r\n".encode("utf-8")))
            else:
                # All these things break apart the given chat message to make things easier to work with.
                user = misc.getUser(line)
                message = str(misc.getMessage(line))
                command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                cmdArguments = message.replace(command or "\r" or "\n", "").strip()
                print(("(" + misc.formatTime() + ")>> " + user + ": " + message))
                # Run the commands function
                if command[0] == "!":
                    runcommand(command, cmdArguments, user, False)
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
    cachedProgress = 0
    drain = 0
    while True:
        time.sleep(0.2)
        if COMMON.isActive:
            drawBar.generateGif(COMMON.progress)

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

        if COMMON.isWinActive:
            if COMMON.activeEndTime < datetime.datetime.now():
                COMMON.returnToNormal()


if __name__ == "__main__":
    misc = runMiscControls()

    t1 = Thread(target=watchChat)
    t2 = Thread(target=console)
    t3 = Thread(target=tick)

    t1.start()
    t2.start()
    t3.start()

