import os
import xml.etree.ElementTree as et
import urlparse
import shutil
import requests
import re
import HTMLParser

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from resources.lib.skinpatch import SkinPatch

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
        self.streams = dict((int(stream.get("bitrate", default=0)), stream.text) for stream in xml.findall("stream"))
        self.info = dict((child.tag, child.text) for child in xml if child.tag not in ("name", "stream", "scraper"))
        self.url = "{}?source={}".format(plugin_url, file)

        # Load scraper properties
        if xml.find("scraper") is not None:
            self.scraper = dict((child.tag, child.text) for child in xml.find("scraper"))
            self.scraper["type"] = xml.find("scraper").get("type", default=None)
        else:
            self.scraper = None

    # Generate a Kodi list item from the radio source
    def list_item(self):
        li = xbmcgui.ListItem(self.name, iconImage="DefaultAudio.png")
        li.setInfo("music", {"title": self.name, "artist": self.info.get("tagline", None)})
        li.setArt(self.__build_art())
        return li

    # Start playing the radio source
    def play(self):
        # Detect correct bitrate stream to play
        max_bitrate = int(addon.getSetting("bitrate").split(" ")[0])
        bitrates = [bitrate for bitrate in self.streams.keys() if bitrate <= max_bitrate]
        url = streams[min(self.streams.keys())] if len(bitrates) == 0 else self.streams[max(bitrates)]

        # Create list item with stream URL and send to Kodi
        li = self.list_item()
        li.setPath(url)
        xbmcplugin.setResolvedUrl(handle, True, li)

        # Start scraping track info
        if self.scraper is not None:
            InfoScraper(self, url).run()

    # Create dictionary of available artwork files to supply to list item
    def __build_art(self):
        art = {}
        for art_type in ("thumb", "fanart", "poster", "banner", "clearart", "clearlogo", "landscape", "icon"):
            if self.info.get(art_type, None) is not None:
                path = os.path.join(addon.getAddonInfo("path"), "artwork", self.info[art_type])
                if os.path.isfile(path):
                    art[art_type] = path
        return art


class InfoScraper():
    def __init__(self, source, stream):
        self.properties = source.scraper
        self.stream = stream
        self.window = xbmcgui.Window(10000)  # Attach properties to the home window
        self.window_properties = []

    def update(self):
        if self.properties["type"] == "tunein":
            return self.__update_tunein()

    def run(self):
        xbmc.sleep(5000)  # Wait for playback to start
        # Retrieve track information every 10 seconds until playback stops
        while xbmc.Player().isPlayingAudio() and xbmc.Player().getPlayingFile() == self.stream:
            try:
                artist, title = self.update()
                self.set_window_property("Artist", artist)
                self.set_window_property("Title", title)
            except:
                pass
            xbmc.sleep(10000)

        # Remove window properties after playback stops
        self.clear_window_properties()

    def set_window_property(self, name, value):
        name = addon.getAddonInfo("id") + "." + name
        self.window.setProperty(name, value)
        if name not in self.window_properties:
            self.window_properties.append(name)

    def clear_window_properties(self):
        for name in self.window_properties:
            self.window.clearProperty(name)

    # Scrape track info from Tunein website
    def __update_tunein(self):
        html = requests.get(self.properties["url"]).text
        match = re.search(r"<h3 class=\"title\">(.+?) - (.+?)</h3>", html)
        if match is not None:
            return unescape(match.group(1)), unescape(match.group(2))


# Build a list of radio stations in the Kodi GUI
def build_list():
    xbmcplugin.setContent(handle, "audio")
    # Loop through sources XML and create list item for each entry
    for file in sources:
        source = RadioSource(file)
        li = source.list_item()
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=handle, url=source.url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(handle)


def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string)


# Request permission from user to modify skin files
def prompt_skinpatch():
    if addon.getSetting("skin-patch-prompt") == "true":
        if xbmcgui.Dialog().yesno(heading=addon.getAddonInfo("name"), line1=addon.getLocalizedString(30003),
                line2=addon.getLocalizedString(30004)):
            addon.setSetting("skin-patch", "true")
        addon.setSetting("skin-patch-prompt", "false")
    # Patch skin to allow track info to be displayed
    if addon.getSetting("skin-patch") == "true":
        SkinPatch().sideload()


# Extract URL parameters
params = dict((key, value_list[0]) for key, value_list in urlparse.parse_qs(sys.argv[2][1:]).items())

# Load source filenames into list
sources = []
for source in os.listdir(sources_path):
    source_file = os.path.join(sources_path, source)
    if os.path.isfile(source_file):
        name, extension = os.path.splitext(source)
        if extension == ".xml":
            sources.append(name)

# Run addon
if params.get("source", None) is None:
    build_list()
else:
    prompt_skinpatch()
    RadioSource(params["source"]).play()
