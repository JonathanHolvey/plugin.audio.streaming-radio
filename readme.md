# A custom internet radio addon for Kodi

This addon allows you to specify custom internet radio streams and add artwork to them. This provides a slightly nicer interface for custom radio streams than scanning .strm files into the Kodi library, as recommended in the [Kodi wiki](http://kodi.wiki/view/internet_video_and_audio_streams).

![Buddha Radio][screenshot]  
*Buddha Radio playing in the Xperience1080 skin*

## Adding streams

Radio streams can be added to the addon by specifying them in the sources file `sources.xml`, which can be found in the root of the addon folder. This file is created the first time the addon is run, and includes an example radio station which can be used as a starting point:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sources>
	<radio>
		<stream bitrate="128">http://stream.scahw.com.au/live/buddha_128.stream/playlist.m3u8</stream>
		<stream bitrate="32">http://stream.scahw.com.au/live/buddha_32.stream/playlist.m3u8</stream>
		<name>Buddha Radio</name>
		<tagline>Tune in, chill out</tagline>
		<description>Chill Out Digital Radio - Buddha Radio has a very simple philosophy...</description>
		<fanart>buddha-fanart.jpg</fanart>
		<thumb>buddha-thumb.png</thumb>
	</radio>
</sources>
```

A new radio station can be added by creating a new `<radio>...</radio>` section (or copying an existing one), and filling in the `name` field with the name of the radio station. The stream URL should be specified in the `stream` field. Multiple stream URLs can be provided in separate XML nodes, with the bitrate specified in the `bitrate` attribute of each. The bitrate is used in conjunction with the *Maximum bitrate* setting to choose an appropriate stream URL.

## Adding artwork

Artwork images should be placed inside the `artwork` folder, and the filenames added to the `fanart` and `thumb` fields in `sources.xml`.

[screenshot]: http://i.imgur.com/UbNqJ6X.png