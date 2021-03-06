import os
import time
import argparse

try:
    import xlrd
    import xlsxwriter
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")

parser = argparse.ArgumentParser(description='Generate Settings File')
parser.add_argument('--g', dest="GenSettings", action="store_true")
parser.add_argument('--d', dest="debugMode", action="store_true")
parser.set_defaults(GenSettings=False, debugMode=False)

GenSettings = (vars(parser.parse_args())["GenSettings"])
debugMode = (vars(parser.parse_args())["debugMode"])


'''----------------------SETTINGS----------------------'''

'''FORMAT ---->   ("Option", "Default", "This is a description"), '''

defaultSettings = [
    ("BOT NAME", "", "Your bot's Twitch username, all lowercase."),
    ("CHANNEL", "", "Your Twitch username, all lowercase."),
    ("OBS WS PASSWORD", "test", "Your obs-websocket password, configured in OBS > Tools > Websockets Server Settings"),
    ("", "", ""),
    ("TRIGGER USER", "CreatisBot", "Only this user can send the TRIGGER MESSAGE and trigger the bot."),
    ("FILL COLOR", "red", "DEPRECATED - Fill color of the bar, either in #fffffff format or the name of the color."),
    ("DRAIN RATE", "4", "The bar will slowly go down every X amount of seconds if nobody says kill."),
    ("DIFFICULTY", "10", "Raise this value to make the bar harder to increase, lower it to make it easier."),
    ("BAR DURATION", "30", "The amount of time in seconds the meter is active. Remember to adjust difficulty and drain rate accordingly."),
    ("ACTIVE DURATION", "60", "The amount of time in seconds the victory Source is active after the bar fills. After this time is up it will revert back to the normal Source."),
    ("FAIL SOURCE", "Fail", "OBS Source name for the fail source"),
    ("FAIL DURATION", "15", "How long in seconds to display the fail source before hiding it."),
    ("BAR ANIMATION DELAY", "100", "This should be equal to the Custom Duration of the filter in OBS, in milliseconds."),
    ("", "", "RIP AND TEAR"),
    ("RAT TRIGGER MESSAGE", "", "The message from another bot that will trigger this mode."),
    ("RAT SPAM MESSAGE", "kill", "The message users in chat will spam to fill the bar"),
    ("RAT BAR SOURCE", "RAT Bar", "OBS Source name for the Rip and Tear Source with the bar in it"),
    ("RAT ACTIVE SOURCE", "RAT Active", "OBS Source name for the Rip and Tear Source if the chat fills the bar"),
    ("", "", "INSPIRE"),
    ("INSPIRE TRIGGER MESSAGE", "", "The message from another bot that will trigger this mode."),
    ("INSPIRE SPAM MESSAGE", "inspire", "The message users in chat will spam to fill the bar"),
    ("INSPIRE BAR SOURCE", "INSPIRE Bar", "OBS Source name for the Inspire Source with the bar in it"),
    ("INSPIRE ACTIVE SOURCE", "INSPIRE Active", "OBS Source name for the Inspire Source if the chat fills the bar"),
    ("", "", "CHEER"),
    ("CHEER TRIGGER MESSAGE", "", "The message from another bot that will trigger this mode."),
    ("CHEER SPAM MESSAGE", "cheer", "The message users in chat will spam to fill the bar"),
    ("CHEER BAR SOURCE", "CHEER Bar", "OBS Source name for the Cheer Source with the bar in it"),
    ("CHEER ACTIVE SOURCE", "CHEER Active", "OBS Source name for the Cheer Source if the chat fills the bar"),
    ("", "", "LEGENDARY"),
    ("LEGENDARY TRIGGER MESSAGE", "", "The message from another bot that will trigger this mode."),
    ("LEGENDARY SPAM MESSAGE", "legend", "The message users in chat will spam to fill the bar"),
    ("LEGENDARY BAR SOURCE", "LEGENDARY Bar", "OBS Source name for the Legendary Source with the bar in it"),
    ("LEGENDARY ACTIVE SOURCE", "LEGENDARY Active", "OBS Source name for the Legendary Source if the chat fills the bar"),
    ("", "", ""),
    ("HOTKEY TRIGGER PHRASE", "", "The message from another bot that will trigger the hotkey configured below"),
    ("HOTKEY TO SEND", "OBS_KEY_F17", "The message from another bot that will trigger the hotkey configured below. Keys are here: https://bit.ly/3dZVwGe"),
    ("", "", ""),
    ("BAR MAX SOURCE TO SHOW", "", "The source to show when the bar is filled"),
    ("BAR MAX FILTER TO SHOW", "rainbowbar", "The filter to show when the bar is filled"),
    ("EXP MAX", "2200", "Makes the message below appear when the exp reaches this value."),
    ("EXP MAX MSG", "Claymore levelled up!", "This message appears when your exp reaches the EXP MAX"),
    ("FILTER SCENE", "WG - ClaymoreEXPBar", "The scene name with all the filters in it to make the bar work"),
]


