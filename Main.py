from SpotiPlus import SpotiPlus
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

# Setting the window size and making it non resizable
Config.set("graphics", "width", "300")
Config.set("graphics", "height", "285")
Config.set("graphics", "resizable", False)

class HomeWindow(Screen):
    """This will represent the home window"""
    pass

class SettingsWindow(Screen):
    """This will represent the settings window"""
    pass

class Popups(AnchorLayout):
    """This will represent the popup window"""
    pass

sm = Builder.load_file("SpotiPlus.kv")

class SpotiPlusApp(App):

    def build(self):

        self.sp = SpotiPlus()
        return sm

    def on_start(self):
        """This function is called on the start of the application"""

        # Getting the previously set playlist if existing.
        self.sp.readSettingFromFile()
        # Setting the correct text values in the gui for selected playlist
        self.setPlaylistInGUI()

    def setPlaylistInGUI(self):
        """This function will set the name of the currently selected playlist in the GUI"""
       
        # Checking if a playlist id has been set. setting currentplaylist value to "no playlist selected" otherwise
        if (self.sp.checkIfPlaylistIDHasBeenSet()):

            currentPlaylist = self.sp.getCurrentPlaylistName()

        else:

            currentPlaylist = "No playlist selected!"

        self.root.get_screen("home").ids.selectedPlaylist.text = currentPlaylist
        self.root.get_screen("settings").ids.selectedPlaylist.text = currentPlaylist

    def showPopup(self, msg):
        """Will display a popup with the given msg"""

        def autoClose(dt):
  
            popupWindow.dismiss()

        # Creating an instance of the popup once and setting the msg text.
        show = Popups() 
        show.ids.pu.text = msg

        # Making a popup instance which uses our Popups class as the content (what was created in the kv file)
        popupWindow = Popup(title ="Alert", content = show, size_hint =(None, None), size = (300, 150)) 
        
        # open popup window
        popupWindow.open()

        # Closing the popup automatically in X seconds
        Clock.schedule_once(autoClose, 2)

    def addCurrentSongToPlaylist(self):
        """This function will handle anything needed to add the current song to the selected playlist"""

        # Checking if current playlist has been set or not
        if not (self.sp.checkIfPlaylistIDHasBeenSet()):

            self.showPopup("Please select a playlist first!")
            return

        # Adding current song to selected playlist
        self.sp.addCurrentSongToSelectedPlaylist()
        self.showPopup("Current song has been added to playlist!")

    def setSelectedPlaylist(self):
        """This function will handle anything needed to set the users given playlist as the selected playlist"""

        # Getting the input from the gui by the ID
        playlistID = self.root.get_screen("settings").ids.uInput.text

        # Checking if input isn't empty
        if (len(playlistID) < 1):

            self.showPopup("Playlist ID is too short!")
            return

        # Checking if playlist exists     
        playlistValid = self.sp.checkIfValidPlaylist(playlistID)
        if not (playlistValid):

            self.showPopup(f"Playlist {playlistID} does not exist!")
            return

        # Checking if the user is the owner of the given playlist
        isPlaylistOwner = self.sp.checkIfUserIsOwner(playlistID)
        if not (isPlaylistOwner):

            self.showPopup(f"You are not the owner of playlist {playlistID}!")
            return

        # Setting the playlist in the SpotiPlus class
        self.sp.setSelectedPlaylist(playlistID)
        playlistName = self.sp.getCurrentPlaylistName()
        self.showPopup(f"Playlist {playlistName} succesfully set!")

        # Setting / updating the playlist name in gui
        self.setPlaylistInGUI()

if (__name__ == "__main__"):
  
    app = SpotiPlusApp()
    app.run()
