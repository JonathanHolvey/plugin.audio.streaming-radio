# A custom internet radio addon for Kodi

This addon allows you to specify custom internet radio streams and add artwork to them. This provides a slightly nicer interface for custom radio streams than scanning .strm files into the Kodi library, as recommended in the [Kodi wiki](http://kodi.wiki/view/internet_video_and_audio_streams).

![Buddha Radio][screenshot]  
*Buddha Radio playing in the Xperience1080 skin*

## Adding streams

Radio streams can be added to the addon by specifying them in XML files in the `sources` folder, which can be found in the root of the addon. An example radio station `buddha.xml` is included, which can be used as a starting point:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<source>
	<stream bitrate="128">http://stream.scahw.com.au/live/buddha_128.stream/playlist.m3u8</stream>
	<stream bitrate="32">http://stream.scahw.com.au/live/buddha_32.stream/playlist.m3u8</stream>
	<name>Buddha Radio</name>
	<tagline>Tune in, chill out</tagline>
	<description>Chill Out Digital Radio - Buddha Radio has a very simple philosophy...</description>
	<fanart>buddha-fanart.jpg</fanart>
	<thumb>buddha-thumb.png</thumb>
</source>
```

A new radio station can be added by creating a new XML file (or copying an existing one), and filling in the `name` field with the name of the radio station. The stream URL should be specified in the `stream` field. Multiple stream URLs can be provided in separate XML nodes, with the bitrate specified in the `bitrate` attribute of each. The bitrate is used in conjunction with the *Maximum bitrate* setting to choose an appropriate stream URL.

## Adding artwork

Artwork images for the radio station should be placed inside the `artwork` folder, and the filenames added to the `fanart` and `thumb` fields in the source file. Other artwork types can also be defined, however they have not been tested.

## Track info

The Streaming Radio addon allows the scraping of now playing track infomation from the [Tunein website](http://tunein.com), however getting this information to show up in your Kodi skin is not straightforward.

Since there is no standard way of pushing track info to the Kodi OSD, the skin must be modified to allow the information to be displayed. Currently, support is provided for the Xperience1080 skin, through a patch file which is shipped with the addon. This can be found in the `resources/skins` folder, and once applied, the current artist's name and the track title will be displayed in the skin.

A track info scraper can be defined for a radio station by supplying a `<scraper>` node in the XML source file:

```xml
<source>
	...
	<scraper type="tunein">
		<url>http://tunein.com/radio/Buddha-Radio-s172072/</url>
	</scraper>
</source>
```

The `url` can be found by searching for your radio station on the Tunein website and copying the URL from your browser's address bar. If the track info is displayed on the Tunein website, then it should be scraped into Kodi successfully.

### To do:

1. Pull track artwork from the web and display it in the skin
2. Increase the time between requests to tunein.com by looking up the track's duration and predicting when it will end
3. Implement a more elegent track info scraper (using, for example Lightstreamer) for radio stations which support it
4. Apply a delay to the track info change to sync it with the audio (Tunein updates10-15 seconds before the track changes)
5. Improve skin integration
6. Automatically apply skin patches on first run
7. Add support for other skins - pull requests welcome

## Licence

This software is distributed under the GNU General Public License v3. Copyright 2016 Jonathan Holvey.

[screenshot]: http://i.imgur.com/UbNqJ6X.png
