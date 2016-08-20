import os
import xml.etree.ElementTree as et

import xbmcgui
import xbmcaddon
import xbmcplugin

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, "audio")

addon = xbmcaddon.Addon(id="plugin.audio.streaming-radio")

sources = et.parse(os.path.join(addon.getAddonInfo("path"), "sources.xml"))
# Loop through sources XML and create list item for each entry
for source in sources.iter("radio"):
    url = source.find("stream").text
    li = xbmcgui.ListItem(source.find("name").text, iconImage="DefaultAudio.png")
    li.setInfo("music", {
        "title": source.find("name").text,
        "artist": source.find("tagline").text
    })
    li.setArt({
        "thumb": os.path.join(addon.getAddonInfo("path"), "artwork", source.find("thumbnail").text),
        "fanart": os.path.join(addon.getAddonInfo("path"), "artwork", source.find("fanart").text)
    })
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li)

xbmcplugin.endOfDirectory(handle)