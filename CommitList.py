
import Globals
import Utils
import Filter
import FileList

import site
import os
site.addsitedir( os.path.join( os.path.dirname( __file__ ), 'ansi2html' ) )
import ansi2html

from PyQt5 import QtWidgets, QtGui, QtCore

commitListItemColumn_index = 0
commitListItemColumn_commit = 1
commitListItemColumn_lines = 2
commitListItemColumn_tags = 3
commitListItemColumn_date = 4
commitListItemColumn_author = 5
commitListItemColumn_branch = 6
commitListItemColumn_message = 7

def showContextMenu( item, globalPos ):
    """
    :type item: QtWidgets.QTreeWidgetItem
    :type globalPos: QtCore.QPoint
    """
    receiver = TagMenuSlot()
    menu = QtWidgets.QMenu( receiver )
    if not Globals.readOnlyMode:
        addMenu = menu.addMenu( 'add' )
        removeMenu = menu.addMenu( 'remove' )
        for group in Globals.allTagsGrouped:
            addSubMenu = addMenu.addMenu( group )
            removeSubMenu = removeMenu.addMenu( group )
            for tag in Globals.allTagsGrouped[group]:
                addSubMenu.addAction( tag, receiver.slot_addTag )
                removeSubMenu.addAction( tag, receiver.slot_removeTag )
    menu.addAction( 'copy hashes', on_action_copyHashes )
    menu.addAction( 'copy hashes, tags, message', on_action_copyHashesWithTagsAndMessage )

    menu.exec( globalPos )

def updateTagsOfTreeWidgetItem( commit ):
    Globals.ui_commitListItemHash[commit.commitHash].setText( commitListItemColumn_tags, commit.getTagsOneliner() )

class TagMenuSlot( QtWidgets.QWidget ):

    @QtCore.pyqtSlot()
    def slot_addTag( self ):
        tag = self.sender().text()
        for item in Globals.ui_commitList.selectedItems():
            commit = Globals.allCommitsHash[item.text( commitListItemColumn_commit )]
            if not tag in commit.tags:
                commit.tags.append( tag )
                updateTagsOfTreeWidgetItem( commit )
        on_commitList_currentItemChanged( Globals.ui_commitList.currentItem(), None )
        Filter.doFiltering()

    @QtCore.pyqtSlot()
    def slot_removeTag( self ):
        tag = self.sender().text()
        for item in Globals.ui_commitList.selectedItems():
            commit = Globals.allCommitsHash[item.text( commitListItemColumn_commit )]
            if tag in commit.tags:
                commit.tags.remove( tag )
                updateTagsOfTreeWidgetItem( commit )
        on_commitList_currentItemChanged( Globals.ui_commitList.currentItem(), None )
        Filter.doFiltering()

@QtCore.pyqtSlot()
def on_action_copyHashes():
    lines = []
    for item in Globals.ui_commitList.selectedItems():
        commit = Globals.allCommitsHash[item.text( commitListItemColumn_commit )]
        lines.append( commit.commitHash )
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText( '\n'.join( lines ) )

@QtCore.pyqtSlot()
def on_action_copyHashesWithTagsAndMessage():
    lines = []
    for item in Globals.ui_commitList.selectedItems():
        commit = Globals.allCommitsHash[item.text( commitListItemColumn_commit )]
        line = []
        line.append( commit.commitHash )
        line.extend( map( lambda t: '[%s]' % t, commit.getTagsSorted() ) )
        line.append( commit.getMessageOneliner() )
        lines.append( ' '.join( line ) )
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText( '\n'.join( lines ) )

