# tgit

This is a simple git GUI for tagging commits.

## Installation

You need python3 with pyqt5:

```bash
sudo apt install python3-pyqt5
```

For the git-diff rendering the
[ansi2html library](https://github.com/ralphbean/ansi2html) is expected to
reside under the root directory of this project:

```bash
cd tgit
git clone https://github.com/ralphbean/ansi2html.git
```

## tgit -h

```
usage: tgit [-h] [-b BRANCH] [-n] [--full-numstat] [-c DIR] [--tags FILENAME]
            [--authors FILENAME] [--commits FILENAME] [--repository FILENAME]
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
```

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

Example:
```json
{
  "core": {
    "fs": ["Fabian Sandoval", "FabianSandoval"],
    "jd": ["John Doe"]
  },
  "other": {
    "mm": ["Max Mustermann"]
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
  (additive to `--paths`).

Example:
```json
{
  "root": "..",
  "paths": [
    "dir",
    "file",
    "sub/path"
  ]
}
```
