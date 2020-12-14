"""Common constants for both ncurses and qiui"""
import pathlib
import os
import re

try:
    from xdg import BaseDirectory
except ImportError:
    BaseDirectory = None


PROGRAMNAME = 'pter'
QTPROGRAMNAME = 'qpter'
HERE = pathlib.Path(os.path.abspath(__file__)).parent
HOME = pathlib.Path.home()
CONFIGDIR = HOME / ".config" / PROGRAMNAME
CONFIGFILE = HOME / ".config" / PROGRAMNAME / (PROGRAMNAME + ".conf")
CACHEDIR = HOME / ".cache" / PROGRAMNAME
CACHEFILE = CACHEDIR / (PROGRAMNAME + ".settings")

if BaseDirectory is not None:
    CONFIGDIR = pathlib.Path(BaseDirectory.save_config_path(PROGRAMNAME) or CONFIGDIR)
    CONFIGFILE = CONFIGDIR / (PROGRAMNAME + ".conf")
    CACHEDIR = pathlib.Path(BaseDirectory.save_cache_path(PROGRAMNAME) or CACHEDIR)
    CACHEFILE = CACHEDIR / (PROGRAMNAME + ".settings")

SEARCHES_FILE = CONFIGDIR / "searches.txt"

URL_RE = re.compile(r'([A-Za-z][A-Za-z0-9+\-.]*)://([^ ]+)')

DEFAULT_TASK_FORMAT = '{selection: >} {nr: >} {done} {tracking }{due }{(pri) }{description}'
ATTR_TRACKING = 'tracking'
ATTR_T = 't'
ATTR_DUE = 'due'
ATTR_PRI = 'pri'
ATTR_ID = 'id'

DELEGATE_ACTION_NONE = 'none'
DELEGATE_ACTION_MAIL = 'mail-to'
DELEGATE_ACTIONS = (DELEGATE_ACTION_NONE, DELEGATE_ACTION_MAIL)

SETTING_GROUP_GENERAL = 'General'
SETTING_GROUP_SYMBOLS = 'Symbols'
SETTING_GROUP_COLORS = 'Colors'
SETTING_GROUP_HIGHLIGHT = 'Highlight'
SETTING_GROUP_KEYS = 'Keys'
SETTING_GROUP_EDITORKEYS = 'Editor:Keys'
SETTING_GROUP_GUICOLORS = 'GUI:Colors'
SETTING_GROUP_GUIHIGHLIGHT = 'GUI:Highlight'
SETTING_GROUP_GUIKEYS = 'GUI:Keys'
SETTING_GROUP_GUI = 'GUI'
SETTING_HUMAN_DATES = 'human-friendly-dates'
SETTING_PROTOCOLS = 'protocols'
SETTING_DELEG_MARKER = 'delegation-marker'
SETTING_DELEG_ACTION = 'delegation-action'
SETTING_DELEG_TO = 'delegation-to'
SETTING_DEFAULT_THRESHOLD = 'default-threshold'
SETTING_ADD_CREATED = 'add-creation-date'
SETTING_SEARCH_CASE_SENSITIVE = 'search-case-sensitive'
SETTING_SAFE_SAVE = 'safe-save'
SETTING_SCROLL_MARGIN = 'scroll-margin'
SETTING_SHOW_NUMBERS = 'show-numbers'
SETTING_USE_COLORS = 'use-colors'
SETTING_TASK_FORMAT = 'task-format'
SETTING_CLEAR_CONTEXT = 'clear-context'
SETTING_FONT = 'font'
SETTING_FONTSIZE = 'font-size'
SETTING_SINGLE_INSTANCE = 'single-instance'
SETTING_CREATE_FROM_SEARCH = 'create-from-search'
SETTING_AUTO_ID = 'auto-id'
SETTING_HIDE_SEQUENTIAL = 'hide-sequential'
SETTING_CLICKABLE = 'clickable'
SETTING_ICON_SELECTION = 'selection'
SETTING_ICON_NOT_DONE = 'not-done'
SETTING_ICON_DONE = 'done'
SETTING_ICON_OVERFLOW_LEFT = 'overflow-left'
SETTING_ICON_OVERFLOW_RIGHT = 'overflow-right'
SETTING_ICON_OVERDUE = 'overdue'
SETTING_ICON_DUE_TODAY = 'due-today'
SETTING_ICON_DUE_TOMORROW = 'due-tomorrow'
SETTING_ICON_TRACKING = 'tracking'
SETTING_COL_NORMAL = 'normal'
SETTING_COL_PRI_A = 'pri-a'
SETTING_COL_PRI_B = 'pri-b'
SETTING_COL_PRI_C = 'pri-c'
SETTING_COL_INACTIVE = 'inactive'
SETTING_COL_CONTEXT = 'context'
SETTING_COL_PROJECT = 'project'
SETTING_COL_ERROR = 'error'
SETTING_COL_HELP_TEXT = 'help'
SETTING_COL_HELP_KEY = 'help-key'
SETTING_COL_OVERFLOW = 'overflow'
SETTING_COL_OVERDUE = 'overdue'
SETTING_COL_DUE_TODAY = 'due-today'
SETTING_COL_DUE_TOMORROW = 'due-tomorrow'
SETTING_COL_TRACKING = 'tracking'
SETTING_COL_URL = 'url'
SETTING_GK_QUIT = 'quit'
SETTING_GK_NEW = 'new'
SETTING_GK_NEW_REF = 'new-related'
SETTING_GK_NEW_AFTER = 'new-subsequent'
SETTING_GK_EDIT = 'edit'
SETTING_GK_OPEN_FILE = 'open-file'
SETTING_GK_TOGGLE_DONE = 'toggle-done'
SETTING_GK_SEARCH = 'search'
SETTING_GK_TOGGLE_TRACKING = 'toggle-tracking'
SETTING_GK_OPEN_MANUAL = 'open-manual'
SETTING_GK_NAMED_SEARCHES = 'named-searches'
SETTING_GK_FOCUS_TASKS = 'focus-tasks'
SETTING_GK_TOGGLE_HIDDEN = 'toggle-hidden'
SETTING_GK_TOGGLE_DARK = 'toggle-dark-mode'
SETTING_GK_DELEGATE = 'delegate'

TF_SELECTION = 'selection'
TF_NUMBER = 'nr'
TF_DESCRIPTION = 'description'
TF_DONE = 'done'
TF_TRACKING = 'tracking'
TF_DUE = 'due'
TF_ALL = 'all'
TF_DUEDAYS = 'duedays'
TF_PRIORITY = 'pri'
TF_CREATED = 'created'
TF_COMPLETED = 'completed'
TF_AGE = 'age'

