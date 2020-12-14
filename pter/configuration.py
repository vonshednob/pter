import pathlib
import configparser

from pter import common


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
            common.SETTING_CREATE_FROM_SEARCH: 'no',
            common.SETTING_AUTO_ID: 'no',
            common.SETTING_HIDE_SEQUENTIAL: 'yes',
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
            'overdue': '#bf360c',
            'due-today': '#f57f17',
            'due-tomorrow': '#827717',
            'done': '#9e9e9e',
            'context': '#1565c0',
            'project': '#00695c',
            'tracking': '#388e3c',
            'pri-a': '#bf360c',
            'pri-b': '#e65100',
            'pri-c': '#ff6f00',
            'url': '#4527a0',
        },
        common.SETTING_GROUP_GUI: {
            common.SETTING_SINGLE_INSTANCE: 'yes',
            common.SETTING_CLICKABLE: 'yes',
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
            common.SETTING_GK_NEW_REF: '',
            common.SETTING_GK_NEW_AFTER: '',
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
            common.SETTING_GK_TOGGLE_DARK: '',
        },
}


class Configuration:
    def __init__(self, conf):
        self.conf = conf

    def __getitem__(self, group):
        return self.conf[group]

    @property
    def sections(self):
        return self.conf.sections()

    def __contains__(self, item):
        return item in self.conf

    def get(self, group, item, default=None):
        if group in self.conf:
            return self.conf[group].get(item, default)
        else:
            return default

    def bool(self, group, item, default='n'):
        return self.get(group, item, default).lower() in ['y', 'yes', '1', 'true', 'on']

    def list(self, group, item, default='', sep=',', strip=True):
        return [e.strip() if strip else e for e in self.get(group, item, default).split(sep)]

    def number(self, group, item, default='0'):
        value = self.get(group, item, default)
        if value.isnumeric():
            return int(value)
        return None

    def color_pair(self, group, item, default=None):
        value = self.get(group, item, default)
        if value is None or len(value) == 0:
            return None

        result = [None, None]
        for idx, colnr in enumerate(value.split(',')):
            if idx >= 2:
                break
            
            colnr = colnr.strip()

            if not colnr.isnumeric():
                # TODO: accept some colors by name
                continue

            result[idx] = int(colnr)

        return result


def get_config(args):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read_dict(DEFAULT_CONFIG)
    conffile = pathlib.Path(args.config).expanduser().resolve()

    if conffile.exists() and conffile.is_file():
        conf.read([conffile])
    
    return Configuration(conf)

