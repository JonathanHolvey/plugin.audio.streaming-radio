import os
import xml.etree.ElementTree as et
import urlparse

import xbmcgui
import xbmcaddon
import xbmcplugin

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()


def create_list_item(source):
    li = xbmcgui.ListItem(source.find("name").text, iconImage="DefaultAudio.png")
    li.setInfo("music", {
        "title": source.find("name").text,
        "artist": source.find("tagline").text
    })
    li.setArt({
        "thumb": os.path.join(addon.getAddonInfo("path"), "artwork", source.find("thumbnail").text),
        "fanart": os.path.join(addon.getAddonInfo("path"), "artwork", source.find("fanart").text)
    })
    return li


def build_list():
    xbmcplugin.setContent(handle, "audio")
    # Loop through sources XML and create list item for each entry
    for source in sources.iter("radio"):
        li = create_list_item(source)
        li.setProperty("IsPlayable", "true")
        url = "{}?source={}".format(plugin_url, source.find("name").text)
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(handle)


def play_source(name):
    # Loop through sources XML to find entry with specified name
    for source in sources.iter("radio"):
        if name == source.find("name").text:
            break
    li = create_list_item(source)
    url = source.find("stream").text
    li.setPath(url)
    xbmcplugin.setResolvedUrl(handle, True, li)


sources = et.parse(os.path.join(addon.getAddonInfo("path"), "sources.xml"))
params = urlparse.parse_qs(sys.argv[2][1:])

if params.get("source", None) is None:
    build_list()
else:
    play_source(params["source"][0])
