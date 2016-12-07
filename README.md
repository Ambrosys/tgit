# tgit

This is a simple git GUI for tagging commits.

## Installation

You need python3 with pyqt5:

```sh
sudo apt install python3-pyqt5
```

For the git-diff rendering the
[ansi2html library](https://github.com/ralphbean/ansi2html) is expected to
reside under the root directory of this project:

```sh
cd tgit
git clone https://github.com/ralphbean/ansi2html.git
```

## Config files

The format of the config files is as given in the following examples.

### tgit-tags.json

This file defines the tags which can be assigned to commits.

```json
[
  "other",
  "refactoring",
  "bugfix",
  "feature 1",
  "feature 2",
  "merged"
]
```

### tgit-authors.json

This file defines author mappings (to simplify the UI).

```json
{
  "Fabian Sandoval": "fs",
  "FabianSandoval": "fs",
  "Max Mustermann": "mm"
}
```

### tgit-commits.json

This file is maintained by the program.

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

### tgit-paths.json

This file defines paths relative to the repository root
to restrict the commits list (additive to `--paths`).

```json
[
  "dir",
  "file",
  "sub/path"
]
```
