import os
import xml.etree.ElementTree as et
import urlparse
import sys
import requests
import re
import HTMLParser
from datetime import datetime, timedelta

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from resources.lib import skinpatch

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

sources_path = os.path.join(addon.getAddonInfo("path"), "sources")


class RadioSource():
    def __init__(self, file):
        # Load XML
        xml = et.parse(os.path.join(sources_path, file + ".xml")).getroot()

        # Load source properties from XML
        self.name = xml.find("name").text
        self.streams = dict((int(stream.get("bitrate", default=0)), stream.text)
                            for stream in xml.findall("stream"))
        self.info = dict((child.tag, child.text) for child in xml
                         if child.tag not in ("name", "stream", "scraper"))
        self.url = "{0}?source={1}".format(plugin_url, file)

        # Load scraper properties
        if xml.find("scraper") is not None:
            self.scraper = dict((child.tag, child.text) for child in xml.find("scraper"))
            self.scraper["type"] = xml.find("scraper").get("type", default=None)
        else:
            self.scraper = None

    # Generate a Kodi list item from the radio source
    def list_item(self):
        li = xbmcgui.ListItem(self.name, iconImage="DefaultAudio.png")
        li.setInfo("music", {"title": self.name,
                             "artist": self.info.get("tagline", None),
                             "genre": self.info.get("genre", None)
                             })
        li.setArt(self.__build_art())
        return li

    # Start playing the radio source
    def play(self):
        # Detect correct bitrate stream to play
        if addon.getSetting("bitrate") == "Maximum":
            self.stream_url = self.streams[max(self.streams.keys())]
        else:
            max_bitrate = int(addon.getSetting("bitrate").split(" ")[0])
            bitrates = [bitrate for bitrate in self.streams.keys() if bitrate <= max_bitrate]
            self.stream_url = (self.streams[min(self.streams.keys())]
                               if len(bitrates) == 0 else self.streams[max(bitrates)])

        # Create list item with stream URL and send to Kodi
        li = self.list_item()
        li.setPath(self.stream_url)
        RadioPlayer().play_stream(self)

    # Create dictionary of available artwork files to supply to list item
    def __build_art(self):
        art = {}
        for art_type in ("thumb", "fanart", "poster", "banner",
                         "clearart", "clearlogo", "landscape", "icon"):
            if self.info.get(art_type, None) is not None:
                path = os.path.join(addon.getAddonInfo("path"), "artwork", self.info[art_type])
                if os.path.isfile(path):
                    art[art_type] = path
        return art


class RadioPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def play_stream(self, source):
        self.play(item=source.stream_url, listitem=source.list_item())

        if source.scraper is not None:
            info = RadioInfo(source)
            start_time = datetime.today()
            # Wait for playback to start, then loop until stopped
            while self.isPlaying() or datetime.today() <= start_time + timedelta(seconds=5):
                info.update()
                xbmc.sleep(1000)

            info.cleanup()  # Remove window properties on playback stop


