from PyQt5 import QtWidgets, QtGui, QtCore

repositoryDir = None
branch = None

includeDirectories = []
includeFiles = []
includePaths = [] # used for git commands, contains '.' or dirs and files
excludePatterns = [] # note: not used for git commands

transparentIcon = None

readOnlyMode = False
calculateDiffHashes = False

normalPointSize = 9
smallPointSize = 8

temporarilyNoDiffViewer = False

app = None
ui_progressDialog = None
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
hash_commit_filename_history = {}
hash_commit_filenames_diffHash = {}
hash_commit_filenames_spaceTolerantDiffHash = {}
allTags = []
allTagsGrouped = {}
previousBackgroundList = []

normalFont = None
smallFont = None
courierFont = None
boldFont = None

def initUiGlobals():
    """
    Call this after QtWidgets.QApplication() was constructed.
    """
    global normalFont
    global smallFont
    global courierFont
    global boldFont
    normalFont = QtGui.QFont()
    normalFont.setPointSize( normalPointSize )
    smallFont = QtGui.QFont()
    smallFont.setPointSize( smallPointSize )
    courierFont = QtGui.QFont( 'Courier New' )
    courierFont.setPointSize( smallPointSize )
    boldFont = QtGui.QFont()
    boldFont.setPointSize( smallPointSize )
    boldFont.setBold( True )
