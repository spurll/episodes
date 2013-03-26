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

Renames media files in a directory to correspond to the episode list of a television show. (Useful when you want to correctly label episodes from ripped DVDs for use in Plex, for example.) Episode information is scraped from TheTVDB.com, via season_information.py.

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

The label_episodes.py program will only rename files with the following extensions:

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

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Add directories by season (using os.renames, with constant for format).
* Add support for episodes that are "missing" (the user doesn't have the file: skip them in enumeration/labeling).
* Add support fo linked files (subtitle files, for example): if they have the same name, but different extension, treat them as a unit.

Known Bugs
----------

* UTF-8 encoded unicode (common with TheTVDB.com) messes with the character count in tables displayed by season_information.py.

TheTVDB.com
===========

All season and episode information is provided via TheTVDB.com; please consider contributing to that project. For more information about TheTVDB.com's API, visit:
http://thetvdb.com/wiki/index.php?title=Programmers_API

License Information
===================

Written by Gem Newman.
http://www.startleddisbelief.com

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
