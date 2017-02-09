
import Colors

from PyQt5 import QtGui
import os
import json
import collections

allAuthorsGrouped = collections.OrderedDict()
allAuthorsHash = {}
allAuthorsHash_author_group = {}
map_author_color = {} # does not need to be complete until call of updateColors()
map_author_originalColor = {} # does not need to be complete

def load( filepath ):
    global allAuthorsGrouped
    global allAuthorsHash
    global allAuthorsHash_author_group
    global map_author_color
    global map_author_originalColor

    if os.path.isfile( filepath ):
        allAuthorsHashGrouped = json.load( open( filepath, 'r' ), object_pairs_hook=collections.OrderedDict )
    else:
        allAuthorsHashGrouped = {}
    for group, authorsHash in allAuthorsHashGrouped.items():
        allAuthorsGrouped[group] = set()
        for authorWithAttributes, originalAuthors in authorsHash.items():
            attributes = authorWithAttributes.split()
            author = attributes[0]
            color = None
            for i in range( 1, len(attributes) ):
                if i == 1: # attributes[i][:1] == '#':
                    color = QtGui.QColor( attributes[i] )
            if color is not None:
                map_author_originalColor[author] = color
                map_author_color[author] = Colors.optimizeForBackground( color )
            allAuthorsGrouped[group].add( author )
            allAuthorsHash_author_group[author] = group
            for originalAuthor in originalAuthors:
                allAuthorsHash[originalAuthor] = author

def updateColors():
    """
    set colors for authors without color definition
    """

    i = 0
    for group, authors in allAuthorsGrouped.items():
        for author in authors:
            if not author in map_author_color:
                map_author_color[author] = Colors.optimizeForBackground( QtGui.QColor( Colors.colors[i % len( Colors.colors ) ] ) )
                i += 1