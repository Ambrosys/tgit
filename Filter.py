
import Globals
import CommitList

from PyQt5 import QtWidgets, QtGui, QtCore
import re

def passesPathFilter( filename ):
    if not Globals.includeDirectories and not Globals.includeFiles:
        found = True
    else:
        found = False
    if not found:
        for include in Globals.includeDirectories:
            if filename[:len(include)+1] == '%s/' % include:
                found = True
                break
    if not found:
        for include in Globals.includeFiles:
            if filename == include:
                found = True
                break
    if found:
        for exclude in Globals.excludePatterns:
            if exclude.match( filename ):
                found = False
                break
    return found

def somePassesPathFilter( filenames, default ):
    passed = default
    for filename in filenames:
        if passesPathFilter( filename ):
            passed = True
            break
        else:
            passed = False
    return passed

def checkSearchTextFilter( commit, searchFilter, filterText, filterRegex ):
    if Globals.ui_searchFilterLineEdit.text():
        found = False
        if not found:
            if 'commit' in searchFilter and commit.commitHash[:len(filterText)] == filterText:
                found = True
        if not found:
            if 'branch' in searchFilter and filterRegex.search( commit.getBranch() ):
                found = True
        if not found:
            if 'message' in searchFilter and filterRegex.search( commit.message ):
                found = True
        if not found:
            if 'files in paths' in searchFilter or 'files not in paths' in searchFilter:
                for filename in commit.getFilenames():
                    if filterRegex.search( filename ):
                        if passesPathFilter( filename ) and 'files in paths' in searchFilter:
                            found = True
                            break
                        elif not passesPathFilter( filename ) and 'files not in paths' in searchFilter:
                            found = True
                            break
        return found
    else:
        return True

