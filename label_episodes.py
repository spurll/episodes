#!/usr/bin/env python

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

# For more information about TheTVDB.com's API, visit
# http://thetvdb.com/wiki/index.php?title=Programmers_API


import argparse, os, re, string
from os.path import join
from table import table, menu
from season_information import season_information


FILE_FORMAT = "{series_name} S{season:02}E{episode:02} {episode_name}"
FILE_TYPES = {'.avi', '.divx', '.flv', '.mpg', '.mpeg', '.m4v', '.mp4', '.mkv',
              '.mov', '.ogg', '.swf', '.wmv'}

RESERVED_CHARACTERS = r'/\?%*:|"<>' # These are removed from file names.
WORD_SEPARATOR = " "                # Spaces are replaced by this character.
REPLACE = ("/", "&")                # First characters replaced with second.


def label_episodes(series, directory, start, missing, dvd):
    start = parse_ep(start)
    missing = set(map(parse_ep, missing))

    # Seasons start at 0 (for "Specials"), episodes start at 1
    episodes = season_information(series, dvd)

    if start[0] not in episodes:
        print "No information found for season {}.".format(start[0])
        return

    files = os.listdir(directory)

    # Remove directories and files that don't match the pattern, if any.
    files = [f for f in files if os.path.isfile(os.path.join(directory, f)) and
             extension(f).lower() in FILE_TYPES]

    if len(files) < 1:
        print 'Found no media files in "{}".'.format(directory)
        return

    print 'Found {} media files in "{}".'.format(len(files), directory)

    files.sort()

    done = False
    while not done:
        # Map the files to the list of episodes
        rename = files2episodes(series, episodes, files, missing, start)
        index = file_index(rename)

        choice = menu(
            "Confirm New File Names",
            *zip(*rename),
            headers=["Episode", "Current Name", "New Name"],
            input_range=["", "m", "s", "r", "q", "x"],
            footer="What would you like to do?"
                "\nENTER: Proceed with renaming"
                "\n    M: Mark missing episodes"
                "\n    S: Skip (ignore) files"
                "\n    R: Re-order files"
                "\n  X/Q: Exit"
        )

        if choice == "":
            for r in rename:
                if r[2]:
                    print "Renaming {} to {}...".format(r[1], r[2])
                    os.rename(join(directory, r[1]), join(directory, r[2]))
                else:
                    print "Skipping {}...".format(r[0])
            done = True

        elif choice in ("q", "x"):
            done = True

        elif choice == "m":
            selection = menu(
                "Mark Missing Episodes",
                *zip(*rename),
                headers=["Episode", "Current Name", "New Name"],
                footer="Enter episode numbers (S##E##) to mark missing files."
            )

            miss = map(parse_ep, selection.upper().replace(",", " ").split())
            for m in miss:
                missing.add(m)

        elif choice == "s":
            selection = menu(
                "Ignore Files",
                index,
                *zip(*rename),
                headers=["Index", "Episode", "Current Name", "New Name"],
                footer="Enter the indices of the files you would like to skip."
            )

            skip = map(int, selection.replace(",", " ").split())
            files = [f for i, f in enumerate(files) if i + 1 not in skip]

        elif choice == "r":
            source = menu(
                "Change File Order",
                index,
                *zip(*rename),
                headers=["Index", "Episode", "Current Name", "New Name"],
                input_range=index + [""],
                footer="Enter the index of the file you would like to move."
            )

            if source == "": continue

            destination = None
            print "Which index would you like to move it to?"
            while not destination in index + [""]:
                destination = raw_input(">> ")

            if destination == "": continue

            files.insert(int(destination) - 1, files.pop(int(source) - 1))

    print "Done."


def files2episodes(series, episodes, files, missing, start):
    rename = []
    s, e = start

    print "Identifying episodes in season {}...".format(s)

    for f in files:
        # Skip any episodes that are marked as "missing"
        while (s, e) in missing:
            rename.append(('S{:02}E{:02}'.format(s, e), None, None))
            e += 1

        if e > len(episodes[s]):
            if s + 1 in episodes:
                e = 1
                s += 1
                print "Moving on to season {}...".format(s)
            else:
                print "Unable to rename {}: no episodes remain.".format(f)
                rename.append(('S{:02}E{:02}'.format(s, e), f, None))
                continue

        file_name = create_file_name(series, episodes[s][e - 1], extension(f))
        rename.append(('S{:02}E{:02}'.format(s, e), f, file_name))

        e += 1

    return rename


def extension(f):
    ext = re.search(r"\.[^\.]+$", f)
    if ext: ext = ext.group(0)
    return ext


def find_ep(f):
    ep = re.search(r"[sS][0-9]+[eE][0-9]+", f)
    if ep: ep = ep.group(0)
    return ep


def parse_ep(f):
    ep = re.search(r"[sS]([0-9]+)[eE]([0-9]+)", f)
    if ep: ep = (int(ep.group(1)), int(ep.group(2)))
    return ep


def file_index(rename):
    index = []
    current = 1
    for row in rename:
        if row[1]:
            index += [str(current)]
            current += 1
        else:
            index += ""

    return index


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
                        " present working directory.", default="./")
    parser.add_argument("-s", "--start", help="The season and episode at which"
                        " to begin enumeration in S##E## format. Defaults to "
                        "S01E01", default="S01E01")
    parser.add_argument("-m", "--missing", help="A list of episodes for which "
                        "files are missing in S##E## format. These episode "
                        "numbers will be skipped.", nargs="*", default=[])
    parser.add_argument("-v", "--dvd", help="Use DVD instead of aired order, "
                        "if available.", action="store_true")
    args = parser.parse_args()

    label_episodes(" ".join(args.series), args.dir, args.start, args.missing,
                   args.dvd)
