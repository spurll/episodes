# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.


import argparse, os, re, subprocess
from label_episodes import extension


def unpack(directory, target):
    directory = os.path.expanduser(directory)
    target = os.path.expanduser(target)

    # Calling "unrar e" will unpack to PWD, so...
    os.chdir(target)

    for root, dirs, files in os.walk(directory):
        for f in files:
            if extension(f).lower() == ".rar":
                rar = os.path.join(root, f)
                print "Unpacking {} to {}...".format(rar, target),
                code = subprocess.call(["unrar", "e", rar])
                if code != 0:
                    print "Error!"
                else:
                    print "Done."


if __name__ == "__main__":
    description = "Unpacks all RAR archives in the specified directory and "  \
                  "subdirectories."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--dir", help="The directory containing the RAR "
                        "files to unpack. Defaults to present working "
                        "directory.", default="./")
    parser.add_argument("-t", "--target", help="The directory to which to "
                        "move the unpacked files. Defaults to the source "
                        "directory.", default=None)
    args = parser.parse_args()

    unpack(args.dir, args.target if args.target else args.dir)
