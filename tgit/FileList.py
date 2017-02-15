import os
import threading
import tempfile

from PyQt5 import QtWidgets, QtGui, QtCore

from . import Globals
from . import Utils
from . import GitUtils


filesListItemColumn_diff = 0
filesListItemColumn_lines = 1
filesListItemColumn_status = 2
filesListItemColumn_filename = 3
filesListItemColumnCount = 4

def showContextMenu( item, globalPos ):
    """
    :type item: QtWidgets.QTreeWidgetItem
    :type globalPos: QtCore.QPoint
    """
    parents = Globals.selectedCommit.getParents( Globals.allCommitsHash )
    compareToFile = item.text( filesListItemColumn_filename )
    receiver = CompareFileMenuSlot( compareToFile )
    menu = QtWidgets.QMenu( receiver )
    for parent in parents:
        compareMenu = menu.addMenu( 'compare to %s' % parent.commitHash )
        compareMenu.addAction( compareToFile, receiver.slot_compareFromFile )
        compareFromFiles = []
        for file in parent.files:
            (status, name) = (file.status, file.name)
            if name == compareToFile:
                continue
            if status[0] != 'D' and status[0] != '?':
                compareFromFiles.append( name )
        if compareFromFiles:
            compareMenu.addSeparator()
            for name in compareFromFiles:
                compareMenu.addAction( name, receiver.slot_compareFromFile )

    menu.exec( globalPos )

class CompareFileMenuSlot( QtWidgets.QWidget ):

    def __init__( self, compareToFile ):
        super().__init__()
        self.compareToFile = compareToFile

    @QtCore.pyqtSlot()
    def slot_compareFromFile( self ):
        compareFromFile = self.sender().text()
        compareFromCommitHash = self.sender().parent().title()[11:] # cut out 'compare to '
        thread = threading.Thread( target=diff_nonblocking, args=(compareFromCommitHash, Globals.selectedCommit.commitHash, compareFromFile, self.compareToFile) )
        thread.start()

@QtCore.pyqtSlot( QtCore.QPoint )
def on_filesList_customContextMenuRequested( pos ):
    item = Globals.ui_filesList.itemAt( pos )
    if item:
        showContextMenu( item, Globals.ui_filesList.viewport().mapToGlobal( pos ) )

def diff_nonblocking( fromCommitReference, toCommitReference, fromFile, toFile ):
    file1content = Utils.call( ['git', 'show', '%s:%s' % (fromCommitReference, fromFile)], cwd=Globals.repositoryDir )
    file2content = Utils.call( ['git', 'show', '%s:%s' % (toCommitReference, toFile)], cwd=Globals.repositoryDir )
    file1 = tempfile.NamedTemporaryFile( mode='w', suffix='_%s_%s' % (fromCommitReference, os.path.basename(fromFile)) )
    file2 = tempfile.NamedTemporaryFile( mode='w', suffix='_%s_%s' % (toCommitReference, os.path.basename(toFile)) )
    file1.write( '\n'.join( file1content ) )
    file2.write( '\n'.join( file2content ) )
    file1.flush()
    file2.flush()
    Utils.call( ['meld', file1.name, file2.name], cwd=Globals.repositoryDir )

@QtCore.pyqtSlot()
def on_filesList_itemSelectionChanged():
    items = Globals.ui_filesList.selectedItems()
    if items:
        files = list( map( lambda item: item.text( filesListItemColumn_filename ), items ) )
        Globals.ui_diffViewer.setHtml( GitUtils.getDiffHtml( Globals.selectedCommit.commitHash, files ) )

        if Globals.calculateDiffHashes and len( items ) == 1:
            item = items[0]
            if not item.text( filesListItemColumn_diff ):
                diffHash = GitUtils.getDiffHash( Globals.selectedCommit.commitHash, files, forceGeneration=True )
                item.setText( filesListItemColumn_diff, diffHash )

@QtCore.pyqtSlot( QtWidgets.QListWidgetItem )
def on_filesList_itemActivated( item ):
    file = item.text( filesListItemColumn_filename )
    thread = threading.Thread( target=diff_nonblocking, args=('%s~1' % Globals.selectedCommit.commitHash, Globals.selectedCommit.commitHash, file, file) )
    thread.start()

@QtCore.pyqtSlot( QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem )
def on_filesList_currentItemChanged( current, before ):
    """
    :type current: QtWidgets.QTreeWidgetItem
    :type before: QtWidgets.QTreeWidgetItem
    """

    if current == before:
        return # because this event gets fired if you click on a different column of the same item

    Globals.ui_followViewerScrollArea.setVisible( bool( current ) )
    if current:
        filename = current.text(filesListItemColumn_filename)
        hashes = Globals.selectedCommit.getHistory( filename )
        htmls = ['<strong>history:</strong> (<a href="history:%s:%s">new window</a>)<br />' % (Globals.selectedCommit.commitHash, filename)]
        htmls.extend( '<br />'.join( map( lambda c: c.getOnelinerHtml( True, filename ), map( lambda h: Globals.allCommitsHash[h], hashes ) ) ) )
        Globals.ui_followViewer.setText( '' )
        QtCore.QCoreApplication.processEvents( QtCore.QEventLoop.ExcludeUserInputEvents ) # dirty workaround to avoid scrolling
        Globals.ui_followViewer.setText( ''.join( htmls ) )
