
import Globals
import Utils
import datetime

class CommitFile:
    def __init__( self, name ):
        self.name = name
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
        return map( lambda file: file.name, self.files )

    def getChildren( self ):
        children = []
        for c in Globals.allCommits:
            if self.commitHash in c.parents:
                children.append( c )
        return sorted( children, key=lambda c: c.index, reverse=True )

    def getParents( self, commitsHash ):
        parents = map( lambda h: commitsHash[h], self.parents )
        return sorted( parents, key=lambda c: c.index, reverse=True )

    def getOneliner( self ):
        return '%i: %s: %s' % (self.index, self.commitHash, self.getMessageOneliner())

    def getShortOnelinerHtml( self, withLink ):
        if withLink:
            return '<a href="%s">%i: <code>%s</code></a>' % (self.commitHash, self.index, self.commitHash)
        else:
            return '%i: <code>%s</code>' % (self.index, self.commitHash)

    def getOnelinerHtml( self, withLink ):
        return '%s: %s' % (self.getShortOnelinerHtml( withLink ), self.getMessageOneliner())

    def getMultilinerHtml( self ):
        (m1, m2) = self.message.split( '\n', 1 )
        m1 = m1.strip().replace( '\n', '<br />' )
        m2 = m2.strip().replace( '\n', '<br />' )
        if m2:
            m2 = '<br />%s' % m2
        return '%i: <strong><code>%s</code>: </strong><span style="color:#e66c1e;"><strong>%s</strong>%s</span>' % (self.index, self.commitHash, m1, m2)

    def getOnelinerWithDateHtml( self, withLink ):
        return '%s: %s' % (self.getDateString(), self.getOnelinerHtml( withLink ))

    def getMessageOneliner( self ):
        return self.message.strip().replace( '\n', ' ' )

    def getTagsSorted( self ):
        tags = []
        for tag in Globals.allTags:
            if tag in self.tags:
                tags.append( tag )
        tags.extend( sorted( list( set( self.tags ) - set( Globals.allTags ) ) ) )
        return tags

    def getTagsOneliner( self ):
        return ', '.join( self.getTagsSorted() )

    def getDateString( self ):
        return self.date.strftime( '%Y-%m-%d %H:%M:%S' )

    def getHistory( self, filename ):
        if not filename in self.hash_filename_history:
            history = Utils.call( ['git', 'log', '--format=%h', '--follow', self.commitHash, '--', filename], cwd=Globals.repositoryDir )
            self.hash_filename_history[filename] = history[1:] # dismiss self
        return self.hash_filename_history[filename]
