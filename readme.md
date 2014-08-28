Overview
========

season_information.py
---------------------

Fetches season and episode information for a television show from TheTVDB.com.

### Arguments

Positional:
* The name of the television series.

Flags:
* -v, --dvd: List episodes by DVD order instead of aired order (if available).

label_episodes.py
-----------------

Renames media files in a directory to correspond to the episode list of a television show. (Useful when you want to correctly label episodes from ripped DVDs for use in Plex, for example.) Episode information is scraped from TheTVDB.com, via `season_information.py`.

### Arguments

Positional:
* The name of the television series.

Options:
* -d, --dir: The directory containing the media files. Defaults to present working directory.
* -s, --season: The season at which to begin episode enumeration. Defaults to season one.
* -e, --episode: The episode at which to begin enumeration. Defaults to episode one of the specified season.

Flags:
* -v, --dvd: List episodes by DVD order instead of aired order (if available).

### More Information

The `label_episodes.py` program will only rename files with the following extensions:

* .aaf
* .3gp
* .asf
* .avcd
* .avi
* .flv
* .mpg, .mpeg, .mpe
* .m4v
* .mkv
* .mov
* .ogg
* .swf
* .wmv

Files will be named in the following format:

```Python
FORMAT = "{series_name} s{season:02}e{episode:02} {episode_name}"
```

unpack.py
---------

This one's mostly just for me. It walks a directory tree and unpacks all RAR files it finds. Useful if your private tracker (or whatever) insists on putting every episode of something in its own RAR file in its own subdirectory. There are definitely more powerful (and more useful) tools out there, but this happens to be exactly what I need, so... meh.

### Arguments

Options:
* -d, --dir: The root directory at which to begin looking for RARs. Defaults to present working directory.
* -t, --target: The directory in which to place the unpacked files. Defaults to the aforementioned directory. (Not implemented yet!)

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Add directories by season (using os.renames, with constant for format).
* Add support for episodes that are "missing" (the user doesn't have the file: skip them in enumeration/labeling).
* Add support fo linked files (subtitle files, for example): if they have the same name, but different extension, treat them as a unit.

Known Bugs
----------

* UTF-8 encoded unicode (common with TheTVDB.com) messes with the character count in tables displayed by `season_information.py`.

TheTVDB.com
===========

All season and episode information is provided via [TheTVDB.com](http://thetvdb.com); please consider contributing to that project. You can find more information about TheTVDB.com's API [here](http://thetvdb.com/wiki/index.php?title=Programmers_API).

License Information
===================

Written by Gem Newman. [GitHub](https://github.com/spurll/) | [Blog](http://www.startleddisbelief.com) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
