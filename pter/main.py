import argparse
import configparser
import pathlib
import sys
import locale

from pytodotxt import TodoTxt

try:
    from pter.curses import run_cursesui
except ImportError:
    run_cursesui = None

try:
    from pter.qtui import run_qtui
    qterr = None
except ImportError as exc:
    run_qtui = None
    qterr = exc

from pter import common
from pter.tr import tr
from pter.configuration import Configuration
from pter.source import Source


DEFAULT_CONFIG = {
        common.SETTING_GROUP_GENERAL: {
            common.SETTING_USE_COLORS: 'yes',
            common.SETTING_SHOW_NUMBERS: 'yes',
            common.SETTING_SCROLL_MARGIN: 5,
            common.SETTING_SAFE_SAVE: 'yes',
            common.SETTING_SEARCH_CASE_SENSITIVE: 'yes',
            common.SETTING_DEFAULT_THRESHOLD: '',
            common.SETTING_HUMAN_DATES: '',
            common.SETTING_DELEG_MARKER: '@delegated',
            common.SETTING_DELEG_ACTION: common.DELEGATE_ACTION_NONE,
            common.SETTING_DELEG_TO: 'to',
            common.SETTING_ADD_CREATED: 'yes',
            common.SETTING_TASK_FORMAT: common.DEFAULT_TASK_FORMAT,
            common.SETTING_CLEAR_CONTEXT: '',
            common.SETTING_PROTOCOLS: 'http,https,mailto,ftp,ftps',
        },
        common.SETTING_GROUP_SYMBOLS: {
            common.SETTING_ICON_SELECTION: '',
            common.SETTING_ICON_NOT_DONE: '[ ]',
            common.SETTING_ICON_DONE: '[x]',
            common.SETTING_ICON_OVERFLOW_LEFT: '←',
            common.SETTING_ICON_OVERFLOW_RIGHT: '→',
            common.SETTING_ICON_OVERDUE: '!!',
            common.SETTING_ICON_DUE_TODAY: '!',
            common.SETTING_ICON_DUE_TOMORROW: '*',
            common.SETTING_ICON_TRACKING: '@',
        },
        common.SETTING_GROUP_COLORS: {
            common.SETTING_COL_NORMAL: '',
            common.SETTING_COL_PRI_A: '',
            common.SETTING_COL_PRI_B: '',
            common.SETTING_COL_PRI_C: '',
            common.SETTING_COL_INACTIVE: '',
            common.SETTING_COL_CONTEXT: '',
            common.SETTING_COL_PROJECT: '',
            common.SETTING_COL_ERROR: '',
            common.SETTING_COL_HELP_TEXT: '',
            common.SETTING_COL_HELP_KEY: '',
            common.SETTING_COL_OVERFLOW: '',
            common.SETTING_COL_OVERDUE: '',
            common.SETTING_COL_DUE_TODAY: '',
            common.SETTING_COL_DUE_TOMORROW: '',
            common.SETTING_COL_TRACKING: '',
        },
        common.SETTING_GROUP_GUICOLORS: {
            'project': '#9c27b0',
            'context': '#2e7d32',
        },
        common.SETTING_GROUP_GUI: {
        },
        common.SETTING_GROUP_KEYS: {
        },
        common.SETTING_GROUP_EDITORKEYS: {
        },
        common.SETTING_GROUP_HIGHLIGHT: {
        },
        common.SETTING_GROUP_GUIHIGHLIGHT: {
        },
        common.SETTING_GROUP_GUIKEYS: {
            common.SETTING_GK_QUIT: 'Ctrl+Q',
            common.SETTING_GK_NEW: 'Ctrl+N',
            common.SETTING_GK_EDIT: 'Ctrl+E',
            common.SETTING_GK_TOGGLE_DONE: 'Ctrl+D',
            common.SETTING_GK_SEARCH: 'Ctrl+F',
            common.SETTING_GK_TOGGLE_TRACKING: 'Ctrl+T',
            common.SETTING_GK_OPEN_MANUAL: 'F1',
            common.SETTING_GK_OPEN_FILE: '',
            common.SETTING_GK_NAMED_SEARCHES: 'F8',
            common.SETTING_GK_FOCUS_TASKS: 'F6',
            common.SETTING_GK_TOGGLE_HIDDEN: 'Ctrl+H',
            common.SETTING_GK_DELEGATE: 'Ctrl+G',
        },
}


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        type=str,
                        default=common.CONFIGFILE,
                        help=tr("Location of your configuration file. Defaults to %(default)s."))
    parser.add_argument('filename',
                        type=str,
                        nargs='*',
                        help=tr('todo.txt file(s) to open'))
    args = parser.parse_args(sys.argv[1:])

    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    sources = [Source(TodoTxt(pathlib.Path(fn).expanduser().resolve())) for fn in args.filename]
    for source in sources:
        if source.filename.exists():
            source.parse()

    conf = configparser.ConfigParser(interpolation=None)
    conf.read_dict(DEFAULT_CONFIG)
    conffile = pathlib.Path(args.config).expanduser().resolve()

    if conffile.exists() and conffile.is_file():
        conf.read([conffile])

    if pathlib.Path(sys.argv[0]).name == 'qpter':
        success = -1
        if run_qtui is None:
            print(tr("PyQt5 is not installed or could otherwise not be imported: {}").format(qterr),
                  file=sys.stderr)
        else:
            success = 0
            run_qtui(Configuration(conf), sources, args)
    elif run_cursesui is not None:
        success = run_cursesui(sources, conf)
    else:
        print(tr("Neither PyQt5 nor curses are installed."), file=sys.stderr)
        success = -2

    return success

