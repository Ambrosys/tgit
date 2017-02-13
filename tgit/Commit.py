import datetime

from . import Globals
from . import Utils


class CommitFile:
    def __init__( self, name ):
        self.name = name
        # status from --name-status may be A|C|D|M|R|T|U; all status identifiers:
        # - Added (A)
        # - Copied (C)
        # - Deleted (D)
        # - Modified (M)
        # - Renamed (R)
        # - have their type (i.e. regular file, symlink, submodule, …​) changed (T)
        # - are Unmerged (U)
        # - are Unknown (X)
        # - have had their pairing Broken (B)
        self.status = '?'
        self.added = 0
        self.removed = 0

    def setStatus( self, status ):
        self.status = status

    def addNumstat( self, added, removed ):
        if added == '-' and removed == '-': # numstat calculation failed, may happen...
            return
        try:
            self.added += int( added )
            self.removed += int( removed )
        except ValueError:
            print( 'Warning: numstat for %s is "%s %s"' % (self.name, added, removed) )

class Commit:
    def __init__( self, index, commitHash, parents, author, email, date, message ):
        self.index = index
        self.commitHash = commitHash
        self.parents = parents
        self.author = author
        self.originalAuthor = author
        self.email = email
        # git date example: 2010-06-17T13:08:54+00:00
        self.date = datetime.datetime.strptime( date[:22] + date[-2:], '%Y-%m-%dT%H:%M:%S%z' )
        self.message = message
        self.files = []
        self.filesHash = {}
        self.added = 0
        self.removed = 0
        self.tags = []
        self.hash_filename_history = {}
        self._children = None
        self._branch = None
        self._recognizedMerges = None # a and b into c would be [a, b, c]
        self._maxDate = None
        self._branchUncertainty = 0

    def _ensureFile( self, filename ):
        if filename in self.filesHash:
            return self.filesHash[filename]
        else:
            file = CommitFile( filename )
            self.files.append( file )
            self.filesHash[filename] = file
            return file

    def _recalculateOverallNumstat( self ):
        self.added = 0
        self.removed = 0
        for file in self.files:
            self.added += file.added
            self.removed += file.removed

    def setStatus( self, status, filename ):
        self._ensureFile( filename ).setStatus( status )

    def addNumstat( self, added, removed, filename ):
        self._ensureFile( filename ).addNumstat( added, removed )
        self._recalculateOverallNumstat()

    def getFilenames( self ):
        return list( map( lambda file: file.name, self.files ) )

    def getChildrenUnsorted( self ):
        if self._children is None:
            self._children = []
            for c in Globals.allCommits:
                if self.commitHash in c.parents:
                    self._children.append( c )
        return self._children

    def getChildren( self ):
        return sorted( self.getChildrenUnsorted(), key=lambda c: c.index, reverse=True )

    def getParentsUnsorted( self, commitsHash ):
        parents = map( lambda h: commitsHash[h], self.parents )
        return list( parents )

    def getParents( self, commitsHash ):
        return sorted( self.getParentsUnsorted( commitsHash ), key=lambda c: c.index, reverse=True )

    def getOneliner( self ):
        return '%i: %s: %s' % (self.index, self.commitHash, self.getMessageOneliner())

    def getShortOnelinerHtml( self, withLink, filename = '' ):
        if withLink:
            link = self.commitHash
            if filename:
                link += '-' + filename
            return '<a href="%s">%i: <code>%s</code></a>' % (link, self.index, self.commitHash)
        else:
            assert not filename
            return '%i: <code>%s</code>' % (self.index, self.commitHash)

    def getOnelinerHtml( self, withLink, filename = '' ):
        return '%s: %s' % (self.getShortOnelinerHtml( withLink, filename ), self.getMessageOneliner())

    def getMultilinerHtml( self ):
        if '\n' in self.message:
            (m1, m2) = self.message.split( '\n', 1 )
        else:
            m1 = self.message
            m2 = ''
        m1 = m1.strip().replace( '\n', '<br />' )
        m2 = m2.strip().replace( '\n', '<br />' )
        if m2:
            m2 = '<br />%s' % m2
        return '%i: <strong><code>%s</code>: </strong><span style="color:#e66c1e;"><strong>%s</strong>%s</span>' % (self.index, self.commitHash, m1, m2)

    def getOnelinerWithDateHtml( self, withLink, filename = '' ):
        return '%s: %s' % (self.getDateString(), self.getOnelinerHtml( withLink, filename ))

    def getMessageOneliner( self ):
        return self.message.strip().replace( '\n', ' ' )

    def getTagsSorted( self ):
        tags = []
        for tag in Globals.allTags:
            if tag in self.tags:
                tags.append( tag )
        tags.extend( sorted( list( set( self.tags ) - set( Globals.allTags ) ) ) )
        return tags

    def getBranch( self ):
        if self._branch:
            return self._branch
        return ''

    def getBranchOneliner( self ):
        if self._branch:
            if self._branchUncertainty == 0:
                return self._branch
            elif self._branchUncertainty <= 3:
                return '%s%s' % (self._branch, '?' * self._branchUncertainty)
            else:
                return '%s%s' % (self._branch, '?+%i' % (self._branchUncertainty - 1))
        return ''

    def getTagsOneliner( self ):
        return ', '.join( self.getTagsSorted() )

    def getDateString( self ):
        return self.date.strftime( '%Y-%m-%d %H:%M:%S' )

    def getHistory( self, filename ):
        if not filename in self.hash_filename_history:
            history = Utils.call( ['git', 'log', '--format=%h', '--follow', self.commitHash, '--', filename], cwd=Globals.repositoryDir )
            self.hash_filename_history[filename] = history[1:] # dismiss self
        return self.hash_filename_history[filename]
