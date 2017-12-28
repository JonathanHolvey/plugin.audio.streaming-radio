# A custom internet radio addon for Kodi

This addon allows you to specify custom internet radio streams and add artwork to them. In addition, it can find out information about a track that's being played, and display information about it in Kodi's OSD (with supported skins). This provides a far nicer interface for custom radio streams than scanning .strm files into the Kodi library, as recommended in the [Kodi wiki](http://kodi.wiki/view/internet_video_and_audio_streams).

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
	<genre>Chillout</genre>
	<fanart>buddha-fanart.jpg</fanart>
	<thumb>buddha-thumb.png</thumb>
</source>
```

A new radio station can be added by creating a new XML file (or copying an existing one), and filling in the `name` field with the name of the radio station. The stream URL should be specified in the `stream` field. Multiple stream URLs can be provided in separate `stream` nodes, with the bitrate specified in the `bitrate` attribute of each. The bitrate is used in conjunction with the *Maximum bitrate* setting to choose an appropriate stream URL.

## Adding artwork

Artwork images for the radio station should be placed inside the `artwork` folder, and the filenames added to the `fanart` and `thumb` fields in the source file. Other artwork types can also be defined, however they have not been tested.

## Track information

The Streaming Radio addon allows the scraping of now playing track infomation from the [Tunein website](http://tunein.com).

Since there is no standard way of pushing track info to the Kodi OSD, the skin is modified automatically to allow the information to be displayed. This is achieved through a patch file which is shipped with the addon, and applied to the skin the first time playback is started.

*Note that Xperience1080 is the only skin that currently supports displaying track information.*

A track info scraper can be defined for a radio station by supplying a `<scraper>` node in the XML source file:

```xml
<source>
	...
	<scraper type="tunein">
		<url>http://tunein.com/radio/Buddha-Radio-s172072/</url>
		<delay>20</delay>
	</scraper>
</source>
```

The `url` can be found by searching for your radio station on the Tunein website and copying the URL from your browser's address bar. If the track info is displayed on the Tunein website, then it should be scraped into Kodi successfully. The `delay` property is optional, and allows you to sync the track info change with the audio, in the case where the scraper source changes first. The delay is specified in seconds.

## Sorting

By default, radio stations are sorted alphabetically by the station name. This behaviour can be modified by providing a `<sort>` node in the source XML file, which will be used to assist the default sorting. Lower `sort` values will be placed toward the top of the list. Stations which share the same `sort` value (including those with no value at all) will also be sorted alphabetically within the list. The `sort` property should be provided as a decimal number, eg `1` or `1.2`.

```xml
<source>
	...
	<sort>1</sort>
</source>
```

Stations can also be sorted by name only (ignoring `sort`) and by genre, using the options available in the Kodi GUI.

### To do:

1. ~~Pull track artwork from the web and display it in the skin~~ *Done*
2. Increase the time between requests to tunein.com by looking up the track's duration and predicting when it will end
3. Implement a more elegent track info scraper (using, for example Lightstreamer) for radio stations which support it
4. ~~Apply a delay to the track info change to sync it with the audio (Tunein updates \~20 seconds before the track changes)~~ *Done*
5. ~~Show more track information in the OSD~~ *Done*
6. ~~Automatically apply skin patch on first run~~ *Done*
7. Add support for other skins - pull requests welcome
8. Show track progress and end time in the OSD

## Licence

This software is distributed under the GNU General Public License v3. Copyright 2016-2018 Jonathan Holvey.

[screenshot]: http://i.imgur.com/ITegNCy.png