def stopBot(err):
    print(">>>>>---------------------------------------------------------------------------<<<<<")
    print(err)
    print(">>>>>----------------------------------------------------------------------------<<<<<")
    time.sleep(3)
    quit()


def deformatEntry(inp):
    if isinstance(inp, list):
        toRemove = ["'", '"', "[", "]", "\\", "/"]
        return ''.join(c for c in str(inp) if not c in toRemove)

    elif isinstance(inp, bool):
        if inp:
            return "Yes"
        else:
            return "No"

    else:
        return inp


def writeSettings(sheet, toWrite):

    row = 1  # WRITE SETTINGS
    col = 0
    for col0, col1, col2 in toWrite:
        sheet.write(row, col, col0)
        sheet.write(row, col + 1, col1)
        sheet.write(row, col + 2, col2)
        row += 1


class settingsConfig:
    def __init__(self):
        self.defaultSettings = defaultSettings

    def formatSettingsXlsx(self):
        try:
            with xlsxwriter.Workbook('../Config/Settings.xlsx') as workbook:
                worksheet = workbook.add_worksheet('Settings')
                format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
                boldformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'black'})
                lightformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'black', 'bg_color': '#DCDCDC', 'border': True})
                worksheet.set_column(0, 0, 25)
                worksheet.set_column(1, 1, 50)
                worksheet.set_column(2, 2, 130)
                worksheet.write(0, 0, "Option", format)
                worksheet.write(0, 1, "Your Setting", boldformat)
                worksheet.write(0, 2, "Description", format)
                worksheet.set_column('B:B', 50, lightformat)  # END FORMATTING

                writeSettings(worksheet, self.defaultSettings)

        except PermissionError:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only.")
        except:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only. [0]")

    def reloadSettings(self, tmpSettings):
        for item in tmpSettings:
            for i in enumerate(defaultSettings):
                if (i[1][0]) == item:  # Remove all 'list' elements from the string to feed it back into the speadsheet
                    defaultSettings[i[0]] = (item, deformatEntry(tmpSettings[item]), defaultSettings[i[0]][2])

        self.formatSettingsXlsx()

    def readSettings(self, wb):
        settings = {}
        worksheet = wb.sheet_by_name("Settings")

        for item in range(worksheet.nrows):
            if item == 0:
                pass
            else:
                option = worksheet.cell_value(item, 0)
                try:
                    setting = int(worksheet.cell_value(item, 1))
                except ValueError:
                    setting = str(worksheet.cell_value(item, 1))
                    # Change "Yes" and "No" into bools, only for strings
                    if setting.lower() == "yes":
                        setting = True
                    elif setting.lower() == "no":
                        setting = False

                settings[option] = setting

        if worksheet.nrows != (len(defaultSettings) + 1):
            self.reloadSettings(settings)
            stopBot("The settings have been changed with an update! Please check your Settings.xlsx file then restart the bot.")
        return settings


    def settingsSetup(self):
        global settings

        if not os.path.exists('../Config'):
            print("Creating a Config folder, check it out!")
            os.mkdir("../Config")

        if not os.path.exists('../Config/Settings.xlsx'):
            print("Creating Settings.xlsx")
            self.formatSettingsXlsx()
            stopBot("Please open Config / Settings.xlsx and configure the bot, then run it again.")

        wb = xlrd.open_workbook('../Config/Settings.xlsx')
        # Read the settings file

        settings = self.readSettings(wb)

        # Check Settings
        if not settings['BOT NAME'] or not settings['CHANNEL']:
            stopBot("Missing BOT NAME or CHANNEL")

        print(">> Initial Checkup Complete! Connecting to Chat...")
        return settings


def buildConfig():
    if not os.path.exists('../Config'):
        os.mkdir("../Config")

    if not os.path.exists('../Config/Settings.xlsx'):
        print("Creating Settings.xlsx")
        settingsConfig.formatSettingsXlsx(settingsConfig())
        print("\nPlease open Config / Settings.xlsx and configure the bot, then run it again.")
        print("Please follow the setup guide to everything set up! https://rxbots.net/rxbot-setup.html")
        time.sleep(3)
        quit()
    else:
        print("Everything is already set up!")


if GenSettings:
    buildConfig()