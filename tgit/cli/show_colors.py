import os
import argparse
import signal

from PyQt5 import QtWidgets, QtGui, QtCore

from .. import Colors
from .. import Authors
from .. import Globals


def addColor( ui_list, color, name, alignRight ):
    color_normalized = Colors.optimizeForBackground( color )
    item = QtWidgets.QTreeWidgetItem( [
        name,
        color.name(),
        name,
        color_normalized.name()
    ] )
    if alignRight:
        item.setTextAlignment( 0, QtCore.Qt.AlignRight )
        item.setTextAlignment( 2, QtCore.Qt.AlignRight )
    item.setFont( 0, Globals.boldFont )
    item.setFont( 1, Globals.courierFont )
    item.setFont( 2, Globals.boldFont )
    item.setFont( 3, Globals.courierFont )
    item.setBackground( 0, QtGui.QBrush( color ) )
    item.setBackground( 1, QtGui.QBrush( color ) )
    item.setBackground( 2, QtGui.QBrush( color_normalized ) )
    item.setBackground( 3, QtGui.QBrush( color_normalized ) )
    ui_list.addTopLevelItem( item )

def main():
    signal.signal( signal.SIGINT, signal.SIG_DFL )

    parser = argparse.ArgumentParser( description='Color test utility for tgit.' )
    parser.add_argument( '--authors', metavar='FILENAME', type=str, default='tgit-authors.json', help = 'authors config file, default: %(default)s' )
    args = parser.parse_args()

    ui_app = QtWidgets.QApplication( [] )
    ui_app.setWindowIcon( QtGui.QIcon( os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), '../../img/tgit-logo.svg' ) ) )

    Globals.initUiGlobals()

    QtWidgets.QApplication.setFont( Globals.normalFont )

    Authors.load( args.authors )

    # building window...

    ui_list = QtWidgets.QTreeWidget()
    ui_list.setRootIsDecorated( False )
    ui_list.setHeaderItem( QtWidgets.QTreeWidgetItem( [
        'name',
        'original color',
        'name',
        'distance to white = 9.0'
    ] ) )
    ui_list.setColumnCount( 4 )
    ui_list.header().setSectionResizeMode( QtWidgets.QHeaderView.ResizeToContents )
    ui_list.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )

    if Authors.map_author_originalColor:
        ui_list.addTopLevelItem( QtWidgets.QTreeWidgetItem( ['', '', '', ''] ) )
        for group, authors in Authors.allAuthorsGrouped.items():
            for author in authors:
                if author in Authors.map_author_originalColor:
                    addColor( ui_list, Authors.map_author_originalColor[author], author, alignRight=False )
    ui_list.addTopLevelItem( QtWidgets.QTreeWidgetItem( ['', '', '', ''] ) )
    for i in range( len( Colors.colors ) ):
        addColor( ui_list, QtGui.QColor( Colors.colors[i] ), str(i + 1), alignRight=True )
    ui_list.addTopLevelItem( QtWidgets.QTreeWidgetItem( ['', '', '', ''] ) )

    ui_window = QtWidgets.QMainWindow()
    ui_window.setWindowTitle( 'Colors' )
    ui_window.setCentralWidget( ui_list )

    ui_window.resize( 700, 700 )

    ui_window.show()

    ui_app.exec_()

if __name__ == '__main__':
    main()
