import pypresence
import pyautogui
import ctypes
import configparser

class Blacklist(object):
    def __init__(self, blacklist: list = [], strict: bool = False):
        self.blacklist = blacklist
        self.strict = strict

    def check(self, name):
        return (any([i.lower() in name.lower() for i in self.blacklist]) and not self.blacklistStrict) or (any([i in name for i in self.blacklist]) and self.blacklistStrict)

class App(pypresence.Presence):
    def __init__(self, appId):
        super(App, self).__init__(client_id=appId)
        self.lastActivity = None
        self.config = configparser.ConfigParser()
        self.blacklist = Blacklist()

    def _getWindowByName(self, name):
        titles = []

        @ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        def enum(hwnd, lParam):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 1
                windowTitle = ctypes.create_unicode_buffer(length)
                ctypes.windll.user32.GetWindowTextW(hwnd, windowTitle, length)
                if name in windowTitle.value:
                    titles.append(windowTitle.value.replace(name, "").strip())

            return True

        ctypes.windll.user32.EnumWindows(enum, 0)

        if len(titles) > 0:
            return titles[0]

        return None

    def buildButtons(self):
            buttons = []
            if self.button1Text and self.button1URL:
                buttons.append({"label": self.button1Text, "url": self.button1URL})
            if self.button2Text and self.button2URL:
                buttons.append({"label": self.button2Text, "url": self.button2URL})
            buttons = buttons or None
            return buttons

    def updateWikipedia(self, wikipedia=None):
        if not wikipedia:
            wikipedia = self._getWindowByName("— Википедия - Google Chrome") or self._getWindowByName("- Wikipedia - Google Chrome")

        if not wikipedia:
            return False

        elif wikipedia == self.lastActivity:
            return True

        if self.blacklist.check(wikipedia):
            return False

        buttons = self.buildButtons()
        self.update(details=f"Читает {wikipedia}", state="на Wikipedia", large_image=self.wikipediaLargeImage, large_text=self.wikipediaLargeImageText, small_image=self.wikipediaSmallImage, small_text=self.wikipediaSmallImageText, buttons=buttons, instance=False)
        self.lastActivity = wikipedia
        return True

    def updateYouTube(self, youtube=None):
        if not youtube:
            youtube = self._getWindowByName("- YouTube - Google Chrome")

        if not youtube:
            return False

        elif youtube == self.lastActivity:
            return True

        if self.blacklist.check(youtube):
            return False

        if "lyric" in youtube.lower() or "nightcore" in youtube.lower() or "song" in youtube.lower():
            text = f"Слушает {youtube}"

        else:
            text = f"Смотрит {youtube}"

        buttons = self.buildButtons()
        self.update(details=text, state="На YouTube", large_image=self.youtubeLargeImage, large_text=self.youtubeLargeImageText, small_image=self.youtubeSmallImage, small_text=self.youtubeSmallImageText, buttons=buttons, instance=False)
        self.lastActivity = youtube
        return True

    def updateCurrentWindow(self):
        try:
            currentWindow = pyautogui.getActiveWindowTitle()
            
        except:
            return

        else:
            if not currentWindow or currentWindow == self.lastActivity:
                return

            elif self.blacklist.check(currentWindow):
                return
            
            elif "- YouTube - Google Chrome" in currentWindow:
                return self.updateYouTube(currentWindow.replace("- YouTube - Google Chrome", "").strip())

            buttons = self.buildButtons()
            self.update(details="Сейчас в", state=currentWindow, large_image=self.currentLargeImage, large_text=self.currentLargeImageText, small_image=self.currentSmallImage, small_text=self.currentSmallImageText, buttons=buttons, instance=False)
            self.lastActivity = currentWindow

    def loadConfig(self, filename):
        self.config.read(filename)
        self.blacklist = Blacklist(blacklist=([i.strip() for i in self.config.get("PRIVACY", "blacklist").split(";") if i != ""] or []), strict=(self.config.getboolean("PRIVACY", "strict") or False))
        self.showYoutube = self.config.getboolean("MAIN", "show-youtube") or False
        self.showCurrent = self.config.getboolean("MAIN", "show-current") or False
        self.showWikipedia = self.config.getboolean("MAIN", "show-wikipedia") or False
        self.youtubeLargeImage = self.config.get("YOUTUBE", "youtube-large-image") or None
        self.youtubeSmallImage = self.config.get("YOUTUBE", "youtube-small-image") or None
        self.youtubeLargeImageText = self.config.get("YOUTUBE", "youtube-large-image-text") or None
        self.youtubeSmallImageText = self.config.get("YOUTUBE", "youtube-small-image-text") or None
        self.currentLargeImage = self.config.get("CURRENT", "current-large-image") or None
        self.currentSmallImage = self.config.get("CURRENT", "current-small-image") or None
        self.currentLargeImageText = self.config.get("CURRENT", "current-large-image-text") or None
        self.currentSmallImageText = self.config.get("CURRENT", "current-small-image-text") or None
        self.wikipediaLargeImage = self.config.get("WIKIPEDIA", "wikipedia-large-image") or None
        self.wikipediaSmallImage = self.config.get("WIKIPEDIA", "wikipedia-small-image") or None
        self.wikipediaLargeImageText = self.config.get("WIKIPEDIA", "wikipedia-large-image-text") or None
        self.wikipediaSmallImageText = self.config.get("WIKIPEDIA", "wikipedia-small-image-text") or None
        self.button1Text = self.config.get("BUTTONS", "button-1-text") or None
        self.button1URL = self.config.get("BUTTONS", "button-1-url") or None
        self.button2Text = self.config.get("BUTTONS", "button-2-text") or None
        self.button2URL = self.config.get("BUTTONS", "button-2-url") or None

    def mainloop(self):
        while True:
            if self.showYouTube:
                if not self.updateYouTube():
                    if self.showWikipedia:
                        if not self.updateWikipedia():
                            if self.showCurrent:
                                self.updateCurrentWindow()
                                
            elif self.showWikipedia:
                if not self.updateWikipedia():
                    if self.showCurrent:
                        self.updateCurrentWindow()
                        
            elif self.showCurrent:
                self.updateCurrentWindow()


try:
    app = App(your_app_id) # get it on discord.com/developers/applications
    app.connect()
    app.loadConfig("./config.ini")
    app.mainloop()
except Exception as e:
    pyautogui.alert(text=repr(e), title="Jabka Activity Error")
    exit(1)
