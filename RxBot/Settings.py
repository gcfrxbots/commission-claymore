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
parser.set_defaults(GenSettings=False)

GenSettings = (vars(parser.parse_args())["GenSettings"])


'''----------------------SETTINGS----------------------'''

'''FORMAT ---->   ("Option", "Default", "This is a description"), '''

defaultSettings = [
    ("PORT", 6667, "Try 80 if this doesn't work. Use 443 or 6697 for SSL. Don't touch otherwise."),
    ("BOT OAUTH", "", "To get this oauth code, head here and log in with YOUR BOT'S account: https://twitchapps.com/tmi/"),
    ("BOT NAME", "", "Your bot's Twitch username, all lowercase."),
    ("CHANNEL", "", "Your Twitch username, all lowercase."),
    ("OBS WS PASSWORD", "test", "Your obs-websocket password, configured in OBS > Tools > Websockets Server Settings"),
    ("", "", ""),
    ("TRIGGER USER", "CreatisBot", "Only this user can send the TRIGGER MESSAGE and trigger the bot."),
    ("FILL COLOR", "red", "Fill color of the bar, either in #fffffff format or the name of the color."),
    ("DRAIN RATE", "4", "The bar will slowly go down every X amount of seconds if nobody says kill."),
    ("DIFFICULTY", "10", "Raise this value to make the bar harder to increase, lower it to make it easier."),
    ("BAR DURATION", "30", "The amount of time in seconds the meter is active. Remember to adjust difficulty and drain rate accordingly."),
    ("ACTIVE DURATION", "60", "The amount of time in seconds the victory scene is active after the bar fills. After this time is up it will revert back to the normal scene."),
    ("NORMAL SCENE", "Normal", "OBS Scene name for your normal game scene"),
    ("", "", "RIP AND TEAR"),
    ("RAT TRIGGER MESSAGE", "", "The message from another bot that will trigger this bot's main function."),
    ("RAT SPAM MESSAGE", "kill", "The message users in chat will spam to fill the bar"),
    ("RAT BAR SCENE", "RAT Bar", "OBS Scene name for the scene with the bar in it"),
    ("RAT ACTIVE SCENE", "RAT Active", "OBS Scene name for the rip and tear scene if the chat fills the bar"),
    ("RAT FAIL SCENE", "RAT Fail", "OBS Scene name for if chat fails to fill the bar"),
    ("", "", "INSPIRE"),
    ("INSPIRE TRIGGER MESSAGE", "", "The message from another bot that will trigger this bot's main function."),
    ("INSPIRE SPAM MESSAGE", "inspire", "The message users in chat will spam to fill the bar"),
    ("INSPIRE BAR SCENE", "INSPIRE Bar", "OBS Scene name for the scene with the bar in it"),
    ("INSPIRE ACTIVE SCENE", "INSPIRE Active", "OBS Scene name for the rip and tear scene if the chat fills the bar"),
    ("INSPIRE FAIL SCENE", "INSPIRE Fail", "OBS Scene name for if chat fails to fill the bar"),
    ("", "", "CHEER"),
    ("CHEER TRIGGER MESSAGE", "", "The message from another bot that will trigger this bot's main function."),
    ("CHEER SPAM MESSAGE", "cheer", "The message users in chat will spam to fill the bar"),
    ("CHEER BAR SCENE", "CHEER Bar", "OBS Scene name for the scene with the bar in it"),
    ("CHEER ACTIVE SCENE", "CHEER Active", "OBS Scene name for the rip and tear scene if the chat fills the bar"),
    ("CHEER FAIL SCENE", "CHEER Fail", "OBS Scene name for if chat fails to fill the bar"),
    ("", "", "LEGENDARY"),
    ("LEGENDARY TRIGGER MESSAGE", "", "The message from another bot that will trigger this bot's main function."),
    ("LEGENDARY SPAM MESSAGE", "legend", "The message users in chat will spam to fill the bar"),
    ("LEGENDARY BAR SCENE", "LEGENDARY Bar", "OBS Scene name for the scene with the bar in it"),
    ("LEGENDARY ACTIVE SCENE", "LEGENDARY Active", "OBS Scene name for the rip and tear scene if the chat fills the bar"),
    ("LEGENDARY FAIL SCENE", "LEGENDARY Fail", "OBS Scene name for if chat fails to fill the bar"),
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
        if str(int(settings["PORT"])) not in ('80', '6667', '443', '6697'):  # Convert into non-float string
            stopBot("Wrong Port! The port must be 80 or 6667 for standard connections, or 443 or 6697 for SSL")
        if not settings['BOT OAUTH']:
            stopBot("Missing BOT OAUTH - Please follow directions in the settings or readme.")
        if not ('oauth:' in settings['BOT OAUTH']):
            stopBot("Invalid BOT OAUTH - Your oauth should start with 'oauth:'")
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