# For more information about TheTVDB.com's API, visit
# http://thetvdb.com/wiki/index.php?title=Programmers_API


# TO DO:
#   Make season_information a separate module.
#   Either add file types to ignore or file types to include (not whole dir).
#   Add directories by season (using os.renames, with constant for format).


import argparse, urllib2, os, re, datetime, random, xml.etree.ElementTree as et
from table import table, menu


WORD_SEPARATOR = " "            # Replaces all spaces with this character.
DESCRIPTION_LIMIT = 80          # Number of characters to display.
DATE_FORMAT = "{:%d %B %Y}"     # For viewing air date in season information.
FILE_FORMAT = "{series_name} s{season:02}e{episode:02} {episode_name}"

KEY = "F6C8EF890E843081"
MIRROR_URL = "http://thetvdb.com/api/{key}/mirrors.xml"
SERIES_URL = '{mirror}/api/GetSeries.php?seriesname="{name}"'
EPISODE_URL = "{mirror}/api/{key}/series/{series_id}/all/en.xml"


def season_information(series):
    # Randomly selects a mirror to connect to.
    response = urllib2.urlopen(MIRROR_URL.format(key=KEY))
    xml = response.read()
    root = et.fromstring(xml)

    mirrors = root.findall("Mirror")
    if len(mirrors) < 1:
        print "Warning: No mirrors found. Failing over to TheTVDB.com..."
        mirror = "http://thetvdb.com"
    else:
        mirror = grab(mirrors[random.randint(0, len(mirrors) - 1)],
                      "mirrorpath")
        print "Mirror: {}".format(mirror)

    # Identify the series by name, and retrieve its ID from TheTVDB.com.
    print "Search: {}".format(series)

    series = series.replace(" ", "%20")
    response = urllib2.urlopen(SERIES_URL.format(mirror=mirror, name=series))
    xml = response.read()
    root = et.fromstring(xml)

    series = root.findall("Series")

    if len(series) == 1:
        series_id = grab(series[0], "seriesid")
        series_name = grab(series[0], "SeriesName")

    else:
        rows = []
        for i in xrange(len(series)):
            name = grab(series[i], "SeriesName")
            aired = grab(series[i], "FirstAired")
            if aired is not None:
                aired = "{:%Y}".format(datetime.datetime.strptime(aired,
                                       "%Y-%m-%d"))
            rows.append((i + 1, name, aired))

        choice = menu("Matches", *zip(*rows), headers=["#", "Series Name",
                      "First Aired"], input_range=range(1, len(series) + 1),
                      footer="To select a series, enter its number.")
        series_id = grab(series[int(choice) - 1], "seriesid")
        series_name = grab(series[int(choice) - 1], "SeriesName")

    print "Series Name: {}".format(series_name)
    print "Series ID: {}".format(series_id)

    # Retrieve the episode list for the series.
    response = urllib2.urlopen(EPISODE_URL.format(mirror=mirror, key=KEY,
                               series_id=series_id))
    xml = response.read()
    root = et.fromstring(xml)

    episodes = [{"season": grab(e, "SeasonNumber", int),
                "episode": grab(e, "EpisodeNumber", int),
                "name": grab(e, "EpisodeName"),
                "date": grab(e, "FirstAired", lambda d: DATE_FORMAT.format(
                             datetime.datetime.strptime(d, "%Y-%m-%d"))),
                "description": grab(e, "Overview")}
                for e in root.findall("Episode")]

    # Show table of seasons, with the number of episodes in them.
    episodes.sort(key=lambda e: e["episode"])
    episodes.sort(key=lambda e: e["season"])

    season_list = list({e["season"] for e in episodes})
    season_list.sort()

    # Turn episodes into a dictionary, organizing the episodes into seasons.
    # The reason I chose a dict of lists, rather than a list of lists, is
    # because some shows have a season 0 (which usually means specials, etc.),
    # while others start at season 1. A dict allows us to index directly to
    # season 1 in either case.
    episodes = {s: [e for e in episodes if e["season"] == s]
                for s in season_list}

    # Optionally display episode information for each season.
    done = False
    while not done:
        s = menu("Season Information", season_list, [len(episodes[s]) for s in
                 season_list], headers=["Season", "Episodes"],
                 footer="Enter a season number for more information. (ENTER to"
                 " continue.)", input_range=season_list+[""])
        if s:
            s = int(s)
            rows = [(e["episode"], e["name"], e["date"],
                    short_description(e["description"])) for e in episodes[s]]
            #print rows
            menu("Season {}".format(s), *zip(*rows), headers=["Episode",
                 "Name", "Air Date", "Description"],
                 footer="ENTER to continue.")
        else:
            done = True

    return episodes


def label_episodes(series, directory, season):
    episodes = season_information(series)

    files = os.listdir(directory)
    files.sort()

    rename = []
    s, e = season, 0
    print 'Found {} episodes in directory "{}".'.format(len(files), directory)
    print "Identifying episodes in season {}...".format(s)

    for f in files:
        if e >= len(episodes[s]):
            e = 0
            s += 1
            print "Moving on to season {}...".format(s)

        if s not in episodes:
            print "Error: No information on season {} exists."
            return

        ext = re.search(r"\.[^\.]+$",f)
        if not ext:
            print 'Warning: Unable to determine file type for "{}".'.format(f)
            rename.append((f, f))
            continue

        ext = ext.group(0)
        file_name = FILE_FORMAT.format(series_name=series, season=s,
                                       episode=episodes[s][e]["episode"],
                                       episode_name=episodes[s][e]["name"])
        file_name = file_name.replace(" ", WORD_SEPARATOR)
        file_name = "".join([file_name, ext])
        file_name = os.path.join(directory, file_name)
        rename.append((os.path.join(directory, f), file_name))

        e += 1

    print "{} episodes were identified in seasons {} through {}.".format(
          len(files), season, s)

    choice = menu("Confirm New File Names", *zip(*rename),
                  headers=["Current Name", "New Name"],
                  input_range=["yes", "y", "no", "n"], footer="Would you like "
                  "to proceed with renaming the files? (yes/no)")

    if choice[0] == "n":
        return

    for r in rename:
        print "Renaming {} to {}...".format(*r)
        os.rename(*r)

    print "Done."


def grab(parent, child, convert=None):
    child = parent.find(child)
    if child is not None: child = child.text
    if child is not None:
        if convert: child = convert(child)
        else: child = child.encode("utf-8")     # Important. Watch for Unicode.
    return child


def short_description(description):
    if description:
        description = description.replace("\n", " ")
        if len(description) > DESCRIPTION_LIMIT:
            description = description[0:DESCRIPTION_LIMIT-2]
            description = re.sub(r"\W+\w*$", r"...", description)
    return description


if __name__ == "__main__":
    description = "Renames media files in a directory to correspond to the "  \
                  "episode list of a television show. Episode information is "\
                  "scraped from TheTVDB.com. Please consider contributing."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("series", help="The name of the television series.",
                        nargs="+")
    parser.add_argument("-d", "--dir", help="The directory containing the "
                        "media files. (All files will be renamed!) Defaults to"
                        "present working directory.", default="./")
    parser.add_argument("-s", "--season", help="The season at which to begin "
                        "episode enumeration. Defaults to the first season.",
                        type=int, default=1)
    args = parser.parse_args()

    label_episodes(" ".join(args.series), args.dir, args.season)
