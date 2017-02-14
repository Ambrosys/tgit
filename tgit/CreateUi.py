import functools
import copy
import collections

from PyQt5 import QtWidgets, QtGui, QtCore

from . import Globals
from . import Filter
from . import GeneralUi


@QtCore.pyqtSlot()
def slot_selectCheckBoxes( checkBoxes, select, slot ):
    for checkBox in checkBoxes:
        checkBox.blockSignals( True )
        checkBox.setChecked( select )
        checkBox.blockSignals( False )
    slot()

def createTagCheckBoxes( groupTags, checkBoxList, checked, slot, allowButtons=True ):
    ui_tagGridLayout = QtWidgets.QGridLayout()
    ui_tagGridLayout.setVerticalSpacing( 0 )

    enabledCheckBoxes = []
    for row, group in enumerate( groupTags ):
        (enabled, tags) = groupTags[group]
        if not tags:
            continue

        ui_tagLineLayout = QtWidgets.QHBoxLayout()

        ui_tagGridLayout.addWidget( QtWidgets.QLabel( '<strong>%s:</strong>' % group ), row, 0 )

        rowCheckBoxList = []
        for tag in tags:
            filterCheckBox = QtWidgets.QCheckBox( tag )
            filterCheckBox.setContentsMargins( 0, 0, 0, 0 )
            rowCheckBoxList.append( filterCheckBox )
            checkBoxList.append( filterCheckBox )
            filterCheckBox.setChecked( checked )
            if enabled:
                filterCheckBox.clicked.connect( slot )
            else:
                filterCheckBox.setEnabled( False )
            ui_tagLineLayout.addWidget( filterCheckBox )

        ui_tagLineLayout.addStretch()

        if enabled and allowButtons:
            # note: If we use lambda below instead of functools.partial,
            #       rowCheckBoxList in the slot refers to the last
            #       rowCheckBoxList defined in this loop. This may be a python
            #       error, because "rowCheckBoxList = []" above states
            #       explicitely that we want a new list instance and do not
            #       want to overwrite the last one. The effect is that each
            #       button toggles all check boxes in the tab instead only
            #       toggling the row.
            ui_selectButton = QtWidgets.QPushButton( '[x]' )
            ui_selectButton.clicked.connect( functools.partial( slot_selectCheckBoxes, rowCheckBoxList, True, slot ) )
            ui_unselectButton = QtWidgets.QPushButton( '[ ]' )
            ui_unselectButton.clicked.connect( functools.partial( slot_selectCheckBoxes, rowCheckBoxList, False, slot ) )
            ui_tagLineLayout.addWidget( ui_selectButton )
            ui_tagLineLayout.addWidget( ui_unselectButton )
            enabledCheckBoxes.extend( rowCheckBoxList )

        ui_tagGridLayout.addLayout( ui_tagLineLayout, row, 1 )

    if enabledCheckBoxes:
        row = len( groupTags )
        #ui_tagGridLayout.addWidget( QtWidgets.QLabel( '<strong>all:</strong>' ), row, 0 )
        ui_selectButton = QtWidgets.QPushButton( 'all' )
        ui_selectButton.clicked.connect( functools.partial( slot_selectCheckBoxes, enabledCheckBoxes, True, slot ) )
        ui_unselectButton = QtWidgets.QPushButton( 'none' )
        ui_unselectButton.clicked.connect( functools.partial( slot_selectCheckBoxes, enabledCheckBoxes, False, slot ) )
        ui_tagLineLayout = QtWidgets.QHBoxLayout()
        ui_tagLineLayout.addStretch()
        ui_tagLineLayout.addWidget( ui_selectButton )
        ui_tagLineLayout.addWidget( ui_unselectButton )
        ui_tagGridLayout.addLayout( ui_tagLineLayout, row, 1 )

    ui_tagGridWidget = QtWidgets.QWidget()
    ui_tagGridWidget.setLayout( ui_tagGridLayout )
    return ui_tagGridWidget

