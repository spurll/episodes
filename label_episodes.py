# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

# For more information about TheTVDB.com's API, visit
# http://thetvdb.com/wiki/index.php?title=Programmers_API

# TO DO:
#   Either add file types to ignore or file types to include (not whole dir).
#     (At the very least, exclude directories!)
#   Add directories by season (using os.renames, with constant for format).
#   Add support for "missing" episodes (skip them).


import argparse, os, re, string
from table import table, menu
from season_information import season_information


FILE_FORMAT = "{series_name} s{season:02}e{episode:02} {episode_name}"

RESERVED_CHARACTERS = r'/\?%*:|"<>' # These are removed from file names.
WORD_SEPARATOR = " "                # Spaces are replaced by this character.
REPLACE = ("/", "&")                # First characters replaced with second.


def label_episodes(series, directory, season, episode, dvd):
    episodes = season_information(series, dvd)

    if season not in episodes:
        print "No information found for season {}.".format(season)
        return

    files = os.listdir(directory)
    files.sort()

    rename = []
    s, e = season, episode - 1
    print 'Found {} episodes in directory "{}".'.format(len(files), directory)
    print "Identifying episodes in season {}...".format(s)

    for f in files:
        if e >= len(episodes[s]):
            if s + 1 in episodes:
                e = 0
                s += 1
                print "Moving on to season {}...".format(s)
            else:
                print "Unable to rename {}: no episodes remain.".format(f)
                rename.append((f, None))
                continue

        ext = re.search(r"\.[^\.]+$",f)
        if not ext:
            print 'Warning: Unable to determine file type for "{}".'.format(f)
            rename.append((f, None))
            continue

        file_name = create_file_name(series, episodes[s][e], ext.group(0))
        rename.append((f, file_name))

        e += 1

    choice = menu("Confirm New File Names", *zip(*rename),
                  headers=["Current Name", "New Name"],
                  input_range=["yes", "y", "no", "n"], footer="Would you like "
                  "to proceed with renaming the files? (yes/no)")

    if choice[0] == "n":
        return

    for r in rename:
        if r[1]:
            print "Renaming {} to {}...".format(*r)
            os.rename(os.path.join(directory, r[0]), os.path.join(directory,
                r[1]))
        else:
            print "Skipping {}...".format(r[0])

    print "Done."


def create_file_name(series, episode, extension):
    file_name = FILE_FORMAT.format(series_name=series,
                                   season=episode["season"],
                                   episode=episode["episode"],
                                   episode_name=episode["name"])

    if REPLACE:
        translator = string.maketrans(*REPLACE)
        file_name = file_name.translate(translator, "")

    # Remove reserved characters (and spaces, if necessary)
    translator = string.maketrans(" ", WORD_SEPARATOR)

    file_name = file_name.translate(translator, RESERVED_CHARACTERS)
    file_name = "".join([file_name, extension])

    return file_name


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
                        "episode enumeration. Defaults to the season one.",
                        type=int, default=1)
    parser.add_argument("-e", "--episode", help="The episode at which to begin"
                        " enumeration. Defaults to episode one of the "
                        "specified season.", type=int, default=1)
    parser.add_argument("-v", "--dvd", help="List episodes by DVD order, if "
                        "available.", action="store_true")
    args = parser.parse_args()

    label_episodes(" ".join(args.series), args.dir, args.season, args.episode,
                   args.dvd)
