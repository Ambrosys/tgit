from PyQt5 import QtWidgets, QtGui, QtCore
import json
import collections
import re
import argparse
import os
import datetime

from .. import Globals
from .. import Utils
from .. import Filter
from .. import CommitList
from .. import FileList
from .. import CreateUi
from .. import GeneralUi
from .. import Commit
from .. import Colors
from .. import Authors


@QtCore.pyqtSlot()
def on_tagCheckBox_clicked():
    if Globals.selectedCommit is None:
        return
    tags = []
    for tagCheckBox in Globals.ui_tagCheckBoxes:
        if tagCheckBox.isChecked():
            tags.append( tagCheckBox.text() )
    Globals.selectedCommit.tags = tags

    CommitList.updateTagsOfTreeWidgetItem( Globals.selectedCommit )
    Filter.doFiltering()

class MainWindow( QtWidgets.QMainWindow ):
    def __init__( self, onClose ):
        super().__init__()
        self.onClose = onClose
    def closeEvent( self, event ):
        if self.onClose():
            event.accept()
        else:
            event.ignore()

def getYoungestFollowingFirstParent( commit_, parent_ ):
    if commit_._maxDate is not None:
        return commit_._maxDate
    maxDate = datetime.datetime.min.replace( tzinfo=datetime.timezone.utc )
    commit = parent_
    parent = None
    children = [commit_]
    while len( children ) == 1:
        parent = commit
        commit = children[0]
        parents = list( commit.getParentsUnsorted( Globals.allCommitsHash ) )
        if len( parents ) >= 1 and parents[0] == parent:
            maxDate = commit.date
            children = commit.getChildrenUnsorted()
        else:
            children = []
            break
    if len( children ) > 1:
        maxDate = max( map( lambda child: getYoungestFollowingFirstParent( child, commit ), children ) )
    commit_._maxDate = maxDate
    return maxDate