@QtCore.pyqtSlot( QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem )
def on_commitList_currentItemChanged( current, before ):
    """
    :type current: QtWidgets.QTreeWidgetItem
    :type before: QtWidgets.QTreeWidgetItem
    """

    pixmap = QtGui.QPixmap( 64, 64 )
    pixmap.fill( QtGui.QColor( 230, 108, 30, 255 ) )

    smallFont = QtGui.QFont()
    smallFont.setPointSize( Globals.smallPointSize )

    # restore backgrounds
    for (item, brush) in Globals.previousBackgroundList:
        #for col in [commitListItemColumn_commit]: # range( item.columnCount() ):
        #    item.setBackground( col, brush )
        item.setIcon( 0, Globals.transparentIcon )

    if current:
        Globals.selectedCommit = Globals.allCommitsHash[current.text( commitListItemColumn_commit )]

        for tagCheckBox in Globals.ui_tagCheckBoxes:
            tagCheckBox.setChecked( tagCheckBox.text() in Globals.selectedCommit.tags )

        Globals.ui_commitInfo1.setText( Globals.selectedCommit.getMultilinerHtml() )

        children = map( lambda c: '<strong>child:</strong> %s<br />' % c.getOnelinerHtml( True ), Globals.selectedCommit.getChildren() )
        parents = map( lambda c: '<strong>parent:</strong> %s<br />' % c.getOnelinerHtml( True ), Globals.selectedCommit.getParents( Globals.allCommitsHash ) )
        childrenParents = '%s%s' % (''.join(children), ''.join(parents))
        if childrenParents[-6:] == '<br />':
            childrenParents = childrenParents[:-6]
        author = '<strong>author:</strong> %s (%s), <strong>email:</strong> %s' % (Globals.selectedCommit.author, Globals.selectedCommit.originalAuthor, Globals.selectedCommit.email)
        Globals.ui_commitInfo2.setText( '%s<br />%s' % (author, childrenParents) )

        Globals.ui_filesList.clear()
        for file in Globals.selectedCommit.files:
            (status, name) = (file.status, file.name)
            readableLines = str( file.added + file.removed )
            item = QtWidgets.QTreeWidgetItem( [readableLines, name] )
            for i in range( 8 ):
                item.setFont( i, smallFont )
            if Filter.passesPathFilter( name ):
                colors = {
                    'M': item.foreground(0),
                    'A': QtGui.QBrush( QtCore.Qt.darkGreen ),
                    'D': QtGui.QBrush( QtCore.Qt.red ),
                    'C': item.foreground(0),
                    'R': item.foreground(0),
                    'T': item.foreground(0),
                    'U': item.foreground(0)
                    }
                item.setForeground( FileList.filesListItemColumn_filename, colors[status[0]] )
            else:
                colors = {
                    'M': QtGui.QBrush( QtCore.Qt.lightGray ),
                    'A': QtGui.QBrush( QtGui.QColor(164,192,164) ),
                    'D': QtGui.QBrush( QtGui.QColor(255,192,192) ),
                    'C': QtGui.QBrush( QtCore.Qt.lightGray ),
                    'R': QtGui.QBrush( QtCore.Qt.lightGray ),
                    'T': QtGui.QBrush( QtCore.Qt.lightGray ),
                    'U': QtGui.QBrush( QtCore.Qt.lightGray )
                    }
                item.setForeground( FileList.filesListItemColumn_lines, QtGui.QBrush( QtCore.Qt.lightGray ) )
                item.setForeground( FileList.filesListItemColumn_filename, colors[status[0]] )
            Globals.ui_filesList.addTopLevelItem( item )

        # set parents/children background
        family = []
        family.extend( Globals.selectedCommit.getParents( Globals.allCommitsHash ) )
        family.extend( Globals.selectedCommit.getChildren() )
        for c in family:
            item = Globals.ui_commitListItemHash[c.commitHash]
            Globals.previousBackgroundList.append( (item, item.background(0)) )
            #for col in [commitListItemColumn_commit]: # range( item.columnCount() ):
            #    item.setBackground( col, QtGui.QBrush( QtGui.QColor( 230, 108, 30, 32 ) ) )
            item.setIcon( 0, QtGui.QIcon( pixmap ) )

        if Globals.ui_diffViewerCheckBox.isChecked() and not Globals.temporarilyNoDiffViewer:
            cmd = ['git', 'show', '--format=', Globals.selectedCommit.commitHash, '--color-words', '--']
            if Globals.includeDirectories or Globals.includeFiles:
                cmd.extend( Globals.includeDirectories )
                cmd.extend( Globals.includeFiles )
            else:
                cmd.append( '.' )
            diff = Utils.call( cmd, cwd=Globals.repositoryDir )
            conv = ansi2html.Ansi2HTMLConverter( font_size="9pt" )
            ansi = '\n'.join( diff )
            html = conv.convert( ansi )
            #html = '\n'.join( Utils.call( ['ansi2html.sh', '--bg=dark'], input=ansi ) )
            Globals.ui_diffViewer.setHtml( html )
        else:
            Globals.ui_diffViewer.setHtml( '<html><body style="background: black;"></body></html>' )

@QtCore.pyqtSlot( QtCore.QPoint )
def on_commitList_customContextMenuRequested( pos ):
    item = Globals.ui_commitList.itemAt( pos )
    if item:
        showContextMenu( item, Globals.ui_commitList.viewport().mapToGlobal( pos ) )

@QtCore.pyqtSlot()
def slot_updateCommitListInfo():
    visibleItemsCount = 0
    for i in range( Globals.ui_commitList.topLevelItemCount() ):
        item = Globals.ui_commitList.topLevelItem( i )
        if not item.isHidden():
            visibleItemsCount += 1
    Globals.ui_commitListInfo.setText( '%i/%i visible commits (%i selected)' % (
        visibleItemsCount,
        Globals.ui_commitList.topLevelItemCount(),
        len( Globals.ui_commitList.selectedItems() )
    ))
