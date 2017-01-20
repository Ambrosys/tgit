
from PyQt5 import QtWidgets, QtGui, QtCore

repositoryDir = None
branch = None

includeDirectories = []
includeFiles = []
excludePatterns = [] # note: not used for git commands

transparentIcon = None

readOnlyMode = False

normalPointSize = 9
smallPointSize = 8

ui_commitList = None
ui_commitListInfo = None
ui_diffViewer = None
ui_followViewer = None
ui_followViewerScrollArea = None
ui_filesList = None
ui_commitInfo1 = None
ui_commitInfo2 = None
ui_filterAreaCheckBox = None
ui_filterAreaOnlySearchCheckBox = None
ui_filterIncludeSpecialCheckBoxes = []
ui_filterIncludeCheckBoxes1 = []
ui_filterIncludeCheckBoxes2 = []
ui_filterObligatoryCheckBoxes = []
ui_filterExcludeCheckBoxes = []
ui_filterFindFilesCheckBoxes = []
ui_filterFindFilesIncludeCheckBoxes = []
ui_filterFindFilesForwardCheckBox = None
ui_filterAuthorCheckBoxes = []
ui_searchFilterLineEdit = None
ui_searchFilterCheckBoxes = []
ui_tagCheckBoxes = []
ui_commitListItemHash = {}
ui_diffViewerCheckBox = None
selectedCommit = None
allCommits = []
allCommitsHash = {}
allTags = []
allTagsGrouped = {}
previousBackgroundList = []