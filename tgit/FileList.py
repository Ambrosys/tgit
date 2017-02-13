import threading
import tempfile
import hashlib
import site
import re

from PyQt5 import QtWidgets, QtGui, QtCore
import ansi2html

from . import Globals
from . import Utils

filesListItemColumn_diff = 0
filesListItemColumn_lines = 1
filesListItemColumn_filename = 2
filesListItemColumnCount = 3

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
        files = [item.text( filesListItemColumn_filename ) for item in items]
        cmd = ['git', 'show', '--format=', Globals.selectedCommit.commitHash, '--color-words', '--']
        cmd.extend( files )
        diff = Utils.call( cmd, cwd=Globals.repositoryDir )
        conv = ansi2html.Ansi2HTMLConverter( font_size="9pt" )
        ansi = '\n'.join( diff )
        html = conv.convert( ansi )
        #html = '\n'.join( Utils.call( ['ansi2html.sh', '--bg=dark'], input=ansi ) )
        Globals.ui_diffViewer.setHtml( html )

        if Globals.calculateDiffHashes and len( items ) == 1:
            cmd = ['git', 'show', '--format=', Globals.selectedCommit.commitHash, '--']
            cmd.extend( files )
            diff = Utils.call( cmd, cwd=Globals.repositoryDir )
            # replace patterns like "index 5504aae..f60cf6b 100755" or
            # "index 5504aae..f60cf6b" with "index 0000000..0000000 100755"
            # or "index 0000000..0000000" respectively
            regex = re.compile("^index [a-z0-9]+\.\.[a-z0-9]+( [0-9]+)?$")
            diff[:] = [regex.sub( 'index 0000000..0000000\\1', line ) for line in diff]
            if Globals.calculateDiffHashesSpaceTolerant:
                # remove blank lines and white space at EOL
                diff[:] = [line.rstrip() for line in diff if line.strip()]

            m = hashlib.sha1()
            m.update( '\n'.join( diff ).encode('utf-8') )
            item = items[0]
            item.setText( filesListItemColumn_diff, m.digest().hex()[:7] )

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
