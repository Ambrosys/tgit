
import Globals
import Utils

import site
import os
site.addsitedir( os.path.join( os.path.dirname( __file__ ), 'ansi2html' ) )
import ansi2html

from PyQt5 import QtWidgets, QtGui, QtCore
import threading
import tempfile

filesListItemColumn_lines = 0
filesListItemColumn_filename = 1

def diff_nonblocking( commit, file ):
    file1content = Utils.call( ['git', 'show', '%s~1:%s' % (commit.commitHash, file)], cwd=Globals.repositoryDir )
    file2content = Utils.call( ['git', 'show', '%s:%s' % (commit.commitHash, file)], cwd=Globals.repositoryDir )
    file1 = tempfile.NamedTemporaryFile( mode='w', suffix='_OLD_%s' % os.path.basename(file) )
    file2 = tempfile.NamedTemporaryFile( mode='w', suffix='_NEW_%s' % os.path.basename(file) )
    file1.write( '\n'.join( file1content ) )
    file2.write( '\n'.join( file2content ) )
    file1.flush()
    file2.flush()
    Utils.call( ['meld', file1.name, file2.name], cwd=Globals.repositoryDir )

@QtCore.pyqtSlot()
def on_filesList_itemSelectionChanged():
    items = Globals.ui_filesList.selectedItems()
    if items:
        files = map( lambda item: item.text( filesListItemColumn_filename ), items )
        cmd = ['git', 'show', '--format=', Globals.selectedCommit.commitHash, '--color-words', '--']
        cmd.extend( files )
        diff = Utils.call( cmd, cwd=Globals.repositoryDir )
        conv = ansi2html.Ansi2HTMLConverter( font_size="9pt" )
        ansi = '\n'.join( diff )
        html = conv.convert( ansi )
        #html = '\n'.join( Utils.call( ['ansi2html.sh', '--bg=dark'], input=ansi ) )
        Globals.ui_diffViewer.setHtml( html )

@QtCore.pyqtSlot( QtWidgets.QListWidgetItem )
def on_filesList_itemActivated( item ):
    file = item.text( filesListItemColumn_filename )
    thread = threading.Thread( target=diff_nonblocking, args=(Globals.selectedCommit, file) )
    thread.start()

@QtCore.pyqtSlot( QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem )
def on_filesList_currentItemChanged( current, before ):
    """
    :type current: QtWidgets.QTreeWidgetItem
    :type before: QtWidgets.QTreeWidgetItem
    """
    Globals.ui_followViewerScrollArea.setVisible( bool( current ) )
    if current:
        filename = current.text(filesListItemColumn_filename)
        hashes = Globals.selectedCommit.getHistory( filename )
        htmls = ['<strong>history:</strong> (<a href="history:%s:%s">new window</a>)<br />' % (Globals.selectedCommit.commitHash, filename)]
        htmls.extend( '<br />'.join( map( lambda c: c.getOnelinerHtml( True, filename ), map( lambda h: Globals.allCommitsHash[h], hashes ) ) ) )
        Globals.ui_followViewer.setText( '' )
        QtCore.QCoreApplication.processEvents( QtCore.QEventLoop.ExcludeUserInputEvents ) # dirty workaround to avoid scrolling
        Globals.ui_followViewer.setText( ''.join( htmls ) )
