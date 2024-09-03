#!/usr/bin/env python3

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.


import argparse, requests, datetime, random, re, os
import xml.etree.ElementTree as et
from table import table, menu


KEYPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apikey')

with open(KEYPATH, 'r') as file:
    KEY = file.read().replace('\n', '')

DATE_FORMAT = "{:%d %B %Y}"     # For viewing air date in season information.
DESCRIPTION_LIMIT = 80          # Number of characters to display.

DVD_S = "DVD_season"            # XML identifier for DVD season number.
DVD_E = "DVD_episodenumber"     # XML identifier for DVD episode number.
SEASON = "SeasonNumber"         # XML identifier for (aired) season number.
EPISODE = "EpisodeNumber"       # XML identifier for (aired) episode number.
EPISODE_NAME = "EpisodeName"    # XML identifier for episode name.
AIR_DATE = "FirstAired"         # XML identifier for air date.
DESCRIPTION = "Overview"        # XML identifier for episode description.

SERIES_URL = 'https://thetvdb.com/api/GetSeries.php?seriesname="{name}"'
EPISODE_URL = "https://thetvdb.com/api/{key}/series/{series_id}/all/en.xml"


def season_information(series, dvd, display=False):
    # Identify the series by name, and retrieve its ID from TheTVDB.com.
    print(f"Search: {series}")

    series = series.replace(" ", "%20")
    header = {"User-Agent": "Season Information"}

    # Retrieve series information.
    response = requests.get(SERIES_URL.format(name=series), headers=header)

    xml = response.text
    root = et.fromstring(xml)

    series = root.findall("Series")

    if len(series) == 1:
        series_id = grab(series[0], "seriesid")
        series_name = grab(series[0], "SeriesName")

    else:
        rows = []
        for i in range(len(series)):
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

    print(f"Series Name: {series_name}")
    print(f"Series ID: {series_id}")

    # Retrieve the episode list for the series.
    response = requests.get(EPISODE_URL.format(key=KEY, series_id=series_id),
        headers=header)

    xml = response.text
    root = et.fromstring(xml)

    episodes = [{"season": grab(e, SEASON, int),
                "episode": grab(e, EPISODE, int),
                "dvd_season": grab(e, DVD_S, int),
                "dvd_episode": grab(e, DVD_E, int),
                "name": grab(e, EPISODE_NAME),
                "date": grab(e, AIR_DATE, lambda d: DATE_FORMAT.format(
                    datetime.datetime.strptime(d, "%Y-%m-%d"))),
                "description": grab(e, DESCRIPTION)}
                for e in root.findall("Episode")]

    if dvd:
        dvd_episodes = [{"season": e["dvd_season"],
                        "episode": e["dvd_episode"],
                        "name": e["name"],
                        "date": e["date"],
                        "description": e["description"]}
                        for e in episodes if e["dvd_season"] is not None and
                        e["dvd_episode"] is not None]

        # If no DVD information is defined, just use the aired information.
        if dvd_episodes: episodes = dvd_episodes

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
    while display:
        s = menu("Season Information", season_list, [len(episodes[s]) for s in
                 season_list], headers=["Season", "Episodes"],
                 footer="Enter a season number for more information. (ENTER to"
                 " continue.)", input_range=season_list+[""])
        if s:
            s = int(s)
            rows = [(e["episode"], e["name"], e["date"],
                    short_description(e["description"])) for e in episodes[s]]
            menu("Season {}".format(s), *zip(*rows), headers=["Episode",
                 "Name", "Air Date", "Description"],
                 footer="ENTER to continue.")
        else:
            display = False

    return episodes


def grab(parent, child, convert=None):
    child = parent.find(child)
    if child is not None: child = child.text
    if child is not None:
        if convert:
            if convert == int and "." in child:
                # Why would an episode number be stored as a float?
                # Because fuck you, that's why.
                child = int(float(child))
            else:
                child = convert(child)

    return child


def short_description(description):
    if description:
        description = description.replace("\n", " ")
        if len(description) > DESCRIPTION_LIMIT:
            description = description[0:DESCRIPTION_LIMIT-2]
            description = re.sub(r"\W+\w*$", r"...", description)
    return description


if __name__ == "__main__":
    description = "Fetches season and episode information from TheTVDB.com. " \
                  "Please consider contributing."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("series", help="The name of the television series.",
                        nargs="+")
    parser.add_argument("-v", "--dvd", help="List episodes by DVD order, if "
                        "available.", action="store_true")
    args = parser.parse_args()

    season_information(" ".join(args.series), args.dvd, display=True)
