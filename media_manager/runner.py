"""Contains the console script entrypoints.
"""
from __future__ import print_function
from __future__ import unicode_literals
from pprint import pprint
import os
import sys

import readline

from media_manager.sourcerepo import SourceRepo
from media_manager import metadata
from media_manager import utils

DEFAULT_REPO = os.path.abspath(os.path.expanduser('~/media'))
# ^^^ Be careful not to use this in tests, you can overwrite the actual
# metadata and files that way.


def _complete(text, state, tags):
    for tag in tags:
        if tag.startswith(text):
            # print("\n" + tag)
            if not state:
                return tag
            else:
                state -= 1


def complete_albums(text, state):
    return _complete(text, state, utils.ALBUMS)


def add_video():
    if len(sys.argv) < 2:
        print("Pass me a path to a video file.")
        sys.exit(1)
    filename = sys.argv[1]
    assert os.path.exists(filename)
    md = metadata.Metadata(DEFAULT_REPO)
    md.read()
    source_repo = SourceRepo(DEFAULT_REPO)

    # http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    year = None
    while not year:
        year = raw_input('Year: ')
    title = None
    while not title:
        title = raw_input('Title: ')
    readline.set_completer(complete_albums)
    album = None
    while not album:
        album = raw_input('Album: ')

    video = metadata.Video(
        original_filepath=filename.decode('utf8'),
        title=title.decode('utf8'),
        year=year.decode('utf8'),
        albums=[album.decode('utf8')],
        )
    pprint(video.as_dict())

    source_repo.add_file(video)
    md.add(video)
    md.write()

    current_dir = os.getcwd()
    # Print command suggestions.
    print("Suggested commands:\n")
    print("cd {}".format(DEFAULT_REPO))
    for cmd in source_repo.git_commands:
        print(cmd)
    print("git add -u")
    print("git commit -m 'update'")
    print("git push")
    print("git annex copy --to origin")
    print("git annex sync")
    print("cd {}".format(current_dir))
