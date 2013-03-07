# For more information about TheTVDB.com's API, visit
# http://thetvdb.com/wiki/index.php?title=Programmers_API

# Write Python script to scrape the TVDb and rename all files in a directory.
# Assume they sort correctly. Give a season to start with. If the episode count
# wouldn't end at the end of a season, give a warning.



if __name__ == "__main__":
    description = "Renames media files in a directory to correspond to the "
                  "episode list of a television show. Episode information is "
                  "scraped from TheTVDB.com. Please consider contributing."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("series", help="The name of the television series.")
    parser.add_argument("-d", "--dir", help="The directory containing the "
                        "media files. (All files will be renamed!) Defaults to"
                        "present working directory.", default="./")
    parser.add_argument("-s", "--season", help="The season at which to begin "
                        "episode enumeration. Defaults to the first season.",
                        type=int, default=1)
