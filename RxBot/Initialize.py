from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import os
import datetime
try:
    import xlsxwriter
    import xlrd
    import PIL
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")
global settings

class socketConnection:
    def __init__(self):
        self.socketConn = socket.socket()

    def openSocket(self):
        self.socketConn.connect(("irc.chat.twitch.tv", int(settings['PORT'])))
        self.socketConn.send(("PASS " + settings['BOT OAUTH'] + "\r\n").encode("utf-8"))
        self.socketConn.send(("NICK " + settings['BOT NAME'] + "\r\n").encode("utf-8"))
        self.socketConn.send(("JOIN #" + settings['CHANNEL'] + "\r\n").encode("utf-8"))
        return self.socketConn

    def sendMessage(self, message):
        print(message)
        messageTemp = "PRIVMSG #" + settings['CHANNEL'] + " : " + message
        self.socketConn.send((messageTemp + "\r\n").encode("utf-8"))
        print("Sent: " + messageTemp)

    def joinRoom(self, s):
        readbuffer = ""
        Loading = True

        while Loading:
            readbuffer = readbuffer + s.recv(1024).decode("utf-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:
                Loading = self.loadingComplete(line)

    def loadingComplete(self, line):
        if ("End of /NAMES list" in line):
            print(">> Bot Startup complete!")
            return False
        else:
            return True

class coreFunctions:
    def __init__(self):
        pass


    def getmoderators(self):
        moderators = []
        json_url = urllib.request.urlopen('http://tmi.twitch.tv/group/user/' + settings['CHANNEL'].lower() + '/chatters')
        data = json.loads(json_url.read())['chatters']
        mods = data['moderators'] + data['broadcaster']

        for item in mods:
            moderators.append(item)
        print(data)
        print(moderators)
        return moderators

    def getAllUsers(self):
        users = []
        json_url = urllib.request.urlopen('http://tmi.twitch.tv/group/user/' + settings['CHANNEL'].lower() + '/chatters')
        data = json.loads(json_url.read())['chatters']
        for item in (list(data.values())):
            for subitem in item:
                users.append(subitem)

        return users





chatConnection = socketConnection()
core = coreFunctions()

def initSetup():
    global settings


    # Create Folders
    if not os.path.exists('../Config'):
        buildConfig()
    if not os.path.exists('Resources'):
        os.makedirs('Resources')
        print("Creating necessary folders...")

    # Create Settings.xlsx
    loadedsettings = settingsConfig.settingsSetup(settingsConfig())
    settings = loadedsettings

    return