def main():
    parser = argparse.ArgumentParser( description='tgit is a simple git GUI for tagging commits.' )
    parser.add_argument( 'root', nargs='?', type=str, default='.', help = 'root directory of the repository, default: %(default)s' )
    parser.add_argument( 'paths', nargs='*', type=str, default=[], help = 'restrict to given paths' )
    parser.add_argument( '-b', '--branch', type=str, default='master', help = 'branch name, default: %(default)s' )
    parser.add_argument( '-n', '--no-numstat', action='store_true', help = 'do not call git log --numstat (faster)' )
    parser.add_argument( '--full-numstat', action='store_true', help = 'call git log --numstat for excluded files (slower)' )
    parser.add_argument( '-c', '--config-dir', metavar='DIR', type=str, default='.', help = 'directory for config files, default: %(default)s' )
    parser.add_argument( '--tags', metavar='FILENAME', type=str, default='tgit-tags.json', help = 'tags config file, default: %(default)s' )
    parser.add_argument( '--authors', metavar='FILENAME', type=str, default='tgit-authors.json', help = 'authors config file, default: %(default)s' )
    parser.add_argument( '--commits', metavar='FILENAME', type=str, default='tgit-commits.json', help = 'commits config file, default: %(default)s' )
    parser.add_argument( '--repository', metavar='FILENAME', type=str, default='tgit-repository.json', help = 'repository config file, default: %(default)s' )
    parser.add_argument( '--cache', metavar='FILENAME', type=str, default='tgit-cache.json', help = 'cache for commit history, default: %(default)s' )
    parser.add_argument( '--no-diff', action='store_true', help = 'deactivate "automatically diff all files"' )
    parser.add_argument( '--no-cache', action='store_true', help = 'do not save cache file' )
    parser.add_argument( '-r', '--read-only', action='store_true', help = 'read-only mode' )
    parser.add_argument( '-d', '--diff-hash', action='store_true', help = 'calculate diff hashes in views' )
    parser.add_argument( '-s', '--space-tolerant', action='store_true', help = 'ignore blank lines and white space at EOL in diff hashes' )
    args = parser.parse_args()

    if args.no_numstat and args.full_numstat:
        print( 'Error: --no-numstat and --full-numstat are mutually exclusive.' )
        exit( 1 )

    if args.space_tolerant and not args.diff_hash:
        print( 'Error: --space-tolerant requires --diff-hash.' )
        exit( 1 )

    if not os.path.isdir( args.root ):
        print( 'Error: %s is not a directory.' % args.root )
        exit( 1 )

    if not os.path.isdir( args.config_dir ):
        print( 'Error: %s is not a directory.' % args.config_dir )
        exit( 1 )

    Globals.readOnlyMode = args.read_only
    Globals.calculateDiffHashes = args.diff_hash
    Globals.calculateDiffHashesSpaceTolerant = args.space_tolerant

    configDir = args.config_dir
    filepath_tagsJson = os.path.join( configDir, args.tags )
    filepath_commitsJson = os.path.join( configDir, args.commits )
    filepath_authorsJson = os.path.join( configDir, args.authors )
    filepath_repositoryJson = os.path.join( configDir, args.repository )
    filepath_cacheJson = os.path.join( configDir, args.cache )

    if os.path.isfile( filepath_repositoryJson ):
        repository = json.load( open( filepath_repositoryJson, 'r' ) )
    else:
        repository = {}

    if 'root' in repository:
        Globals.repositoryDir = os.path.join( configDir, repository['root'] )
    else:
        Globals.repositoryDir = args.root
    Globals.branch = args.branch

    if 'paths' in repository:
        allPaths = list( map( lambda path: path if path[0] == ':' else os.path.join( Globals.repositoryDir, path ), repository['paths'] ) )
    else:
        allPaths = []
    allPaths.extend( args.paths )
    for path in allPaths:
        if path[0] == ':': # exclude pattern
            Globals.excludePatterns.append( re.compile( path[1:] ) )
        elif os.path.isdir( path ):
            Globals.includeDirectories.append( os.path.relpath( path, Globals.repositoryDir ) )
        elif os.path.isfile( path ):
            Globals.includeFiles.append( os.path.relpath( path, Globals.repositoryDir ) )
        else:
            print( 'Error: %s is not a valid path.' % path )
            exit( 1 )

    if os.path.isfile( filepath_tagsJson ):
        Globals.allTagsGrouped = json.load( open( filepath_tagsJson, 'r' ), object_pairs_hook=collections.OrderedDict )
    else:
        Globals.allTagsGrouped = {}
    for group, tags in Globals.allTagsGrouped.items():
        Globals.allTags.extend( tags )

    Authors.load( filepath_authorsJson )

    if os.path.isfile( filepath_commitsJson ):
        allTagsPerCommitHash = json.load( open( filepath_commitsJson, 'r' ), object_pairs_hook=collections.OrderedDict )
    else:
        allTagsPerCommitHash = collections.OrderedDict()

    ui_app = QtWidgets.QApplication( [] )
    ui_app.setWindowIcon( QtGui.QIcon( os.path.join( os.path.dirname( __file__ ), '../../img/tgit-logo.svg' ) ) )

    Globals.initUiGlobals()

    QtWidgets.QApplication.setFont( Globals.normalFont )

    # reading commits (1/3)...

    Globals.allCommits = []
    Globals.allCommitsHash = {}
    commitCounter = 1
    missingAuthors = set()
    newGroups = {}
    tagsUsedForCommits = set()
    # see https://git-scm.com/docs/pretty-formats
    cmd = ['git', 'log', '-z', '--reverse', '--topo-order', '--format=%h%x09%p%x09%an%x09%ae%x09%aI%x09%B', Globals.branch]
    for log in Utils.call_nullSeperated( cmd, cwd=Globals.repositoryDir ):
        if log:
            (commitHash, parents, originalAuthor, email, date, message) = log.split( '\t', 5 )

            if originalAuthor in Authors.allAuthorsHash:
                author = Authors.allAuthorsHash[originalAuthor]
            else:
                author = originalAuthor
                missingAuthors.add( originalAuthor )
            if author in Authors.allAuthorsHash_author_group:
                group = Authors.allAuthorsHash_author_group[author]
            else:
                group = author[0].upper()
            if group in Authors.allAuthorsGrouped:
                Authors.allAuthorsGrouped[group].add( author )
            else:
                if not group in newGroups:
                    newGroups[group] = set()
                newGroups[group].add( author )

            parents = parents.split( ' ' )
            if not parents[0]:
                parents = []
            commit = Commit.Commit( commitCounter, commitHash, parents, author, email, date, message )
            if commit.commitHash in allTagsPerCommitHash:
                commit.tags = allTagsPerCommitHash[commit.commitHash]
                tagsUsedForCommits.update( commit.tags )
            commit.originalAuthor = originalAuthor
            Globals.allCommits.append( commit )
            Globals.allCommitsHash[commitHash] = commit
            commitCounter += 1
    if os.path.isfile( filepath_authorsJson ):
        for author in sorted( list( missingAuthors ) ):
            print( 'Warning: author "%s" missing in %s' % (author, filepath_authorsJson) )
    for newGroup in sorted( newGroups.keys() ):
        Authors.allAuthorsGrouped[newGroup] = newGroups[newGroup]
    for group in Authors.allAuthorsGrouped:
        Authors.allAuthorsGrouped[group] = sorted( list( Authors.allAuthorsGrouped[group] ) )

    # reading commits (2/3)...

    commit = None
    cmd = ['git', 'log', '--reverse', '--topo-order', '--format=%h', '--name-status', Globals.branch]
    for log in Utils.call( cmd, cwd=Globals.repositoryDir ):
        if log:
            if not '\t' in log:
                commit = Globals.allCommitsHash[log]
            else:
                (status, file) = log.split( '\t', 1 )
                commit.setStatus( status, file )

    # reading commits (3/3)...

    if not args.no_numstat:
        commit = None
        cmd = ['git', 'log', '--reverse', '--topo-order', '--format=%h', '--numstat', Globals.branch, '--']
        if Globals.includeDirectories or Globals.includeFiles:
            cmd.extend( Globals.includeDirectories )
            cmd.extend( Globals.includeFiles )
        else:
            cmd.append( '.' )
        for log in Utils.call( cmd, cwd=Globals.repositoryDir ):
            if log:
                if not '\t' in log:
                    commit = Globals.allCommitsHash[log]
                else:
                    (added, removed, file) = log.split( '\t', 2 )
                    commit.addNumstat( added, removed, file )

    # reconstructing branch names

    def setBranchName( destination, name ):
        destination._branchUncertainty = 0
        destination._branch = name

    def inheritBranchName( destination, origin, uncertainty = 0 ):
        destination._branchUncertainty = origin._branchUncertainty + uncertainty
        destination._branch = origin._branch

    mergeCommitRegex_firstIntoSecond1 = re.compile( "^merge\\b(?:.*)?\\bbranch '([^']+)'.*\\binto ([^ ().]+).*$", re.IGNORECASE )
    mergeCommitRegex_firstIntoSecond2 = re.compile( "^merge from ([^ ()]+)\\b.*into ([^ ().]+).*$", re.IGNORECASE )
    mergeCommitRegex_firstIntoCurrent1 = re.compile( "^merge\\b(?:.*)?\\bbranch '([^']+)'.*$", re.IGNORECASE )
    mergeCommitRegex_firstIntoCurrent2 = re.compile( "^merge from ([^ ().]+).*$", re.IGNORECASE )
    firstCommit = True
    for c in reversed( Globals.allCommits ):
        if firstCommit:
            firstCommit = False
            assert not c.getChildren()
            assert not c._branch
            setBranchName( c, Globals.branch )
        else:
            if not c._branch:
                children = list( c.getChildrenUnsorted() )
                if len( children ) == 1:
                    inheritBranchName( c, children[0] )
                elif len( children ) >= 2:
                    # use child with longest path for first parent
                    dates = list( map( lambda child: getYoungestFollowingFirstParent( child, c ), children ) )
                    youngestDate = max( dates )
                    youngestItems = [children[i] for i in range(len(dates)) if dates[i] == youngestDate]
                    if len(youngestItems) == 1:
                        if youngestItems[0]._branch:
                            inheritBranchName( c, youngestItems[0], 1 )

        parents = list( c.getParentsUnsorted( Globals.allCommitsHash ) )
        if len( parents ) == 2:
            messageFirstLine = c.message.split( '\n', 1 )[0]
            m = None
            if not m:
                for firstIntoSecond in [mergeCommitRegex_firstIntoSecond1, mergeCommitRegex_firstIntoSecond2]:
                    m = firstIntoSecond.match( messageFirstLine )
                    if m:
                        c._recognizedMerges = [m.group(1), m.group(2)]
                        setBranchName( parents[0], m.group(2) )
                        setBranchName( parents[1], m.group(1) )
                        break
            if not m:
                for firstIntoCurrent in [mergeCommitRegex_firstIntoCurrent1, mergeCommitRegex_firstIntoCurrent2]:
                    m = firstIntoCurrent.match( messageFirstLine )
                    if m:
                        c._recognizedMerges = [m.group(1), '']
                        inheritBranchName( parents[0], c )
                        setBranchName( parents[1], m.group(1) )
                        break

    # define colors for authors

    Authors.updateColors()

    # load cache

    if os.path.isfile( filepath_cacheJson ):
        cache = json.load( open( filepath_cacheJson, 'r' ) )
        for hash in cache['history']:
            if hash in Globals.allCommitsHash:
                Globals.allCommitsHash[hash].hash_filename_history = cache['history'][hash]

    # building window...

    transparentPixmap = QtGui.QPixmap( 64, 64 )
    transparentPixmap.fill( QtGui.QColor( 0, 0, 0, 0 ) )
    Globals.transparentIcon = QtGui.QIcon( transparentPixmap )

    undefinedTags = sorted( tagsUsedForCommits - set( Globals.allTags ) )

    Globals.ui_commitList = QtWidgets.QTreeWidget()
    Globals.ui_commitList.setRootIsDecorated( False )
    Globals.ui_commitList.setHeaderItem( QtWidgets.QTreeWidgetItem( [
        '#',
        'commit',
        'diff',
        'lines',
        'tags',
        'date',
        'author',
        'branch',
        'message'
        ] ) )
    Globals.ui_commitList.setColumnCount( CommitList.commitListItemColumnCount )
    Globals.ui_commitList.setColumnHidden( CommitList.commitListItemColumn_diff, not Globals.calculateDiffHashes )
    Globals.ui_commitList.header().setSectionResizeMode( QtWidgets.QHeaderView.ResizeToContents )
    Globals.ui_commitList.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
    Globals.ui_commitList.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
    Globals.ui_commitList.currentItemChanged.connect( CommitList.on_commitList_currentItemChanged )
    Globals.ui_commitList.customContextMenuRequested.connect( CommitList.on_commitList_customContextMenuRequested )
    Globals.ui_commitList.itemSelectionChanged.connect( CommitList.slot_updateCommitListInfo )

    for commit in reversed( Globals.allCommits ):
        readableLines = str( commit.added + commit.removed )
        readableBranch = commit.getBranchOneliner()
        readableTags = commit.getTagsOneliner()
        readableMessage = commit.getMessageOneliner()
        item = QtWidgets.QTreeWidgetItem( [
            str(commit.index),
            commit.commitHash,
            '',
            readableLines,
            readableTags,
            commit.getDateString(),
            commit.author,
            readableBranch,
            readableMessage
            ] )
        Globals.ui_commitListItemHash[commit.commitHash] = item
        for i in range( CommitList.commitListItemColumnCount ):
            item.setFont( i, Globals.smallFont )
        item.setFont( CommitList.commitListItemColumn_commit, Globals.courierFont )
        item.setFont( CommitList.commitListItemColumn_diff, Globals.courierFont )
        item.setFont( CommitList.commitListItemColumn_author, Globals.boldFont )
        item.setTextAlignment( CommitList.commitListItemColumn_index, QtCore.Qt.AlignRight )
        item.setTextAlignment( CommitList.commitListItemColumn_lines, QtCore.Qt.AlignRight )
        if not Filter.somePassesPathFilter( commit.getFilenames(), False ):
            for i in range( item.columnCount() ):
                item.setForeground( i, QtGui.QBrush( QtCore.Qt.lightGray ) )
        for col in range( item.columnCount() ):
            item.setBackground( col, QtGui.QBrush( Authors.map_author_color[commit.author] ) )
        item.setIcon( 0, Globals.transparentIcon )
        Globals.ui_commitList.addTopLevelItem( item )

    Globals.ui_diffViewer = QtWidgets.QTextEdit()
    Globals.ui_diffViewer.setReadOnly( True )
    Globals.ui_diffViewer.setWordWrapMode( QtGui.QTextOption.NoWrap )

    (Globals.ui_followViewerScrollArea, Globals.ui_followViewer) = CreateUi.createHistoryWidgets()
    Globals.ui_followViewerScrollArea.setHidden( True )

    ui_fileViewers = QtWidgets.QSplitter()
    ui_fileViewers.setOrientation( QtCore.Qt.Horizontal )
    ui_fileViewers.addWidget( Globals.ui_diffViewer )
    ui_fileViewers.addWidget( Globals.ui_followViewerScrollArea )
    ui_fileViewers.setSizes( [3000, 1000] )

    Globals.ui_diffViewerCheckBox = QtWidgets.QCheckBox( 'automatically diff all files' )
    Globals.ui_diffViewerCheckBox.setChecked( not args.no_diff )

    ui_diffViewAreaLayout = QtWidgets.QVBoxLayout()
    ui_diffViewAreaLayout.setContentsMargins( 0, 0, 0, 0 )
    ui_diffViewAreaLayout.addWidget( Globals.ui_diffViewerCheckBox )
    ui_diffViewAreaLayout.addWidget( ui_fileViewers )
    ui_diffViewAreaWidget = QtWidgets.QWidget()
    ui_diffViewAreaWidget.setLayout( ui_diffViewAreaLayout )

    Globals.ui_filterAreaCheckBox = QtWidgets.QCheckBox( 'enable filter' )
    Globals.ui_filterAreaCheckBox.setChecked( True )
    Globals.ui_filterAreaOnlySearchCheckBox = QtWidgets.QCheckBox( 'only search' )
    # signals are assigned later

    ui_vline = QtWidgets.QFrame()
    ui_vline.setFrameShape( QtWidgets.QFrame.VLine )
    ui_vline.setFrameShadow( QtWidgets.QFrame.Sunken )

    ui_filterIncludeSpecialAreaLineLayout = QtWidgets.QHBoxLayout()
    ui_filterIncludeSpecialAreaLineLayout.setContentsMargins( 0, 0, 0, 0 )
    ui_filterIncludeSpecialAreaLineLayout.addWidget( Globals.ui_filterAreaCheckBox )
    ui_filterIncludeSpecialAreaLineLayout.addWidget( Globals.ui_filterAreaOnlySearchCheckBox )
    ui_filterIncludeSpecialAreaLineLayout.addWidget( ui_vline )
    for tag in ['consider all paths']:
        filterCheckBox = QtWidgets.QCheckBox( tag )
        Globals.ui_filterIncludeSpecialCheckBoxes.append( filterCheckBox )
        filterCheckBox.clicked.connect( Filter.doFiltering )
        ui_filterIncludeSpecialAreaLineLayout.addWidget( filterCheckBox )
    ui_filterIncludeSpecialAreaLineLayout.addStretch()
    ui_filterIncludeSpecialAreaLineWidget = QtWidgets.QWidget()
    ui_filterIncludeSpecialAreaLineWidget.setLayout( ui_filterIncludeSpecialAreaLineLayout )

    ui_filterTabWidget = CreateUi.createFilterTabWidget( Globals.allTagsGrouped, undefinedTags, Authors.allAuthorsGrouped )

    Globals.ui_searchFilterLineEdit = QtWidgets.QLineEdit()
    Globals.ui_searchFilterLineEdit.setClearButtonEnabled( True )
    #Globals.ui_searchFilterLineEdit.editingFinished.connect( Filter.doFiltering )
    Globals.ui_searchFilterLineEdit.textEdited.connect( Filter.doFiltering )

    ui_filterSearchAreaLayout = QtWidgets.QHBoxLayout()
    ui_filterSearchAreaLayout.setContentsMargins( 0, 0, 0, 0 )
    ui_filterSearchAreaLayout.addWidget( Globals.ui_searchFilterLineEdit )
    for searchLocation in ['commit', 'branch', 'message', 'files in paths', 'files not in paths']:
        filterCheckBox = QtWidgets.QCheckBox( searchLocation )
        Globals.ui_searchFilterCheckBoxes.append( filterCheckBox )
        filterCheckBox.setChecked( True )
        filterCheckBox.clicked.connect( Filter.doFiltering )
        ui_filterSearchAreaLayout.addWidget( filterCheckBox )
    ui_filterSearchAreaWidget = QtWidgets.QWidget()
    ui_filterSearchAreaWidget.setLayout( ui_filterSearchAreaLayout )

    ui_filterAreaLayout = QtWidgets.QVBoxLayout()
    ui_filterAreaLayout.addWidget( ui_filterIncludeSpecialAreaLineWidget )
    ui_filterAreaLayout.addWidget( ui_filterTabWidget )
    ui_filterAreaLayout.addWidget( ui_filterSearchAreaWidget )
    ui_filterAreaLayout.setContentsMargins( 0, 0, 0, 0 )
    ui_filterAreaWidget = QtWidgets.QWidget()
    ui_filterAreaWidget.setLayout( ui_filterAreaLayout )

    def filterCheckBoxesToggled():
        filterEnabled = Globals.ui_filterAreaCheckBox.isChecked()
        onlySearch = Globals.ui_filterAreaOnlySearchCheckBox.isChecked()
        Globals.ui_filterAreaOnlySearchCheckBox.setEnabled( filterEnabled )
        for ui_filterIncludeSpecialCheckBox in Globals.ui_filterIncludeSpecialCheckBoxes:
            ui_filterIncludeSpecialCheckBox.setEnabled( filterEnabled and not onlySearch )
        ui_filterTabWidget.setVisible( filterEnabled and not onlySearch )
        Globals.ui_searchFilterLineEdit.setEnabled( filterEnabled )
        for ui_searchFilterCheckBox in Globals.ui_searchFilterCheckBoxes:
            ui_searchFilterCheckBox.setEnabled( filterEnabled )

    Globals.ui_filterAreaCheckBox.toggled.connect( filterCheckBoxesToggled )
    Globals.ui_filterAreaOnlySearchCheckBox.toggled.connect( filterCheckBoxesToggled )
    Globals.ui_filterAreaCheckBox.clicked.connect( Filter.doFiltering )
    Globals.ui_filterAreaOnlySearchCheckBox.clicked.connect( Filter.doFiltering )

    groupTags = collections.OrderedDict()
    for group in Globals.allTagsGrouped:
        groupTags[group] = (True, Globals.allTagsGrouped[group])
    if undefinedTags:
        groupTags['undefined'] = (False, undefinedTags)

    if not Globals.readOnlyMode and groupTags:
        ui_tagWidget = CreateUi.createTagCheckBoxes( groupTags, Globals.ui_tagCheckBoxes, False, on_tagCheckBox_clicked, allowButtons=False )

        ui_tagScrollArea = QtWidgets.QScrollArea()
        ui_tagScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_tagScrollArea.setWidget( ui_tagWidget )

        ui_tagAreaWidget = QtWidgets.QTabWidget()
        ui_tagAreaWidget.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum )
        ui_tagAreaWidget.addTab( ui_tagScrollArea, 'tags' )
    else:
        ui_tagAreaWidget = None

    Globals.ui_commitInfo1 = QtWidgets.QLabel()
    Globals.ui_commitInfo1.setText( 'commit' )
    Globals.ui_commitInfo1.setTextInteractionFlags( QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse )
    Globals.ui_commitInfo1.setWordWrap( True )
    Globals.ui_commitInfo1.linkActivated.connect( GeneralUi.on_commitLinkActivated )

    Globals.ui_commitInfo2 = QtWidgets.QLabel()
    Globals.ui_commitInfo2.setText( 'meta data' )
    Globals.ui_commitInfo2.setTextInteractionFlags( QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse )
    Globals.ui_commitInfo2.setWordWrap( True )
    Globals.ui_commitInfo2.linkActivated.connect( GeneralUi.on_commitLinkActivated )

    Globals.ui_filesList = QtWidgets.QTreeWidget()
    Globals.ui_filesList.setRootIsDecorated( False )
    Globals.ui_filesList.setHeaderItem( QtWidgets.QTreeWidgetItem( ['diff', 'lines', 'file'] ) )
    Globals.ui_filesList.setColumnCount( FileList.filesListItemColumnCount )
    Globals.ui_filesList.setColumnHidden( FileList.filesListItemColumn_diff, not Globals.calculateDiffHashes )
    Globals.ui_filesList.header().setSectionResizeMode( QtWidgets.QHeaderView.ResizeToContents )
    Globals.ui_filesList.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
    Globals.ui_filesList.itemSelectionChanged.connect( FileList.on_filesList_itemSelectionChanged )
    Globals.ui_filesList.itemActivated.connect( FileList.on_filesList_itemActivated )
    Globals.ui_filesList.currentItemChanged.connect( FileList.on_filesList_currentItemChanged )

    ui_diffSplitter = QtWidgets.QSplitter()
    ui_diffSplitter.setOrientation( QtCore.Qt.Vertical )
    ui_diffSplitter.addWidget( Globals.ui_filesList )
    ui_diffSplitter.addWidget( ui_diffViewAreaWidget )
    ui_diffSplitter.setSizes( [1000, 3000] )

    ui_commitEditorLayout = QtWidgets.QVBoxLayout()
    ui_commitEditorLayout.addWidget( Globals.ui_commitInfo1 )
    if ui_tagAreaWidget:
        ui_commitEditorLayout.addWidget( ui_tagAreaWidget )
    ui_commitEditorLayout.addWidget( Globals.ui_commitInfo2 )
    ui_commitEditorLayout.addWidget( ui_diffSplitter )
    ui_commitEditorWidget = QtWidgets.QWidget()
    ui_commitEditorWidget.setLayout( ui_commitEditorLayout )

    Globals.ui_commitListInfo = QtWidgets.QLabel()

    ui_commitSelectionLayout = QtWidgets.QVBoxLayout()
    ui_commitSelectionLayout.addWidget( ui_filterAreaWidget )
    ui_commitSelectionLayout.addWidget( Globals.ui_commitList )
    ui_commitSelectionLayout.addWidget( Globals.ui_commitListInfo )
    ui_commitSelectionLayout.setStretchFactor( Globals.ui_commitList, 2 )
    ui_commitSelectionWidget = QtWidgets.QWidget()
    ui_commitSelectionWidget.setLayout( ui_commitSelectionLayout )

    ui_centralSplitter = QtWidgets.QSplitter()
    ui_centralSplitter.setOrientation( QtCore.Qt.Horizontal )
    ui_centralSplitter.addWidget( ui_commitSelectionWidget )
    ui_centralSplitter.addWidget( ui_commitEditorWidget )
    ui_centralSplitter.setSizes( [1000, 1000] )

    def mainWindow_onClose():
        Globals.openWindows.clear()
        return True
    ui_window = MainWindow( mainWindow_onClose )
    ui_window.setWindowTitle( '%s (%s)' % (os.path.abspath( Globals.repositoryDir ), Globals.branch) )
    ui_window.setWindowState( QtCore.Qt.WindowMaximized )
    ui_window.setCentralWidget( ui_centralSplitter )

    ui_window.show()

    # note: setHidden() has to be called after window has been shown, that's why this code is here at the bottom
    Filter.doFiltering()

    for i in range( Globals.ui_commitList.topLevelItemCount() ):
        item = Globals.ui_commitList.topLevelItem( i )
        if not item.isHidden():
            Globals.ui_commitList.setCurrentItem( item )
            item.setSelected( True )
            break
    Globals.ui_commitList.setFocus()

    ui_app.exec_()

    if not Globals.readOnlyMode:
        allTagsPerCommitHashBefore = allTagsPerCommitHash
        allTagsPerCommitHash = collections.OrderedDict()
        for commit in Globals.allCommits:
            if commit.tags:
                allTagsPerCommitHash[commit.commitHash] = commit.tags
        if allTagsPerCommitHash or os.path.isfile( filepath_commitsJson ): # do not create file if not necessary
            changed = allTagsPerCommitHash != allTagsPerCommitHashBefore
            if changed:
                button = QtWidgets.QMessageBox.question( None, "Save tags?", "Tags have changed. Save them?" )
                if button == QtWidgets.QMessageBox.Yes:
                    json.dump( allTagsPerCommitHash, open( filepath_commitsJson, 'w' ), indent=2 )

    # save cache

    if not args.no_cache:
        cache = collections.OrderedDict()
        cache['history'] = collections.OrderedDict()
        for commit in Globals.allCommits:
            if commit.hash_filename_history:
                cache['history'][commit.commitHash] = commit.hash_filename_history
        if cache or os.path.isfile( filepath_cacheJson ): # do not create file if not necessary
            json.dump( cache, open( filepath_cacheJson, 'w' ), indent=2 )
