import os
import xml.etree.ElementTree as et
import urlparse

import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmcvfs

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()


class RadioSource():
    def __init__(self, xml=None, name=None):
        if xml is None:
            # Load XML node from name
            for xml in sources.iter("radio"):
                if name == xml.find("name").text:
                    break

        self.name = xml.find("name").text
        self.streams = dict((int(stream.get("bitrate", default=0)), stream.text) for stream in xml.findall("stream"))
        self.info = dict((child.tag, child.text) for child in xml if child.tag not in ("name", "stream"))
        self.url = "{}?source={}".format(plugin_url, self.name)

    def list_item(self):
        li = xbmcgui.ListItem(self.name, iconImage="DefaultAudio.png")
        li.setInfo("music", {"title": self.name, "artist": self.info["tagline"]})
        li.setArt(self.__build_art())
        return li

    def __build_art(self):
        art = {}
        for art_type in ("thumb", "fanart"):
            if self.info.get(art_type, None) is not None:
                path = os.path.join(addon.getAddonInfo("path"), "artwork", self.info[art_type])
                if os.path.isfile(path):
                    art[art_type] = path


def build_list():
    xbmcplugin.setContent(handle, "audio")
    # Loop through sources XML and create list item for each entry
    for item in sources.iter("radio"):
        source = RadioSource(xml=item)
        li = source.list_item()
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=handle, url=source.url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(handle)


def play_source(name):
    # Loop through sources XML to find entry with specified name
    for source in sources.iter("radio"):
        if name == source.find("name").text:
            break

    # Find correct bitrate stream to play as per the maximum bitrate setting
    max_bitrate = int(addon.getSetting("bitrate").split(" ")[0])
    streams = dict((int(stream.get("bitrate", default=0)), stream.text) for stream in source.findall("stream"))
    bitrates = [bitrate for bitrate in streams.keys() if bitrate <= max_bitrate]
    url = streams[min(streams.keys())] if len(bitrates) == 0 else streams[max(bitrates)]

    li = create_list_item(source)
    li.setPath(url)
    xbmcplugin.setResolvedUrl(handle, True, li)


# Create sources file in addon_data folder
sources_path = os.path.join(addon.getAddonInfo("path"), "sources.xml")
if not xbmcvfs.exists(sources_path):
    xbmcvfs.copy(os.path.join(addon.getAddonInfo("path"), "resources", "sources.xml"), sources_path)

sources = et.fromstring(xbmcvfs.File(sources_path).read())
params = urlparse.parse_qs(sys.argv[2][1:])

if params.get("source", None) is None:
    build_list()
else:
    play_source(params["source"][0])
