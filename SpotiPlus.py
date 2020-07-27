import spotipy 
import spotipy.util as util
import json
from Config import CLIENT_ID, CLIENT_SECRET, USER
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException
from os import path

class SpotiPlus():

    def __init__(self):

        # Making a spotify object
        self.__spotify = self.__createSpotifyObject()
        self.__selectedPlaylist = ""

    def __getCurrentSong(self):
        """Will get the name, artist and id of the current playing song. Will return a dictionary"""
        
        # Getting the nested dictionaries
        results = self.__spotify.current_user_playing_track()
        
        # Checking if results is not empty
        if (results == [None, ""]):

            print("No song is currently playing")
            return

        # Getting the name of the song
        songName = results["item"]["name"]

        # Adding all the needed values to the dic
        currentSong = {}

        # Getting all the artist of the current song
        artistNames = [artist["name"] for artist in results["item"]["artists"]]

        # Combining all the artist for each song into one string seperated by / (artist / artist / artist)
        allArtists = ", ".join(artistNames)
        
        # adding our string of songname + artist and the song id to the dictionary and returning it
        currentSong["nameAndArtists"] = songName + " By " + allArtists
        currentSong["id"] = results["item"]["id"]
        return currentSong

    def __createSpotifyObject(self):
        """Will create a spotify object and return it"""
        
        # Defining the scope(s) of the application
        scope = "playlist-modify-public playlist-modify-private user-read-currently-playing"

        # Getting the token
        token = util.prompt_for_user_token(username=USER, scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri="https://google.com/")

        # Returning our spotify object
        return spotipy.Spotify(auth=token)

    def __writeSettingsToFile(self):
        """Will save the selected playlist to the file"""
        
        fileName = "settings.txt"
    
        # Opening file and creating it if it doesn't exist yet
        with open(fileName, "w+") as file:

            # Writing the selected playlist to the file
            file.write("selectedPlaylist : " + self.__selectedPlaylist)

    def readSettingFromFile(self):
        """Will read the previously set settings from the file"""
            
        fileName = "settings.txt"

        # Checking if the file exist or not (it wont if this is first time starting up / no playlist has ever been set
        if (path.exists(fileName)):
            
            with open(fileName, "r") as file:

                # Since we only have one setting which is the set playlist we can justify only getting the first line of the file
                firstLine = file.readline()
                playlistID = firstLine.split(" : ")[1]
        
            self.__selectedPlaylist = playlistID

    def getCurrentPlaylistName(self):
        """Will return the name of the current playlist"""

        playlist = self.__spotify.user_playlist(USER, self.__selectedPlaylist)
        return playlist["name"]

    def addCurrentSongToSelectedPlaylist(self):
        """Will add the currently playing song to the selected playlist"""

        # Getting the current song
        currentSong = self.__getCurrentSong()

        # Adding the current song id to the selected playlist
        self.__spotify.user_playlist_add_tracks(USER, self.__selectedPlaylist, [currentSong["id"]])

    def setSelectedPlaylist(self, playlistID):
        """Will set the given playlist id as the current selected playlist"""

        self.__selectedPlaylist = playlistID

        # Setting the playlist in the settings as well
        self.__writeSettingsToFile()

    def checkIfValidPlaylist(self, playlistID):
        """Checking if the playlist exists and whether the user is the owner or not (needed to add songs to it)"""
        
        # Calling the user playlist 
        try:

            self.__spotify.user_playlist(USER, playlistID)
            return True
        
        except SpotifyException as e:

            return False

    def checkIfUserIsOwner(self, playlistID):
        """Function will check if user is the owner of the given playlist"""

        try:

            result = self.__spotify.user_playlist(USER, playlistID)

            # If the owner id does not equal user id, used different format for if else here, result = (on_false, on_true)[condition]
            returnVal = (False, True)[result["owner"]["id"] == USER]
            return returnVal

        except SpotifyException as e:

            return False

    def checkIfPlaylistIDHasBeenSet(self):
        """Will return True if a playlist id has been set and False if it is empty (needed to display error msg in kivy GUI)"""

        if (self.__selectedPlaylist == ""):

            return False

        else:

            return True