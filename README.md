# tgit

This is a simple git GUI for tagging commits.

## Installation

### a) pip

**Note**: GUI style may not look native on Ubuntu,
because this uses PyQt5 distributed by pip.

```bash
pip3 install --user git+https://github.com/Ambrosys/tgit.git#egg=tgit
```

### b) pip, retaining the repository

**Note**: GUI style may not look native on Ubuntu,
because this uses PyQt5 distributed by pip.

* git clone this project into some directory.
* cd into it
* Run:
  ```bash
  pip3 install --user -e .
  ```

### c) native look and feel

This uses PyQt5 distributed by your distribution.

* Run:
  ```bash
  sudo apt install python3-pyqt5
  pip3 install --user ansi2html scikit-image
  ```
* git clone this project into some directory.
* Create executable tgit script (adjust `/path/to/tgit-repository`):
  ```bash
  #!/bin/bash
  PYTHONPATH="$PYTHONPATH:/path/to/tgit-repository" python3 -m tgit.cli.tgit
  ```
* Create executable tgit-show-colors script (adjust `/path/to/tgit-repository`):
  ```bash
  #!/bin/bash
  PYTHONPATH="$PYTHONPATH:/path/to/tgit-repository" python3 -m tgit.cli.show_colors
  ```

## Deinstallation

```bash
pip3 uninstall -y tgit pyqt5 sip

# May be necessary:
rm ~/.local/bin/tgit
rm ~/.local/bin/tgit-show-colors
```

## tgit -h

```
usage: tgit [-h] [-b BRANCH] [-n] [--full-numstat] [-c DIR] [--tags FILENAME]
            [--authors FILENAME] [--commits FILENAME] [--repository FILENAME]
            [--cache FILENAME] [--no-diff]
            [root] [paths [paths ...]]

tgit is a simple git GUI for tagging commits.

positional arguments:
  root                  root directory of the repository, default: .
  paths                 restrict to given paths

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        branch name, default: master
  -n, --no-numstat      do not call git log --numstat (faster)
  --full-numstat        call git log --numstat for excluded files (slower)
  -c DIR, --config-dir DIR
                        directory for config files, default: .
  --tags FILENAME       tags config file, default: tgit-tags.json
  --authors FILENAME    authors config file, default: tgit-authors.json
  --commits FILENAME    commits config file, default: tgit-commits.json
  --repository FILENAME
                        repository config file, default: tgit-repository.json
  --cache FILENAME      cache for commit history, default: tgit-cache.json
  --no-diff             deactivate "automatically diff all files"
```

## Notes

### paths

Paths given are used to restrict git log commands and to limit the "find file"
filter. If commits contain files that match, unmatched files are still listed in
the files list but are greyed out.

You can give exclude regex patterns by prepending the path with a colon, for
example "```:.*\\bfiles\\.cmake```".
These are not used in git log commands but to limit the "find file" filter.

### Filter

The GUI has several commit filters. Most of them are self-explanatory and not
described here.

#### "find files" filter

This filter analyzes commits with one of the specified tags and selects all
commits related to them. Related means that they have files which are getting
modified by the analyzed commits (backward-search in history, see also
```git log --follow```) or that they have files which were modified by the
analyzed commits in the past (forward-search in history).

## Config files

Each config file is optional. But to be able to tag commits `tgit-tags.json`
has to be given.

### tgit-tags.json

This file defines the tags (in user-definable groups) which can be assigned to commits.

Example:
```json
{
  "feature": [
    "feature 1",
    "feature 2",
    "other"
  ],
  "misc": [
    "refactoring",
    "bugfix"
  ],
  "style": [
    "comment",
    "formatting"
  ],
  "status": [
    "merged"
  ]
}
```

### tgit-authors.json

This file defines author groups and author mappings (to simplify the UI).

You can assign a color to a name by adding the color code to the name
(readable for PyQt5.QtGui.QColor).
Authors with no color assoziation will get one from the integrated color palette.

Example:
```json
{
  "core": {
    "Fabian #008000": ["Fabian Sandoval", "FabianSandoval"],
    "John": ["John Doe"]
  },
  "other": {
    "Max": ["Max Mustermann"]
  }
}
```

### tgit-commits.json

This file is maintained by the program.

Example:
```json
{
  "d9e4f8e": [
    "feature 1"
  ],
  "d884a59": [
    "feature 2",
    "merged"
  ]
}
```

### tgit-repository.json

This file can define two things (each are optional):
- The root directory of the repository
  (overrides positional argument `root`).
- Paths relative to the repository root to restrict the commits list
  (additive to `--paths`) or exclude patterns (prepended with a colon).

Example:
```json
{
  "root": "..",
  "paths": [
    "dir",
    "file",
    "sub/path",
    ":exclude-pattern"
  ]
}
```

## Helper utilities

### tgit-show-colors

Lists all colors defined in an authors file (if given)
and the colors of the integrated color palette
and how they will be rendered in the commits view.

```bash
tgit-show-colors -h
```

```
usage: tgit-show-colors [-h] [--authors FILENAME]

Color test utility for tgit.

optional arguments:
  -h, --help          show this help message and exit
  --authors FILENAME  authors config file, default: tgit-authors.json
```
