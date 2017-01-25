
import Globals
import Filter
import CreateUi
import FileList

from PyQt5 import QtWidgets, QtGui, QtCore

# if we do not hold the windows anywhere, they get garbage-collected before they could ever show up
Globals.openWindows = set()
class Window( QtWidgets.QWidget ):
    def __init__( self ):
        super().__init__()
        Globals.openWindows.add( self )
    def closeEvent( self, event ):
        Globals.openWindows.remove( self )
        event.accept()

@QtCore.pyqtSlot( str )
def on_commitLinkActivated( link ):
    command_history = 'history:'
    if link[:len(command_history)] == command_history:
        (hash,filename) = link[len(command_history):].split( ':', 1 )
        commit = Globals.allCommitsHash[hash]

        layout = QtWidgets.QVBoxLayout()
        (container, label) = CreateUi.createHistoryWidgets()

        hashes = commit.getHistory( filename )
        htmls = ['<strong>history:</strong> (<a href="forward-search:%s">forward-search</a>)<br />' % hash]
        htmls.extend( '<br />'.join( map( lambda c: c.getOnelinerHtml( True, filename ), map( lambda h: Globals.allCommitsHash[h], hashes ) ) ) )
        label.setText( ''.join( htmls ) )

        layout.addWidget( container )
        window = Window()
        window.setLayout( layout )
        #window.resize( 320, 240 )
        window.show()
        return

    if '-' in link:
        (commitHash, filename) = link.split( '-', 1 )
    else:
        (commitHash, filename) = (link, '')

    for item in Globals.ui_commitList.selectedItems():
        item.setSelected( False )
    item = Globals.ui_commitListItemHash[commitHash]

    if filename:
        Globals.temporarilyNoDiffViewer = True
    item.setSelected( True )
    Globals.ui_commitList.setCurrentItem( item )
    if filename:
        Globals.temporarilyNoDiffViewer = False

    if filename:
        for i in range( Globals.ui_filesList.topLevelItemCount() ):
            item = Globals.ui_filesList.topLevelItem( i )
            if item.text( FileList.filesListItemColumn_filename ) == filename:
                item.setSelected( True )
                Globals.ui_filesList.setCurrentItem( item )
                break


@QtCore.pyqtSlot( str )
def labelLinkActivated( label, link ):
    if ':' in link:
        (command, parameters) = link.split( ':', 1 )
        if command == 'history':
            (hash, filename) = parameters.split( ':', 1 )
            commit = Globals.allCommitsHash[hash]

            layout = QtWidgets.QVBoxLayout()
            (container, newLabel) = CreateUi.createHistoryWidgets()

            hashes = commit.getHistory( filename )
            htmls = []
            htmls.extend( ['<a href="forward-search:%s:%s">forward-search (slow)</a>' % (hash, filename)] )
            htmls.extend( ['<br /><span style="color:#e66c1e;">%s</span>' % commit.getOnelinerWithDateHtml( True, filename )] )
            htmls.extend( ['<br /><strong>history</strong> of %s:<br />' % filename] )
            htmls.extend( '<br />'.join( map( lambda c: c.getOnelinerWithDateHtml( True, filename ), map( lambda h: Globals.allCommitsHash[h], hashes ) ) ) )
            newLabel.setText( ''.join( htmls ) )

            layout.addWidget( container )
            window = Window()
            window.setWindowTitle( commit.getOneliner() )
            window.setLayout( layout )
            #window.resize( 320, 240 )
            window.show()
        elif command == 'forward-search':
            (hash, filename) = parameters.split( ':', 1 )
            commit = Globals.allCommitsHash[hash]
            commits = []
            for c in reversed( Globals.allCommits ):
                if c == commit:
                    break
                for f in c.getFilenames():
                    if not Filter.passesPathFilter( f ):
                        continue
                    hashes = c.getHistory( f )
                    foundCommit = False
                    for commit.commitHash in hashes:
                        commits.append( c )
                        foundCommit = True
                        break
                    if foundCommit:
                        break
            htmls = []
            htmls.extend( ['commits whose files in paths <strong>were changed</strong> by %s:<br />' % commit.getShortOnelinerHtml( True )] )
            if commits:
                def getLine( c ):
                    if filename in c.getFilenames():
                        return '%s' % c.getOnelinerWithDateHtml( True, filename )
                    else:
                        return '<span style="color: #aaa;">%s</span>' % c.getOnelinerWithDateHtml( True, filename )
                htmls.extend( '<br />'.join( map( lambda c: getLine( c ), commits ) ) )
            else:
                htmls.extend( '(none)' )
            htmls.extend( ['<br /><span style="color:#e66c1e;">%s</span>' % commit.getOnelinerWithDateHtml( True, filename )] )
            htmls.extend( ['<br /><strong>history</strong> of %s:<br />' % filename] )
            hashes = commit.getHistory( filename )
            htmls.extend( '<br />'.join( map( lambda c: c.getOnelinerWithDateHtml( True, filename ), map( lambda h: Globals.allCommitsHash[h], hashes ) ) ) )
            label.setText( ''.join( htmls ) )
        else:
            print( 'Error: handler for command "%s" not implemented' % command )
    else:
        on_commitLinkActivated( link )