def createFilterTabWidget( definedTagsGrouped, undefinedTags, allAuthorsGrouped ):
    groupTags = collections.OrderedDict()
    for group in Globals.allTagsGrouped:
        groupTags[group] = (True, definedTagsGrouped[group])
    if undefinedTags:
        groupTags['undefined'] = (True, undefinedTags)

    ui_filterTabWidget = QtWidgets.QTabWidget()
    if groupTags:
        ui_filterTabWidget.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed )

        groupTagsWithUntagged = copy.deepcopy( groupTags )
        groupTagsWithUntagged['special'] = (True, ['untagged'])
        ui_filterIncludeWidget1 = createTagCheckBoxes( groupTagsWithUntagged, Globals.ui_filterIncludeCheckBoxes1, True, Filter.doFiltering )
        ui_filterIncludeWidget2 = createTagCheckBoxes( groupTagsWithUntagged, Globals.ui_filterIncludeCheckBoxes2, True, Filter.doFiltering )
        ui_filterObligatoryWidget = createTagCheckBoxes( groupTags, Globals.ui_filterObligatoryCheckBoxes, False, Filter.doFiltering )
        ui_filterExcludeWidget = createTagCheckBoxes( groupTags, Globals.ui_filterExcludeCheckBoxes, False, Filter.doFiltering )
        ui_filterFindFilesWidget = createTagCheckBoxes( groupTags, Globals.ui_filterFindFilesCheckBoxes, False, Filter.doFiltering )
        ui_filterFindFilesIncludeWidget = createTagCheckBoxes( groupTagsWithUntagged, Globals.ui_filterFindFilesIncludeCheckBoxes, True, Filter.doFiltering )

        ui_filterIncludeScrollArea1 = QtWidgets.QScrollArea()
        ui_filterIncludeScrollArea1.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterIncludeScrollArea1.setWidget( ui_filterIncludeWidget1 )
        ui_filterIncludeScrollArea2 = QtWidgets.QScrollArea()
        ui_filterIncludeScrollArea2.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterIncludeScrollArea2.setWidget( ui_filterIncludeWidget2 )
        ui_filterObligatoryScrollArea = QtWidgets.QScrollArea()
        ui_filterObligatoryScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterObligatoryScrollArea.setWidget( ui_filterObligatoryWidget )
        ui_filterExcludeScrollArea = QtWidgets.QScrollArea()
        ui_filterExcludeScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterExcludeScrollArea.setWidget( ui_filterExcludeWidget )
        ui_filterFindFilesScrollArea = QtWidgets.QScrollArea()
        ui_filterFindFilesScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterFindFilesScrollArea.setWidget( ui_filterFindFilesWidget )
        ui_filterFindFilesIncludeScrollArea = QtWidgets.QScrollArea()
        ui_filterFindFilesIncludeScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
        ui_filterFindFilesIncludeScrollArea.setWidget( ui_filterFindFilesIncludeWidget )

        Globals.ui_filterFindFilesForwardCheckBox = QtWidgets.QCheckBox( 'also search forward (slow)' )
        Globals.ui_filterFindFilesForwardCheckBox.setChecked( False )
        Globals.ui_filterFindFilesForwardCheckBox.clicked.connect( Filter.doFiltering )

        ui_filterFindFilesTabWidget = QtWidgets.QTabWidget()
        ui_filterFindFilesTabWidget.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed )
        ui_filterFindFilesTabWidget.addTab( ui_filterFindFilesScrollArea, 'follow files of tags' )
        ui_filterFindFilesTabWidget.addTab( ui_filterFindFilesIncludeScrollArea, 'include tags' )
        ui_filterFindFilesTabWidgetLayout = QtWidgets.QVBoxLayout()
        ui_filterFindFilesTabWidgetLayout.addWidget( Globals.ui_filterFindFilesForwardCheckBox )
        ui_filterFindFilesTabWidgetLayout.addWidget( ui_filterFindFilesTabWidget )
        ui_filterFindFilesTabWidgetWidget = QtWidgets.QWidget()
        ui_filterFindFilesTabWidgetWidget.setLayout( ui_filterFindFilesTabWidgetLayout )

        ui_filterTabWidget.addTab( ui_filterIncludeScrollArea1, 'include tags 1' )
        ui_filterTabWidget.addTab( ui_filterIncludeScrollArea2, 'include tags 2' )
        ui_filterTabWidget.addTab( ui_filterObligatoryScrollArea, 'obligatory tags' )
        ui_filterTabWidget.addTab( ui_filterExcludeScrollArea, 'exclude tags' )
        ui_filterTabWidget.addTab( ui_filterFindFilesTabWidgetWidget, 'find files' )

    existsGroupWithSingleLetter = False # may happen if the group is auto-generated from first letter
    groupAuthors = collections.OrderedDict()
    for group, authors in allAuthorsGrouped.items():
        groupAuthors[group] = (True, authors)
        if len( group ) == 1:
            existsGroupWithSingleLetter = True

    ui_filterAuthorWidget = createTagCheckBoxes( groupAuthors, Globals.ui_filterAuthorCheckBoxes, True, Filter.doFiltering )

    ui_filterAuthorScrollArea = QtWidgets.QScrollArea()
    ui_filterAuthorScrollArea.setFrameShape( QtWidgets.QFrame.NoFrame )
    if existsGroupWithSingleLetter:
        if groupTags:
            ui_filterAuthorScrollArea.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored )
        else:
            ui_filterAuthorScrollArea.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored )
            ui_filterAuthorScrollArea.setMinimumSize( QtCore.QSize( 0, 200.0 ) ) # TODO: find better solution
    ui_filterAuthorScrollArea.setWidget( ui_filterAuthorWidget )

    ui_filterTabWidget.addTab( ui_filterAuthorScrollArea, 'authors' )

    return ui_filterTabWidget

def createHistoryWidgets():
    """
    :return: (container, label)
    :rtype: (QtWidgets.QScrollArea, QtWidgets.QLabel)
    """
    label = QtWidgets.QLabel()
    label.setTextInteractionFlags( QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse )
    label.linkActivated.connect( lambda link: GeneralUi.labelLinkActivated( label, link ) )
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget( label )
    layout.addStretch()
    widget = QtWidgets.QWidget()
    widget.setLayout( layout )
    container = QtWidgets.QScrollArea()
    #container.setFrameShape( QtWidgets.QFrame.NoFrame )
    container.setWidgetResizable( True )
    container.setWidget( widget )
    return container, label