class RadioInfo():
    def __init__(self, source):
        self.api_key = requests.get("http://dev.rocketchilli.com/"
                                    "keystore/ba7000f9-7ef4-4ace-b"
                                    "ca2-f527cdffb393").json()["api-key"]
        self.window = xbmcgui.Window(10000)  # Attach properties to the home window
        self.window_properties = []

        self.scraper = source.scraper
        self.info = {"station": source.name}
        self.first_update = True
        self.next_update = datetime.today()
        self.delayed = False

    def update(self):
        if self.next_update <= datetime.today():
            changed = self.get_now_playing()
            # Get track info if track has changed
            if changed:
                self.get_track_info()
            # Apply delay so OSD update if required
            if changed and "delay" in self.scraper and not self.delayed and not self.first_update:
                self.next_update = datetime.today() + timedelta(seconds=int(self.scraper["delay"]))
                self.delayed = True
            # Set track info if no delay is required, or if a delay has already been applied
            elif changed or self.delayed:
                self.set_info()
                self.delayed = self.first_update = False
            # Wait as usual if track has not changed
            if not self.delayed:
                self.next_update = datetime.today() + timedelta(seconds=10)

    # Push track info to skin the as window properties
    def set_info(self):
        for name, value in self.info.items():
            name = addon.getAddonInfo("id") + "." + name
            if value is None:
                self.window.clearProperty(name)
                if name in self.window_properties:
                    self.window_properties.remove(name)
            else:
                self.window.setProperty(name, value)
                if name not in self.window_properties:
                    self.window_properties.append(name)

    def cleanup(self):
        for name in self.window_properties:
            self.window.clearProperty(name)

    def get_now_playing(self):
        track_id = self.id_track()
        if self.scraper["type"] == "tunein":
            self.__update_tunein()
        # Return True if track info has changed
        return track_id != self.id_track()

    # Retrieve additional track info from last.fm API
    def get_track_info(self):
        # Reset track information before updating
        for key, value in self.info.items():
            if key not in ("title", "artist", "station"):
                self.info[key] = None

        # Request track information
        track_url = ("http://ws.audioscrobbler.com/2.0/?method=track.getInfo"
                     "&api_key={0}&artist={1}&track={2}&format=json")
        try:
            response = requests.get(track_url.format(self.api_key, urlencode(self.info["artist"]),
                                                     urlencode(self.info["title"])))
            if response.status_code == requests.codes.ok and "track" in response.json():
                track_info = response.json()["track"]
                if "album" in track_info:
                    self.info["album"] = track_info["album"]["title"]
                    if "image" in track_info["album"] and len(track_info["album"]["image"]) > 0:
                        self.info["thumb"] = track_info["album"]["image"][-1]["#text"]
                if "duration" in track_info:
                    self.info["duration"] = track_info["duration"]
                if "toptags" in track_info and len(track_info["toptags"]["tag"]) > 0:
                    self.info["genre"] = track_info["toptags"]["tag"][0]["name"].capitalize()
        except requests.exceptions.ConnectionError:
            pass

    def id_track(self):
        return self.info.get("title", "") + self.info.get("artist", "")

    # Scrape track info from Tunein website
    def __update_tunein(self):
        try:
            html = requests.get(self.scraper["url"]).text
            match = re.search(r"<h3 class=\"title\">(.+?) - (.+?)</h3>", html)
            if match is not None:
                self.info["artist"] = unescape(match.group(1))
                self.info["title"] = unescape(match.group(2))
        except requests.exceptions.ConnectionError:
            pass


# Build a list of radio stations in the Kodi GUI
def build_list():
    source_list = [RadioSource(file) for file in sources]
    # Sort sources by XML <sort> property and then name
    source_list = sorted(source_list, key=lambda s: s.name)
    source_list = sorted(source_list, key=lambda s: float(s.info.get("sort", "Inf")))

    # Create list item for each source XML entry
    for source in source_list:
        li = source.list_item()
        xbmcplugin.addDirectoryItem(handle=handle, url=source.url, listitem=li, isFolder=False)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.endOfDirectory(handle)


def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string)


def urlencode(string):
    return requests.utils.quote(string.encode("utf8"))


# Request permission from user to modify skin files
def prompt_skinpatch():
    if addon.getSetting("skin-patch-prompt") == "true":
        if xbmcgui.Dialog().yesno(heading=addon.getAddonInfo("name"),
                                  line1=addon.getLocalizedString(30003),
                                  line2=addon.getLocalizedString(30004)):
            addon.setSetting("skin-patch", "true")
        addon.setSetting("skin-patch-prompt", "false")
    # Patch skin to allow track info to be displayed
    if addon.getSetting("skin-patch") == "true":
        skinpatch.SkinPatch().autopatch()


# Extract URL parameters
params = dict((key, value_list[0]) for key, value_list
              in urlparse.parse_qs(sys.argv[2][1:]).items())

# Load source filenames into list
sources = []
for source in os.listdir(sources_path):
    source_file = os.path.join(sources_path, source)
    if os.path.isfile(source_file):
        name, extension = os.path.splitext(source)
        if extension == ".xml":
            sources.append(name)

# Remove all skin patches
if params.get("action", None) == "unpatch":
    skinpatch.autoremove()
    addon.setSetting("skin-patch", "false")
    addon.setSetting("skin-patch-prompt", "true")
else:
    # Run addon
    if params.get("source", None) is None:
        build_list()
    else:
        prompt_skinpatch()
        RadioSource(params["source"]).play()