@QtCore.pyqtSlot()
def doFiltering():
    activeIncludeSpecialFilter = set()
    for filterCheckBox in Globals.ui_filterIncludeSpecialCheckBoxes:
        if filterCheckBox.isChecked():
            activeIncludeSpecialFilter.add( filterCheckBox.text() )

    activeIncludeFilter1 = set()
    for filterCheckBox in Globals.ui_filterIncludeCheckBoxes1:
        if filterCheckBox.isChecked():
            activeIncludeFilter1.add( filterCheckBox.text() )

    activeIncludeFilter2 = set()
    for filterCheckBox in Globals.ui_filterIncludeCheckBoxes2:
        if filterCheckBox.isChecked():
            activeIncludeFilter2.add( filterCheckBox.text() )

    activeObligatoryFilter = set()
    for filterCheckBox in Globals.ui_filterObligatoryCheckBoxes:
        if filterCheckBox.isChecked():
            activeObligatoryFilter.add( filterCheckBox.text() )

    activeExcludeFilter = set()
    for filterCheckBox in Globals.ui_filterExcludeCheckBoxes:
        if filterCheckBox.isChecked():
            activeExcludeFilter.add( filterCheckBox.text() )

    activeFindFilesFilter = set()
    for filterCheckBox in Globals.ui_filterFindFilesCheckBoxes:
        if filterCheckBox.isChecked():
            activeFindFilesFilter.add( filterCheckBox.text() )

    activeFindFilesIncludeFilter = set()
    for filterCheckBox in Globals.ui_filterFindFilesIncludeCheckBoxes:
        if filterCheckBox.isChecked():
            activeFindFilesIncludeFilter.add( filterCheckBox.text() )

    activeAuthorFilter = set()
    for filterCheckBox in Globals.ui_filterAuthorCheckBoxes:
        if filterCheckBox.isChecked():
            activeAuthorFilter.add( filterCheckBox.text() )

    searchFilter = set()
    for filterCheckBox in Globals.ui_searchFilterCheckBoxes:
        if filterCheckBox.isChecked():
            searchFilter.add( filterCheckBox.text() )

    filterInputText = Globals.ui_searchFilterLineEdit.text()
    try:
        filterRegex = re.compile( filterInputText, re.IGNORECASE )
    except re.error:
        filterRegex = re.compile( r'.*' )

    # follow files and find commits (back in history):
    foundCommitHashes = set()
    for c in Globals.allCommits:
        if set( c.tags ) & activeFindFilesFilter:
            for filename in c.getFilenames():
                if not passesPathFilter( filename ):
                    continue
                hashes = c.getHistory( filename )
                foundCommitHashes.update( set( hashes ) )

    # follow files and find commits (forward in history):
    if Globals.ui_filterFindFilesForwardCheckBox and Globals.ui_filterFindFilesForwardCheckBox.isChecked():
        # 1. find last commit with specified tags
        lastCommit = None
        for c in Globals.allCommits:
            if set( c.tags ) & activeFindFilesFilter:
                lastCommit = c
                break
        # 2. find all commits after the commit found in (2) that have files whose
        # history crosses a commit with specified tags
        if lastCommit:
            for c in reversed( Globals.allCommits ):
                if c == lastCommit:
                    break
                for filename in c.getFilenames():
                    if not passesPathFilter( filename ):
                        continue
                    hashes = c.getHistory( filename )
                    for hash in hashes:
                        if set( Globals.allCommitsHash[hash].tags ) & activeFindFilesFilter:
                            foundCommitHashes.add( c.commitHash )
                            break

    for i in range( 0, Globals.ui_commitList.topLevelItemCount() ):
        item = Globals.ui_commitList.topLevelItem( i )
        commit = Globals.allCommitsHash[item.text( CommitList.commitListItemColumn_commit )]
        shouldBeVisible = True

        if Globals.ui_filterAreaCheckBox.isChecked() and not Globals.ui_filterAreaOnlySearchCheckBox.isChecked():
            if shouldBeVisible:
                if not commit.author in activeAuthorFilter:
                    shouldBeVisible = False

            if shouldBeVisible:
                for tag in activeObligatoryFilter:
                    if not tag in commit.tags:
                        shouldBeVisible = False
                        break

            if shouldBeVisible:
                for tag in activeExcludeFilter:
                    if tag in commit.tags:
                        shouldBeVisible = False
                        break

            if shouldBeVisible:
                if not 'consider all paths' in activeIncludeSpecialFilter and not somePassesPathFilter( commit.getFilenames(), False ):
                    shouldBeVisible = False
                else:
                    if shouldBeVisible:
                        foundATag = False
                        for tag in commit.tags:
                            if tag in activeIncludeFilter1:
                                foundATag = True
                                break
                        if not foundATag:
                            if commit.tags or (Globals.allTags and not 'untagged' in activeIncludeFilter1):
                                shouldBeVisible = False

                    if shouldBeVisible:
                        foundATag = False
                        for tag in commit.tags:
                            if tag in activeIncludeFilter2:
                                foundATag = True
                                break
                        if not foundATag:
                            if commit.tags or (Globals.allTags and not 'untagged' in activeIncludeFilter2):
                                shouldBeVisible = False

                    if shouldBeVisible:
                        if not checkSearchTextFilter( commit, searchFilter, filterInputText, filterRegex ):
                            shouldBeVisible = False

            if not shouldBeVisible:
                if commit.commitHash in foundCommitHashes:
                    foundATag = False
                    for tag in commit.tags:
                        if tag in activeFindFilesIncludeFilter:
                            foundATag = True
                            break
                    if not foundATag:
                        if not commit.tags and (not Globals.allTags or 'untagged' in activeFindFilesIncludeFilter):
                            foundATag = True
                    if foundATag:
                        shouldBeVisible = True
        elif Globals.ui_filterAreaCheckBox.isChecked() and Globals.ui_filterAreaOnlySearchCheckBox.isChecked():
            if shouldBeVisible:
                if not checkSearchTextFilter( commit, searchFilter, filterInputText, filterRegex ):
                    shouldBeVisible = False

        item.setHidden( not shouldBeVisible )

    if Globals.ui_commitList.currentItem():
        Globals.ui_commitList.scrollToItem( Globals.ui_commitList.currentItem() )

    CommitList.slot_updateCommitListInfo()
