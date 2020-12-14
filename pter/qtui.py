import datetime
import html
import re
import configparser
import pathlib
import getpass
import sys
import webbrowser
import os

from pytodotxt import Task, TodoTxt

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

try:
    import qdarkstyle
except ImportError:
    qdarkstyle = None


from pter import common
from pter import utils
from pter import version
from pter import configuration
from pter.source import Source
from pter.searcher import Searcher
from pter.tr import tr


HEX_COLOR = re.compile(r'^#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F][0-9a-fA-F])?$')
NAMED_COLOR = re.compile(r'^[a-zA-Z]+$')

TASK_ROLE = Qt.UserRole + 1
SOURCE_ROLE = Qt.UserRole + 2
SORT_ROLE = Qt.UserRole + 3

ICON_PATH = common.HERE / "icons"

ABOUT_DIALOG_TEXT = '''<h1>About {qtprogramname}</h1>
<h2>Personal Task Entropy Reducer</h2>
<p>{qtprogramname} is the Qt user interface to {programname}.</p>
<p>This is version {version}.</p>
<h2>License</h2>
<p>{programname} is open source software and licensed under MIT License. You
can obtain the source code from <a href="https://github.com/vonshednob/pter">GitHub</a>
or <a href="https://pypi.org/project/pter">PyPI</a>.</p>'''

COLOR_PROJECT = 'project'
COLOR_CONTEXT = 'context'
COLOR_OVERDUE = 'overdue'
COLOR_DUE_TODAY = 'due-today'
COLOR_DUE_TOMORROW = 'due-tomorrow'
COLOR_NORMAL = 'normal'
COLOR_DONE = 'done'
COLOR_TRACKING = 'tracking'
COLOR_PRI_A = 'pri-a'
COLOR_PRI_B = 'pri-b'
COLOR_PRI_C = 'pri-c'

SETTING_GROUP_FILES = 'Files'
SETTING_GROUP_SAVEDSEARCHES = 'SavedSearches'
SETTING_GROUP_SEARCH_EDITOR = 'Search'
SETTING_GROUP_MAINWINDOW = 'Window'
SETTING_GROUP_CREATE = 'CreateTask'
SETTING_DARK_MODE = 'dark-mode'
SETTING_VISIBLE = 'visible'
SETTING_DOCKING = 'docking'
SETTING_FLOATING = 'floating'
SETTING_POSITION = 'position'
SETTING_SIZE = 'size'
SETTING_MR_SOURCE = 'most-recent-source'
SETTING_MR_SEARCH = 'most-recent-search'
DOCK_LEFT = 'left'
DOCK_RIGHT = 'right'
DOCK_TOP = 'top'
DOCK_BOTTOM = 'bottom'


def tr(text):
    return text


def parse_colors(config, section):
    result = {}
    for name in config[section]:
        color = config[section][name]

        if HEX_COLOR.match(color):
            result[name.lower()] = color
        elif NAMED_COLOR.match(color):
            result[name.lower()] = color
    return result


class SettingsStorage(configuration.Configuration):
    def __init__(self):
        super().__init__(None)
        try:
            common.CACHEDIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        self.has_changes = False
        self.accept_changes = False
        self.load()
    
    def load(self):
        self.has_changes = False
        if not common.CACHEFILE.exists():
            common.CACHEFILE.write_text("")
        self.conf = configparser.ConfigParser(interpolation=None)
        self.conf.read([common.CACHEFILE])

    def save(self):
        if not self.has_changes or not self.accept_changes:
            return
        common.CACHEDIR.mkdir(parents=True, exist_ok=True)
        with open(common.CACHEFILE, 'wt', encoding='utf-8') as fd:
            self.conf.write(fd)
        self.has_changes = False

    def docking(self, group, key, default):
        raw = self.get(group, key, '')
        if raw == DOCK_LEFT:
            return Qt.LeftDockWidgetArea
        if raw == DOCK_RIGHT:
            return Qt.RightDockWidgetArea
        if raw == DOCK_TOP:
            return Qt.TopDockWidgetArea
        if raw == DOCK_BOTTOM:
            return Qt.BottomDockWidgetArea
        return default

    def update(self, group, key, value):
        if not self.accept_changes:
            return
        self.has_changes = True
        if group not in self.conf:
            self.conf[group] = {}
        if isinstance(value, bool):
            value = 'yes' if value else 'no'
        self.conf[group][key] = value


class DecorationContext:
    def __init__(self,
                 human_friendly_dates,
                 font,
                 colors,
                 attr_colors):
        self.human_friendly_dates = human_friendly_dates
        self.font = font
        self.color = colors
        self.attr_color = attr_colors
        self.fontmetrics = QtGui.QFontMetrics(self.font)
        self.space_width = self.fontmetrics.boundingRect("w m").width() - \
                           self.fontmetrics.boundingRect("mw").width()

        for colorname in self.color.keys():
            self.color[colorname] = QtGui.QColor(self.color[colorname])
        for colorname in self.attr_color.keys():
            self.attr_color[colorname] = QtGui.QColor(self.attr_color[colorname])


class DecoratedTask:
    def __init__(self, context, task):
        self.context = context
        self._task = task
        self.state_color = self.context.color.get(COLOR_NORMAL, None)
        self.diffdays = None
        self.age = None
        self.words = []
        self.rects = []
        self.width = 0

        self.rebuild()

    def parse(self, line):
        self._task.parse(line)
        self.rebuild()

    def rebuild(self):
        self.state_color = self.context.color.get(COLOR_NORMAL, None)
        self.diffdays = None
        self.age = None
        if self.creation_date is not None:
            self.age = (datetime.date.today() - self.creation_date).days
        if self._task.is_completed:
            self.state_color = self.context.color.get(COLOR_DONE, None) \
                               or self.state_color
        else:
            self.diffdays = utils.task_due_in_days(self._task)
            if self.diffdays is not None:
                if self.diffdays < 0:
                    self.state_color = self.context.color.get(COLOR_OVERDUE, None) \
                                       or self.state_color
                if self.diffdays == 0:
                    self.state_color = self.context.color.get(COLOR_DUE_TODAY, None) \
                                       or self.state_color
                if self.diffdays == 1:
                    self.state_color = self.context.color.get(COLOR_DUE_TOMORROW, None) \
                                       or self.state_color

        self.words = []
        if self._task.description is not None:
            for word in self._task.description.split(' '):
                if ':' in word:
                    name, value = word.split(':', 1)
                    if name in [common.TF_DUE, common.TF_COMPLETED, common.TF_CREATED] and \
                       len(self.context.human_friendly_dates.intersection({common.TF_ALL, name})) > 0:
                        word = f"{name}:{utils.human_friendly_date(value)}"
                self.words.append((word, self.context.fontmetrics.boundingRect(word)))
        self.width = self.context.fontmetrics.boundingRect(' '.join([w[0] for w in self.words])).width()

    def __str__(self):
        return str(self._task)

    def __getattr__(self, name):
        if hasattr(self._task, name):
            return getattr(self._task, name)
        raise AttributeError(name)

    @property
    def description(self):
        return self._task.description

    @description.setter
    def description(self, value):
        self._task.description = value

    @property
    def is_completed(self):
        return self._task.is_completed

    @is_completed.setter
    def is_completed(self, value):
        self._task.is_completed = value

    @property
    def priority(self):
        return self._task.priority

    @priority.setter
    def priority(self, value):
        self._task.priority = value

    @property
    def completion_date(self):
        return self._task.completion_date

    @completion_date.setter
    def completion_date(self, value):
        self._task.completion_date = value

    @property
    def creation_date(self):
        return self._task.creation_date

    @creation_date.setter
    def creation_date(self, value):
        self._task.creation_date = value

    @property
    def linenr(self):
        return self._task.linenr

    @linenr.setter
    def linenr(self, value):
        self._task.linenr = value

    @property
    def raw(self):
        return self._task.raw

    @raw.setter
    def raw(self, value):
        self._task.raw = value

    @property
    def todotxt(self):
        return self._task.todotxt

    @todotxt.setter
    def todotxt(self, value):
        self._task.todotxt = value


class TaskDataModel(QtCore.QAbstractTableModel):
    COLUMN_DONE = 0
    COLUMN_DESCRIPTION = 1
    COLUMN_PRIORITY = 2
    COLUMN_CREATED = 3
    COLUMN_COMPLETED = 4
    COLUMN_DUE = 5
    COLUMN_DUE_IN_DAYS = 6
    COLUMN_AGE = 7
    COLUMN_IS_TRACKING = 8
    COLUMNS = 9  # keep this +1 ahead of the defined columns

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.sources = []
        self._tasks = []
        self.human_friendly_dates = set(config.list(common.SETTING_GROUP_GENERAL,
                                                    common.SETTING_HUMAN_DATES))
        self.done_marker = (utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                     common.SETTING_ICON_NOT_DONE)),
                            utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                     common.SETTING_ICON_DONE)))
        self.due_marker = (utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                    common.SETTING_ICON_OVERDUE)),
                           utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                    common.SETTING_ICON_DUE_TODAY)),
                           utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                    common.SETTING_ICON_DUE_TOMORROW)))
        self.tracking_marker = utils.unquote(config.get(common.SETTING_GROUP_SYMBOLS,
                                                        common.SETTING_ICON_TRACKING))
        self.colors = parse_colors(config, common.SETTING_GROUP_GUICOLORS)
        self.attr_colors = parse_colors(config, common.SETTING_GROUP_GUIHIGHLIGHT)
        self.font = QtGui.QFont(QtWidgets.QApplication.font())
        fontsize = config.get(common.SETTING_GROUP_GUI, common.SETTING_FONTSIZE, None)
        if fontsize is not None and len(fontsize.strip()) > 0:
            if fontsize.endswith('px'):
                self.font.setPixelSize(int(fontsize[:-2]))
            else:
                if fontsize.endswith('pt'):
                    fontsize = fontsize[:-2]
                self.font.setPointSizeF(float(fontsize))
        fontname = config.get(common.SETTING_GROUP_GUI, common.SETTING_FONT, None)
        if fontname is not None and len(fontname.strip()) > 0:
            self.font.setFamily(fontname)
        self.dcontext = DecorationContext(self.human_friendly_dates,
                                          self.font,
                                          self.colors,
                                          self.attr_colors)
        self.reload()

    def reload(self):
        self.beginResetModel()
        self._tasks = []
        for source in self.sources:
            self._tasks += [DecoratedTask(self.dcontext, task)
                            for task in source.tasks]
        self.endResetModel()

    def ensure_up_to_date(self, index):
        task = index.data(TASK_ROLE)
        if task.todotxt.refresh():
            self.beginResetModel()
            self._tasks = []
            for source in [s for s in self.sources if s is not task.todotxt]:
                self._tasks += [DecoratedTask(self.dcontext, other) 
                                for other in source.tasks]
            new_row_nr = None
            for that in task.todotxt.parse():
                self._tasks.append(DecoratedTask(self.dcontext, that))
                if that.raw == task.raw:
                    new_row_nr = len(self._tasks) - 1
            self.endResetModel()

            if new_row_nr is None:
                return None
            index = self.createIndex(new_row_nr, 0)
            assert index.data(TASK_ROLE).raw == task.raw
            assert index.data(TASK_ROLE) is not task

        return index

    def task(self, index):
        return self._tasks[index.row()]

    def setData(self, index, value, role=Qt.EditRole):
        value.rebuild()
        self.dataChanged.emit(index, index)
        return True

    def add_task(self, task):
        count = len(self._tasks)
        self.beginInsertRows(self.createIndex(count-1, 0), count, count)
        self._tasks.append(DecoratedTask(self.dcontext, task))
        self.endInsertRows()

    def data(self, index, role):
        if role == TASK_ROLE:
            return self.task(index)
        if role == SOURCE_ROLE:
            return self.task(index).todotxt
        if role == SORT_ROLE:
            return utils.sort_fnc(self.task(index))
        if role == Qt.FontRole:
            return self.font

        if index.column() == TaskDataModel.COLUMN_DONE:
            if role == Qt.DisplayRole:
                return self.done_marker[1 if self.task(index).is_completed else 0]

        task = self.task(index)

        if index.column() == TaskDataModel.COLUMN_DESCRIPTION:
            if role == Qt.DisplayRole:
                return task.description
            if role in (Qt.ForegroundRole, Qt.BackgroundRole):
                return QtGui.QBrush(Qt.transparent)


        if index.column() == TaskDataModel.COLUMN_PRIORITY:
            if role == Qt.DisplayRole:
                return task.priority or ""
            if role == Qt.ForegroundRole and task.priority is not None:
                color = self.colors.get(globals().get('COLOR_PRI_' + task.priority, ""), None)
                if color is not None:
                    return QtGui.QColor(color)

        if index.column() == TaskDataModel.COLUMN_CREATED:
            if role == Qt.DisplayRole:
                if task.creation_date is None:
                    return None
                if len(self.human_friendly_dates.intersection({common.TF_ALL, common.TF_CREATED})) > 0:
                    return utils.human_friendly_date(task.creation_date)
                return task.creation_date.strftime(Task.DATE_FMT)

        if index.column() == TaskDataModel.COLUMN_COMPLETED:
            if role == Qt.DisplayRole:
                if task.completion_date is None:
                    return None
                if len(self.human_friendly_dates.intersection({common.TF_ALL, common.TF_COMPLETED})) > 0:
                    return utils.human_friendly_date(task.completion_date)
                return task.completion_date.strftime(Task.DATE_FMT)

        if index.column() == TaskDataModel.COLUMN_AGE:
            if role == Qt.DisplayRole:
                if task.creation_date is None:
                    return None
                return (task.creation_date - datetime.date.today()).days

        if index.column() == TaskDataModel.COLUMN_IS_TRACKING:
            is_tracking = len(task.attr_tracking) > 0
            if role == Qt.DisplayRole:
                return self.tracking_marker if is_tracking else ""
        if role == Qt.ForegroundRole and len(task.attr_tracking) > 0:
            color = self.colors.get(COLOR_TRACKING, None)
            if color is not None:
                return QtGui.QColor(color)

        if index.column() == TaskDataModel.COLUMN_DUE and \
           task.diffdays is not None and \
           not task.is_completed and \
           role == Qt.DisplayRole:
            value = ""
            if task.diffdays < 0:
                return self.due_marker[0]
            if task.diffdays == 0:
                return self.due_marker[1]
            if task.diffdays == 1:
                return self.due_marker[2]
            return ""

        if index.column() == TaskDataModel.COLUMN_DUE_IN_DAYS and task.diffdays is not None and role == Qt.DisplayRole:
            return task.diffdays

        if task.diffdays is not None and not task.is_completed and role == Qt.ForegroundRole:
            if task.diffdays < 0:
                return QtGui.QColor(self.colors.get(COLOR_OVERDUE, None) or task.state_color)
            if task.diffdays == 0:
                return QtGui.QColor(self.colors.get(COLOR_DUE_TODAY, None) or task.state_color)
            if task.diffdays == 1:
                return QtGui.QColor(self.colors.get(COLOR_DUE_TOMORROW, None) or task.state_color)

        if role == Qt.ForegroundRole:
            return task.state_color

        return None

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        return " "

    def rowCount(self, index):
        return len(self._tasks)

    def columnCount(self, index):
        return TaskDataModel.COLUMNS


class TaskProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, config, searcher, parent=None):
        super().__init__(parent)
        self.config = config
        self.searcher = searcher
        self.setDynamicSortFilter(True)

    def lessThan(self, left, right):
        return left.data(SORT_ROLE) > right.data(SORT_ROLE)

    def filterAcceptsRow(self, rowidx, parent):
        task = self.sourceModel().data(self.sourceModel().index(rowidx, 0), TASK_ROLE)
        return self.searcher.match(task)


class TaskList(QtWidgets.QTreeView):
    wordClicked = QtCore.pyqtSignal(str)

    def __init__(self, config, menu, parent):
        super().__init__(parent)
        self.config = config
        self.clickable_protocols = config.list(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_PROTOCOLS)

        self.setAllColumnsShowFocus(True)
        self.contextmenu = menu
        self.header().setSectionsMovable(True)
        self.clickable = config.bool(common.SETTING_GROUP_GUI,
                                     common.SETTING_CLICKABLE)
        self.mouse_down = None
        self.setMouseTracking(self.clickable)

    def setModel(self, model):
        super().setModel(model)

        if model is not None:
            mapping = {'description': TaskDataModel.COLUMN_DESCRIPTION,
                       'created': TaskDataModel.COLUMN_CREATED,
                       'age': TaskDataModel.COLUMN_AGE,
                       'completed': TaskDataModel.COLUMN_COMPLETED,
                       'done': TaskDataModel.COLUMN_DONE,
                       'pri': TaskDataModel.COLUMN_PRIORITY,
                       'due': TaskDataModel.COLUMN_DUE,
                       'duedays': TaskDataModel.COLUMN_DUE_IN_DAYS,
                       'tracking': TaskDataModel.COLUMN_IS_TRACKING}
            # Hide everything
            self.header().setSectionHidden(TaskDataModel.COLUMN_DESCRIPTION, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_DONE, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_AGE, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_PRIORITY, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_DUE, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_DUE_IN_DAYS, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_CREATED, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_COMPLETED, True)
            self.header().setSectionHidden(TaskDataModel.COLUMN_IS_TRACKING, True)
            # go by configuration and show/move things into place
            task_format = utils.parse_task_format(self.config.get(common.SETTING_GROUP_GENERAL,
                                                                  common.SETTING_TASK_FORMAT))
            position = 0
            header = self.header()
            for item in task_format:
                if not isinstance(item, tuple):
                    continue
                key = item[0]
                if key in ['selection', 'nr']:
                    continue
                column = mapping[key]

                header.setSectionHidden(column, False)
                resizemode = QtWidgets.QHeaderView.ResizeToContents
                if key == 'description':
                    resizemode = QtWidgets.QHeaderView.Stretch
                header.setSectionResizeMode(column, resizemode)
                header.moveSection(header.visualIndex(column), position)

                position += 1

    def get_selected_index(self):
        for index in self.selectedIndexes():
            return index
        return None

    def handle_on_click(self, task, word):
        if word.startswith('@'):
            self.wordClicked.emit(word)
        elif word.startswith('+'):
            self.wordClicked.emit(word)
        else:
            if word.startswith('uri:') or word.startswith('url:'):
                word = word[4:]
            elif word.startswith('<') and word.endswith('>'):
                word = word[1:-1]

            if ':' in word:
                proto, url = word.split(':', 1)
                if proto in self.clickable_protocols and len(url) > 0:
                    webbrowser.open(word)

    def handle_mouse_over(self, task, word):
        if word.startswith('@'):
            return Qt.PointingHandCursor
        elif word.startswith('+'):
            return Qt.PointingHandCursor
        else:
            if word.startswith('uri:') or word.startswith('url:'):
                word = word[4:]
            elif word.startswith('<') and word.endswith('>'):
                word = word[1:-1]

            if ':' in word:
                proto, url = word.split(':', 1)
                if proto in self.clickable_protocols and len(url) > 0:
                    return Qt.PointingHandCursor
        return Qt.ArrowCursor

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.contextmenu.popup(event.globalPos())
        if event.button() == Qt.LeftButton and self.clickable:
            self.mouse_down = None
            index = self.indexAt(event.pos())
            if index is not None:
                task = index.data(TASK_ROLE)
                if task is not None and len(task.rects) > 0:
                    for rect, word in task.rects:
                        if rect.contains(event.pos()):
                            self.mouse_down = (task, word, rect)
                            break

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.clickable and self.mouse_down is not None and event.button() == Qt.LeftButton:
            task, word, rect = self.mouse_down
            if rect.contains(event.pos()):
                self.handle_on_click(task, word)
            self.mouse_down = None

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.clickable:
            index = self.indexAt(event.pos())
            cursor = Qt.ArrowCursor
            if index is not None:
                task = index.data(TASK_ROLE)
                if task is not None and len(task.rects) > 0:
                    for rect, word in task.rects:
                        if rect.contains(event.pos()):
                            cursor = self.handle_mouse_over(task, word)
                            break
            if self.cursor() != cursor:
                self.setCursor(cursor)


class TaskDescriptionDelegate(QtWidgets.QAbstractItemDelegate):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.clickable_protocols = config.list(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_PROTOCOLS)

    def paint(self, painter, option, index):
        painter.save()
        task = index.data(TASK_ROLE)
        painter.setFont(task.context.font)
        painter.setClipRect(option.rect)
        baseline = option.rect.y() + task.context.fontmetrics.ascent()
        cursor = option.rect.x()
        task.rects = []
        for word, rect in task.words:
            color = task.state_color
            clickable = False
            if len(word) > 1:
                if word.startswith('+'):
                    color = task.context.color.get(COLOR_PROJECT, None) or color
                    clickable = True
                elif word.startswith('@'):
                    color = task.context.color.get(COLOR_CONTEXT, None) or color
                    clickable = True
                elif word.startswith('<') and word.endswith('>'):
                    color = task.context.color.get(common.SETTING_COL_URL, None) or color
                    clickable = True
                elif ':' in word:
                    name, _ = word.lower().split(':', 1)
                    color = task.context.attr_color.get(name, None)

                    clickable = name in self.clickable_protocols
                    if clickable and color is None:
                        color = task.context.color.get(common.SETTING_COL_URL, None)
                    color = color or task.state_color
            if color is None:
                color = option.palette.text().color()
            painter.setPen(color)
            if clickable:
                task.rects.append((QtCore.QRect(cursor, option.rect.y(), rect.width(), rect.height()),
                                   word))
                # for debugging clickable areas:
                # painter.drawRect(task.rects[-1][0])
            painter.drawText(cursor, baseline, word)
            cursor += rect.width() + task.context.space_width
        if task.is_completed:
            painter.setPen(task.state_color)
            middle = option.rect.y() + task.context.fontmetrics.height()/2
            painter.drawLine(option.rect.x(), middle,
                             cursor-task.context.space_width, middle)
        painter.restore()

    def sizeHint(self, option, index):
        task = index.data(TASK_ROLE)
        return QtCore.QSize(task.width, task.context.fontmetrics.height())


class DockWithSettings(QtWidgets.QDockWidget):
    def __init__(self, settings, title, parent=None):
        super().__init__(title, parent)
        self.group = ''
        self.defaults = {SETTING_DOCKING: Qt.RightDockWidgetArea,
                         SETTING_VISIBLE: 'no'}
        self.settings = settings

    def store_setting_location(self, location):
        mapping = {Qt.TopDockWidgetArea: DOCK_TOP,
                   Qt.BottomDockWidgetArea: DOCK_BOTTOM,
                   Qt.LeftDockWidgetArea: DOCK_LEFT,
                   Qt.RightDockWidgetArea: DOCK_RIGHT}
        self.location = location
        if mapping.get(location, None) is None:
            return
        self.settings.update(self.group, SETTING_DOCKING, mapping[location])

    def store_setting_visible(self, visible):
        self.settings.update(self.group, SETTING_VISIBLE, visible)

    def restore_at(self, window):
        window.addDockWidget(self.settings.docking(self.group,
                                                   SETTING_DOCKING,
                                                   self.defaults[SETTING_DOCKING]), self)
        if self.settings.bool(self.group, SETTING_VISIBLE, self.defaults[SETTING_VISIBLE]):
            self.show()
        else:
            self.hide()
        
        self.setFloating(self.settings.bool(self.group, SETTING_FLOATING, 'no'))

        pos = [int(v) for v in self.settings.list(self.group, SETTING_POSITION, "") if v.isnumeric()]
        if len(pos) == 2:
            self.move(*pos)

        size = [int(v) for v in self.settings.list(self.group, SETTING_SIZE, "") if v.isnumeric()]
        if len(size) == 2:
            self.resize(*size)

    def store_size(self):
        self.settings.update(self.group,
                             SETTING_POSITION,
                             f"{self.pos().x()},{self.pos().y()}")
        self.settings.update(self.group,
                             SETTING_SIZE,
                             f"{self.size().width()},{self.size().height()}")


class DockSearchEditor(DockWithSettings):
    def __init__(self, settings, searcher, title, parent=None):
        super().__init__(settings, title, parent)
        self.group = SETTING_GROUP_SEARCH_EDITOR
        self.searcher = searcher
        self.defaults = {SETTING_VISIBLE: 'yes',
                         SETTING_DOCKING: Qt.TopDockWidgetArea}

        self.completion = None
        self.editor = QtWidgets.QLineEdit(self)
        self.setWidget(QtWidgets.QWidget(self))
        layout = QtWidgets.QHBoxLayout(self.widget())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)
        self.saveButton = QtWidgets.QPushButton(tr("Save"), self)
        layout.addWidget(self.saveButton)

        self.setAllowedAreas(Qt.DockWidgetAreas(Qt.TopDockWidgetArea + Qt.BottomDockWidgetArea))

    def update_completion(self, words):
        self.editor.setCompleter(None)
        if self.completion is not None:
            del self.completion
        self.completion = QtWidgets.QCompleter(words, self)
        self.editor.setCompleter(self.completion)


class DockSavedSearches(DockWithSettings):
    def __init__(self, settings, title, parent=None):
        super().__init__(settings, title, parent)
        self.group = SETTING_GROUP_SAVEDSEARCHES

        self.location = None
        self.searches = utils.parse_searches()
        self.model = QtCore.QStringListModel(self)
        self.view = None

        self.model.setStringList(self.searches.keys())

        self.construct()

    def construct(self):
        self.view = QtWidgets.QListView(self)
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.view.setModel(self.model)
        self.setWidget(QtWidgets.QWidget(self))
        layout = QtWidgets.QVBoxLayout(self.widget())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.dockLocationChanged.connect(self.store_setting_location)
        self.topLevelChanged.connect(lambda floating: self.settings.update(SETTING_GROUP_SAVEDSEARCHES,
                                                                           SETTING_FLOATING,
                                                                           floating))
        self.visibilityChanged.connect(self.store_setting_visible)

    def add_search(self, name, text):
        existed_before = name in self.searches
        self.searches[name] = text
        if not existed_before:
            self.model.setStringList(sorted(self.searches.keys()))
        utils.save_searches(self.searches)


class DockTaskEditor(QtWidgets.QDockWidget):
    def __init__(self, settings, title, parent=None):
        super().__init__(title, parent)

        self.settings = settings
        self.tm_index = None
        self.completion = None
        self.editor = QtWidgets.QLineEdit(self)
        self.setWidget(QtWidgets.QWidget(self.editor))
        horizontalLayout = QtWidgets.QHBoxLayout(self.widget())
        horizontalLayout.addWidget(self.editor)
        self.saveButton = QtWidgets.QPushButton(tr("&Save"), self.widget())
        cancelButton = QtWidgets.QPushButton(tr("&Cancel"), self.widget())
        horizontalLayout.addWidget(self.saveButton)
        horizontalLayout.addWidget(cancelButton)

        self.saveAction = QtWidgets.QAction(tr("Save"), self.editor)
        self.saveAction.setShortcut(QtGui.QKeySequence("Return"))
        self.saveAction.setShortcutContext(Qt.WidgetShortcut)
        self.addAction(self.saveAction)

        self.cancelAction = QtWidgets.QAction(tr("Cancel"), self.editor)
        self.cancelAction.setShortcut(QtGui.QKeySequence("Escape"))
        self.cancelAction.setShortcutContext(Qt.WidgetShortcut)
        self.cancelAction.triggered.connect(self.do_cancel)
        self.addAction(self.cancelAction)

        cancelButton.clicked.connect(self.do_cancel)

        self.setAllowedAreas(Qt.DockWidgetAreas(Qt.TopDockWidgetArea + Qt.BottomDockWidgetArea))

    def has_changes(self):
        if self.tm_index is None:
            return False
        return str(self.tm_index.data(TASK_ROLE)).strip() != self.editor.text().strip()

    def set_task(self, tm_index):
        self.tm_index = tm_index
        self.editor.setText(str(tm_index.data(TASK_ROLE)))

    def clear_task(self):
        self.tm_index = None
        self.editor.setText("")

    def do_cancel(self):
        self.clear_task()
        self.hide()

    def update_completion(self, words):
        self.editor.setCompleter(None)
        if self.completion is not None:
            del self.completion
        self.completion = QtWidgets.QCompleter(words, self)
        self.editor.setCompleter(self.completion)


class DockTaskCreator(DockWithSettings):
    def __init__(self, settings, config, title, parent=None):
        super().__init__(settings, title, parent)
        self.group = SETTING_GROUP_CREATE

        self.config = config
        self.sources = []
        self.completion = None
        self.add_creation_date = self.config.bool(common.SETTING_GROUP_GENERAL,
                                                  common.SETTING_ADD_CREATED)
        self.mr_source = self.settings.get(self.group, SETTING_MR_SOURCE, None)

        self.setWidget(QtWidgets.QWidget(self))
        verticalLayout = QtWidgets.QVBoxLayout(self.widget())
        topwidget = QtWidgets.QWidget(self.widget())
        verticalLayout.addWidget(topwidget)
        hlayout = QtWidgets.QHBoxLayout(topwidget)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.editor = QtWidgets.QLineEdit(topwidget)
        hlayout.addWidget(self.editor)
        bottomwidget = QtWidgets.QWidget(self.widget())
        horizontalLayout = QtWidgets.QHBoxLayout(bottomwidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.chkCreationDate = QtWidgets.QCheckBox(tr("Add creation &date"), bottomwidget)
        self.chkCreationDate.setChecked(self.add_creation_date)
        horizontalLayout.addWidget(self.chkCreationDate)
        self.sourceSelector = QtWidgets.QComboBox(self)
        horizontalLayout.addWidget(self.sourceSelector)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtWidgets.QPushButton(tr("&Cancel"), bottomwidget)
        horizontalLayout.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(tr("&Save"), topwidget)
        hlayout.addWidget(self.saveButton)
        verticalLayout.addWidget(bottomwidget)
        self.cancelButton.clicked.connect(self.do_cancel)

    def do_cancel(self):
        if len(self.sources) > 0:
            self.mr_source = self.sources[self.sourceSelector.currentIndex()].filename
        self.chkCreationDate.setChecked(self.add_creation_date)
        self.editor.setText("")
        self.hide()

    def do_show(self):
        self.sourceSelector.clear()
        pre_select = None
        for idx, source in enumerate(self.sources):
            self.sourceSelector.addItem(source.displayname)
            if str(source.filename) == self.mr_source:
                pre_select = idx
        if pre_select is not None:
            self.sourceSelector.setCurrentIndex(pre_select)
        self.show()

    def store_size(self):
        super().store_size()

        self.settings.update(self.group,
                             SETTING_MR_SOURCE,
                             str(self.mr_source))

    def update_completion(self, words):
        self.editor.setCompleter(None)
        if self.completion is not None:
            del self.completion
        self.completion = QtWidgets.QCompleter(words, self)
        self.editor.setCompleter(self.completion)


class MainWindow(QMainWindow):
    def __init__(self, config, pidfile, sources):
        super().__init__()
        self.config = config
        self.pidfile = pidfile
        self.settings = SettingsStorage()
        self.menubar = None
        self.taskList = None
        self.searcher = Searcher(None,
                                 self.config.bool(common.SETTING_GROUP_GENERAL,
                                                  common.SETTING_SEARCH_CASE_SENSITIVE),
                                 self.config.get(common.SETTING_GROUP_GENERAL,
                                                 common.SETTING_DEFAULT_THRESHOLD),
                                 self.config.bool(common.SETTING_GROUP_GENERAL,
                                                  common.SETTING_HIDE_SEQUENTIAL))
        self.taskModel = TaskDataModel(config)
        self.proxyModel = TaskProxyModel(config, self.searcher)
        self.proxyModel.setSourceModel(self.taskModel)
        self.descriptionDelegate = TaskDescriptionDelegate(config)
        self.editor = None
        self.creator = None
        self.searchDock = None
        self.savedSearchesDock = None
        self.completion = None
        self.editMenu = None
        self.sources = sources

        self.watcher = QtCore.QFileSystemWatcher(self)

        self.safe_save = self.config.bool(common.SETTING_GROUP_GENERAL,
                                          common.SETTING_SAFE_SAVE)
        self.create_from_search = self.config.bool(common.SETTING_GROUP_GENERAL,
                                                   common.SETTING_CREATE_FROM_SEARCH)
        self.auto_id = self.config.bool(common.SETTING_GROUP_GENERAL,
                                        common.SETTING_AUTO_ID)

        self.actionOpen = QtWidgets.QAction(tr("&Open…"), self)
        self.actionQuit = QtWidgets.QAction(tr("&Quit"), self)
        self.openSourcesSeparator = None

        self.actionNew = QtWidgets.QAction(tr("&New"), self)
        self.actionEdit = QtWidgets.QAction(tr("&Edit"), self)
        self.actionToggleDone = QtWidgets.QAction(tr("Toggle &done"), self)
        self.actionSearch = QtWidgets.QAction(tr("&Search"), self)
        self.actionSearches = QtWidgets.QAction(tr("&Named searches"), self)
        self.actionToggleTracking = QtWidgets.QAction(tr("Toggle &tracking"), self)
        self.actionToggleHidden = QtWidgets.QAction(tr("Toggle &hidden"), self)
        self.actionFocusTasks = QtWidgets.QAction(tr("Focus &tasks"), self)
        self.actionDelegate = QtWidgets.QAction(tr("Dele&gate task"), self)
        self.actionNewRefTask = QtWidgets.QAction(tr("New &related task"), self)
        self.actionNewAfterTask = QtWidgets.QAction(tr("New &subsequent task"), self)
        self.actionToggleDarkStyle = None

        if qdarkstyle is not None:
            self.actionToggleDarkStyle = QtWidgets.QAction(tr("Toggle &dark mode"))
            self.actionToggleDarkStyle.triggered.connect(self.do_toggle_dark_mode)
            if self.settings.bool(SETTING_GROUP_MAINWINDOW, SETTING_DARK_MODE, "no"):
                QtWidgets.QApplication.instance().setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

        self.actionOpenManual = QtWidgets.QAction(tr("Open &manual"), self)
        self.actionShowAbout = QtWidgets.QAction(tr("&About"), self)
        self.actionShowAboutQt = QtWidgets.QAction(tr("About &Qt"), self)

        self.construct()
        self.show()
        self.searchDock.editor.setText(self.settings.get(SETTING_GROUP_MAINWINDOW, SETTING_MR_SEARCH, ""))

        self.actionOpenManual.triggered.connect(utils.open_manual)

        self.update_search(self.searchDock.editor.text())

        self.server = QtNetwork.QLocalServer(self)
        servername = pidfile.stem + "-" + str(os.getpid())
        attempt = 0
        if self.server.listen(servername):
            pidfile.write_text(self.server.fullServerName())
            self.server.newConnection.connect(self.on_new_connection)
        else:
            print(f"Could not listen on {servername}", file=sys.stderr)
            del self.server
            self.server = None

        self.settings.accept_changes = True

    def construct(self):
        centralwidget = QtWidgets.QWidget(self)
        horizontalLayout = QtWidgets.QHBoxLayout(centralwidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.editMenu = QtWidgets.QMenu(tr("&Edit"), self.menubar)
        self.taskList = TaskList(self.config, self.editMenu, centralwidget)
        self.taskList.setModel(self.proxyModel)
        self.taskList.setRootIsDecorated(False)
        self.taskList.setSortingEnabled(True)
        self.taskList.setHeaderHidden(True)
        self.taskList.setItemDelegateForColumn(TaskDataModel.COLUMN_DESCRIPTION, self.descriptionDelegate)
        horizontalLayout.addWidget(self.taskList)
        self.setCentralWidget(centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 338, 20))
        self.menubar.setMinimumSize(0, 20)
        self.programMenu = QtWidgets.QMenu(tr("&Program"), self.menubar)
        searchMenu = QtWidgets.QMenu(tr("&Search"), self.menubar)
        helpMenu = QtWidgets.QMenu(tr("&Help"), self.menubar)
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.programMenu.addAction(self.actionOpen)
        self.programMenu.addAction(self.actionFocusTasks)
        self.programMenu.addSeparator()
        if self.actionToggleDarkStyle is not None:
            self.programMenu.addAction(self.actionToggleDarkStyle)
            self.programMenu.addSeparator()
        self.programMenu.addAction(self.actionQuit)
        searchMenu.addAction(self.actionSearch)
        searchMenu.addAction(self.actionSearches)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actionNew)
        self.editMenu.addAction(self.actionNewRefTask)
        self.editMenu.addAction(self.actionNewAfterTask)
        self.editMenu.addAction(self.actionEdit)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actionDelegate)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actionToggleTracking)
        self.editMenu.addAction(self.actionToggleDone)
        self.editMenu.addAction(self.actionToggleHidden)
        helpMenu.addAction(self.actionOpenManual)
        helpMenu.addSeparator()
        helpMenu.addAction(self.actionShowAbout)
        helpMenu.addAction(self.actionShowAboutQt)
        self.menubar.addAction(self.programMenu.menuAction())
        self.menubar.addAction(self.editMenu.menuAction())
        self.menubar.addAction(searchMenu.menuAction())
        self.menubar.addAction(helpMenu.menuAction())

        size = [int(n) for n in self.settings.list(SETTING_GROUP_MAINWINDOW, SETTING_SIZE, "500,300")]
        self.resize(*size)

        keymapping = [
                (common.SETTING_GK_QUIT, self.actionQuit, Qt.ApplicationShortcut),
                (common.SETTING_GK_NEW, self.actionNew, Qt.ApplicationShortcut),
                (common.SETTING_GK_NEW_REF, self.actionNewRefTask, Qt.WindowShortcut),
                (common.SETTING_GK_NEW_AFTER, self.actionNewAfterTask, Qt.WindowShortcut),
                (common.SETTING_GK_EDIT, self.actionEdit, Qt.WindowShortcut),
                (common.SETTING_GK_TOGGLE_DONE, self.actionToggleDone, Qt.WindowShortcut),
                (common.SETTING_GK_SEARCH, self.actionSearch, Qt.ApplicationShortcut),
                (common.SETTING_GK_TOGGLE_TRACKING, self.actionToggleTracking, Qt.WindowShortcut),
                (common.SETTING_GK_OPEN_MANUAL, self.actionOpenManual, Qt.ApplicationShortcut),
                (common.SETTING_GK_NAMED_SEARCHES, self.actionSearches, Qt.ApplicationShortcut),
                (common.SETTING_GK_FOCUS_TASKS, self.actionFocusTasks, Qt.ApplicationShortcut),
                (common.SETTING_GK_OPEN_FILE, self.actionOpen, Qt.ApplicationShortcut),
                (common.SETTING_GK_TOGGLE_HIDDEN, self.actionToggleHidden, Qt.WindowShortcut),
                (common.SETTING_GK_DELEGATE, self.actionDelegate, Qt.WindowShortcut),
                (common.SETTING_GK_TOGGLE_DARK, self.actionToggleDarkStyle, Qt.ApplicationShortcut),
                ]
        for name, target, context in keymapping:
            keys = self.config.get(common.SETTING_GROUP_GUIKEYS, name)
            if len(keys) > 0 and target is not None:
                target.setShortcut(QtGui.QKeySequence(keys))
                target.setShortcutContext(context)

        self.searchDock = DockSearchEditor(self.settings, self.searcher, tr("Search"))
        self.addDockWidget(self.settings.docking(SETTING_GROUP_SEARCH_EDITOR,
                                                 SETTING_DOCKING,
                                                 Qt.TopDockWidgetArea), self.searchDock)
        self.searchDock.editor.textChanged.connect(self.update_search)
        self.searchDock.editor.returnPressed.connect(self.taskList.setFocus)
        self.actionSearch.triggered.connect(self.do_show_search)
        self.searchDock.saveButton.clicked.connect(self.do_save_search)

        self.savedSearchesDock = DockSavedSearches(self.settings, tr("Named Searches"))
        self.actionSearches.triggered.connect(self.do_show_saved_searches)
        self.savedSearchesDock.view.activated.connect(self.do_activate_saved_search)
        self.savedSearchesDock.restore_at(self)

        self.actionFocusTasks.triggered.connect(self.taskList.setFocus)
        self.actionShowAbout.triggered.connect(self.do_show_about)

        self.taskModel.dataChanged.connect(self.refresh_caches)
        self.taskModel.modelReset.connect(self.refresh_caches)
        self.taskModel.rowsInserted.connect(self.refresh_caches)

        self.taskList.wordClicked.connect(self.add_to_search)

    def refresh_caches(self):
        for source in self.sources:
            source.update_contexts_and_projects()
        self.searcher.update_sources(self.sources)
        self.taskList.model().invalidate()
        self.taskList.model().dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def update_completers(self, words):
        self.searchDock.update_completion(words)
        if self.creator is not None:
            self.creator.update_completion(words)
        if self.editor is not None:
           self.editor.update_completion(words)

    def add_to_search(self, word):
        if word in self.searcher.text.split(' '):
            return
        self.searchDock.editor.setText(self.searchDock.editor.text() + " " + word)

    def update_search(self, text):
        self.searcher.text = text
        self.settings.update(SETTING_GROUP_MAINWINDOW, SETTING_MR_SEARCH, text)
        self.searcher.parse()
        self.proxyModel.invalidate()

    def start_editor(self, tm_index):
        if self.editor is None:
            self.editor = DockTaskEditor(self.settings, tr("Edit task"))
            self.addDockWidget(Qt.BottomDockWidgetArea, self.editor)
            self.editor.saveButton.clicked.connect(self.do_save_task)
            self.editor.editor.returnPressed.connect(self.do_save_task)

        self.editor.set_task(tm_index)
        self.editor.editor.setFocus()
        self.editor.show()

    def start_creator(self, sources):
        if self.creator is None:
            self.creator = DockTaskCreator(self.settings, self.config, tr("New task"))
            self.addDockWidget(Qt.BottomDockWidgetArea, self.creator)
            self.creator.saveButton.clicked.connect(self.do_create_task)
            self.creator.editor.returnPressed.connect(self.do_create_task)

        if sorted(self.creator.sources) != sorted(self.sources):
            self.sources = sources
            self.creator.sources = sources
        self.creator.sourceSelector.setVisible(len(sources) > 1)

        if self.create_from_search:
            text = utils.create_from_search(self.searcher)
            if len(text) > 0:
                text += " "
            self.creator.editor.setText(text)

        self.creator.editor.setFocus()
        self.creator.do_show()

    def store_size(self):
        self.settings.update(SETTING_GROUP_MAINWINDOW,
                             SETTING_POSITION,
                             f"{self.pos().x()},{self.pos().y()}")
        self.settings.update(SETTING_GROUP_MAINWINDOW,
                             SETTING_SIZE,
                             f"{self.size().width()},{self.size().height()}")
        if self.savedSearchesDock is not None:
            self.savedSearchesDock.store_size()
        if self.creator is not None:
            self.creator.store_size()

    def do_toggle_dark_mode(self):
        if qdarkstyle is None:
            return
        current = self.settings.bool(SETTING_GROUP_MAINWINDOW, SETTING_DARK_MODE, "no")
        current = not current
        self.settings.update(SETTING_GROUP_MAINWINDOW, SETTING_DARK_MODE, current)
        if current:
            stylesheet = qdarkstyle.load_stylesheet(qt_api="pyqt5")
        else:
            stylesheet = ""
        QtWidgets.QApplication.instance().setStyleSheet(stylesheet)
        self.taskList.model().invalidate()

    def do_save_task(self):
        text = self.editor.editor.text().strip()
        if not self.editor.has_changes() or len(text) == 0:
            self.editor.do_cancel()
            return
        text = utils.auto_task_id(self.sources, text)
        text = utils.dehumanize_dates(text)
        taskindex = self.editor.tm_index
        task = taskindex.data(TASK_ROLE)
        if str(task) != text:
            taskindex = self.taskModel.ensure_up_to_date(taskindex)
            success = False
            if taskindex is not None:
                task = taskindex.data(TASK_ROLE)
                task.parse(text)
                task.todotxt.save(safe=self.safe_save)
                success = True
            else:
                # TODO: report error
                pass

            if success:
                self.taskModel.setData(taskindex, task)
                self.editor.do_cancel()

    def do_create_task(self):
        if len(self.creator.sources) == 0:
            self.creator.do_cancel()
            return
        source = self.creator.sources[self.creator.sourceSelector.currentIndex()]
        self.creator.mr_source = source.filename

        text = self.creator.editor.text().strip()
        if len(text) == 0:
            self.creator.do_cancel()
            return

        if self.auto_id and not any([word.startswith('id:') for word in text.split(' ')]):
            text += ' id:#'
        text = utils.auto_task_id(self.sources, text)
        text = utils.dehumanize_dates(text)
        task = Task(text, todotxt=source)
        if task.creation_date is None and self.creator.chkCreationDate.isChecked():
            task.creation_date = datetime.date.today()
            task.parse(str(task))
        update_all = False
        if source.refresh():
            update_all = True
            source.parse()
        source.tasks.append(task)
        task.linenr = len(source.tasks)-1
        source.save(safe=self.safe_save)
        if update_all:
            source.parse()
            self.taskModel.reload()
        else:
            self.taskModel.add_task(task)
        self.creator.do_cancel()

    def do_show_search(self):
        self.searchDock.show()
        self.searchDock.editor.setFocus()

    def do_show_saved_searches(self):
        self.savedSearchesDock.show()
        self.savedSearchesDock.view.setFocus()

    def do_activate_saved_search(self, index):
        name = index.data(Qt.DisplayRole)
        if name in self.savedSearchesDock.searches:
            self.searchDock.editor.setText(self.savedSearchesDock.searches[name])

    def do_save_search(self):
        if len(self.searchDock.editor.text().strip()) == 0:
            return

        name, ok = QtWidgets.QInputDialog.getText(self,
                                                  tr("Save Search"),
                                                  tr("Name of the new saved search"),
                                                  QtWidgets.QLineEdit.Normal,
                                                  "")
        if ok and len(name.strip()) > 0:
            self.savedSearchesDock.add_search(name, self.searchDock.editor.text())

    def do_show_about(self):
        QtWidgets.QMessageBox.about(self,
                                    tr(common.QTPROGRAMNAME),
                                    tr(ABOUT_DIALOG_TEXT)
                                        .format(version=version.__version__,
                                                qtprogramname=common.QTPROGRAMNAME,
                                                programname=common.PROGRAMNAME))

    def on_new_connection(self):
        if self.server is None or not self.server.hasPendingConnections():
            return
        
        sock = self.server.nextPendingConnection()
        while True:
            sock.waitForReadyRead(1000)
            if sock.bytesAvailable() == 4:
                cmd = sock.readLine(4)
                if str(cmd, 'ascii') == "new":
                    self.activateWindow()
                    self.actionNew.trigger()
                elif str(cmd, 'ascii') == "hoi":
                    continue
            break
        sock.abort()

    def closeEvent(self, event):
        if self.server is not None:
            self.server.close()
            del self.server
            self.server = None
        self.store_size()

        self.settings.save()
        self.settings.accept_changes = False
        try:
            self.pidfile.unlink(missing_ok=True)
        except:
            pass
        event.accept()


class Program:
    def __init__(self, config, sources, pidfile):
        self.config = config
        self.sources = sources

        self.clear_contexts = [context for context in config.list(common.SETTING_GROUP_GENERAL,
                                                                  common.SETTING_CLEAR_CONTEXT)
                               if len(context) > 0]
        self.safe_save = self.config.bool(common.SETTING_GROUP_GENERAL, common.SETTING_SAFE_SAVE)
        self.delegate_marker = self.config.get(common.SETTING_GROUP_GENERAL, common.SETTING_DELEG_MARKER).strip()
        self.delegate_to = self.config.get(common.SETTING_GROUP_GENERAL, common.SETTING_DELEG_TO).strip()
        self.delegate_action = self.config.get(common.SETTING_GROUP_GENERAL, common.SETTING_DELEG_ACTION).strip()

        if self.delegate_action not in common.DELEGATE_ACTIONS:
            self.delegate_action = common.DELEGATE_ACTION_NONE

        self.icon = QtGui.QIcon()
        for size in [16, 32, 64]:
            fn = f'qpter_{size}x{size}.png'
            fullpath = ICON_PATH / fn
            if fullpath.exists():
                self.icon.addFile(str(fullpath), QtCore.QSize(size, size))

        self.window = MainWindow(config, pidfile, sources)
        self.window.actionOpen.triggered.connect(self.do_open_source)
        self.window.actionQuit.triggered.connect(self.do_quit)
        self.window.actionNew.triggered.connect(self.do_create)
        self.window.actionNewRefTask.triggered.connect(lambda: self.do_create_ref('ref'))
        self.window.actionNewAfterTask.triggered.connect(lambda: self.do_create_ref('after'))
        self.window.actionEdit.triggered.connect(self.do_edit)
        self.window.actionToggleDone.triggered.connect(self.do_toggle_done)
        self.window.actionToggleTracking.triggered.connect(self.do_toggle_tracking)
        self.window.actionToggleHidden.triggered.connect(self.do_toggle_hidden)
        self.window.actionDelegate.triggered.connect(self.do_delegate)
        self.window.taskList.activated.connect(self.do_edit)

        if len(self.icon.availableSizes()) > 0:
            self.window.setWindowIcon(self.icon)

        if SETTING_GROUP_FILES in self.window.settings:
            group = self.window.settings[SETTING_GROUP_FILES]
            for item in group:
                filename = pathlib.Path(group[item]).expanduser().resolve()
                if filename.exists() and not any([s.filename == filename for s in self.sources]):
                    source = Source(TodoTxt(filename))
                    source.parse()
                    self.sources.append(source)

        for source in self.sources:
            self.window.watcher.addPath(str(source.filename))

        self.expect_change = []
        self.window.watcher.fileChanged.connect(self.source_changed)

        # self.window.taskModel.dataChanged.connect(lambda _0, _1, _2: self.update_completers())
        # self.window.taskModel.modelReset.connect(self.update_completers)
        # self.window.taskModel.rowsInserted.connect(self.update_completers)

        self.update_sources()

    def update_completers(self):
        pass
        # TODO: this is correct so far, but the completers only work on the first word
        #       as far as I have seen, the QLineEdit must be subclasses to allow autocompletion
        #       per typed word, if it starts with '+' or '@'
        # projects = set()
        # contexts = set()
        # for source in self.sources:
        #     projects |= source.projects
        #     contexts |= source.contexts
        # self.window.update_completers(sorted(projects) + sorted(contexts))

    def do_edit(self):
        task = self.window.taskList.get_selected_index()
        if task is None:
            return

        self.expect_change.append(task.data(TASK_ROLE).todotxt.filename)
        self.window.start_editor(task)
        self.update_completers()

    def do_create(self):
        self.window.start_creator(self.sources)
        self.update_completers()

    def do_create_ref(self, reftype='ref'):
        taskindex = self.window.taskList.get_selected_index()
        if taskindex is None:
            return

        taskindex = self.window.taskModel.ensure_up_to_date(taskindex)
        if taskindex is not None:
            task = taskindex.data(TASK_ROLE)
            if len(task.attr_id) == 0:
                task.parse(utils.auto_task_id(self.sources, str(task) + ' id:#'))
                task.todotxt.save(safe=self.safe_save)
                self.window.taskModel.setData(taskindex, task)

            refid = task.attr_id[0]
            self.do_create()
            ref = f"{reftype}:{refid}"
            self.window.creator.editor.setText(ref + " " + self.window.creator.editor.text())

    def do_toggle_done(self):
        taskindex = self.window.taskList.get_selected_index()
        if taskindex is None:
            return
        
        taskindex = self.window.taskModel.ensure_up_to_date(taskindex)
        if taskindex is not None:
            task = taskindex.data(TASK_ROLE)
            utils.toggle_done(task, self.clear_contexts)
            task.todotxt.save(safe=self.safe_save)
            self.window.taskModel.setData(taskindex, task)

    def do_toggle_tracking(self):
        taskindex = self.window.taskList.get_selected_index()
        if taskindex is None:
            return

        taskindex = self.window.taskModel.ensure_up_to_date(taskindex)
        if taskindex is not None:
            task = taskindex.data(TASK_ROLE)
            utils.toggle_tracking(task)
            task.todotxt.save(safe=self.safe_save)
            self.window.taskModel.setData(taskindex, task)

    def do_toggle_hidden(self):
        taskindex = self.window.taskList.get_selected_index()
        if taskindex is None:
            return

        taskindex = self.window.taskModel.ensure_up_to_date(taskindex)
        if taskindex is not None:
            task = taskindex.data(TASK_ROLE)
            utils.toggle_hidden(task)
            task.todotxt.save(safe=self.safe_save)
            self.window.taskModel.setData(taskindex, task)

    def do_open_source(self):
        filename, ok = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                             tr("Open Todo.txt File"),
                                                             str(pathlib.Path().home()),
                                                             tr("Todo.txt files (*.txt)"))
        if not ok:
            return

        filename = pathlib.Path(filename)
        if not filename.exists():
            return

        self.add_source(filename)

    def add_source(self, filename):
        if any([source.filename == filename for source in self.sources]):
            return

        source = Source(TodoTxt(filename))
        # TODO: catch bad parsing
        source.parse()

        self.window.watcher.addPath(str(filename))

        self.sources.append(source)
        if self.window.settings.accept_changes:
            self.window.settings.conf[SETTING_GROUP_FILES] = {}
            for nr, source in enumerate(self.sources):
                self.window.settings.update(SETTING_GROUP_FILES, str(nr+1), str(source.filename))
            self.window.settings.has_changes = True

        self.update_sources()

    def source_changed(self, name):
        if name in self.expect_change:
            self.expect_change.remove(name)
            return
        for source in self.sources:
            if str(source.filename) == name:
                source.parse()
        self.window.taskModel.reload()

    def do_delegate(self):
        if len(self.delegate_marker) == 0:
            return

        taskindex = self.window.taskList.get_selected_index()
        if taskindex is None:
            return

        task = taskindex.data(TASK_ROLE)
        if task.description is None or len(task.description) == 0:
            return

        add_delegate_marker = self.delegate_marker not in task.description.split(' ')
        add_to = len(self.delegate_to) > 0 and task.attributes.get(self.delegate_to, None) is None

        if not add_to:
            name = task.attributes[self.delegate_to][0]

        if add_delegate_marker or add_to:
            if add_to:
                name, ok = QtWidgets.QInputDialog.getText(self.window,
                                                          tr("Delegate task"),
                                                          tr("Delegate this task to:"),
                                                          QtWidgets.QLineEdit.Normal,
                                                          "")
                if not ok:
                    return
                add_to = len(name.strip()) > 0

            taskindex = self.window.taskModel.ensure_up_to_date(taskindex)
            if taskindex is None:
                # TODO: warn that this task has changed and was reloaded
                return
            task = taskindex.data(TASK_ROLE)
            if add_delegate_marker:
                task.description += ' ' + self.delegate_marker
            if add_to:
                task.description += ' ' + self.delegate_to + ':' + name.replace(' ', '_')
            task.todotxt.save(safe=self.safe_save)
            self.window.taskModel.setData(taskindex, task)

        utils.execute_delegate_action(task, self.delegate_to, self.delegate_marker, self.delegate_action)

    def update_sources(self):
        # TODO list sources in Program menu
        self.window.searcher.update_sources(self.sources)
        self.window.taskModel.sources = self.sources
        utils.update_displaynames(self.sources)
        self.window.taskModel.reload()

    def do_quit(self):
        self.window.close()


def run_qtui(args):
    tmpdir = pathlib.Path(QtCore.QDir.tempPath())
    tmpdir.mkdir(parents=True, exist_ok=True)
    username = getpass.getuser().replace(' ', '_')
    fn = f"{common.QTPROGRAMNAME}-{username}.pid"
    fullpath = tmpdir / fn

    sock = None
    if fullpath.exists():
        servername = fullpath.read_text()
        if servername != '-':
            sock = QtNetwork.QLocalSocket()
            sock.connectToServer(servername)
            if not sock.waitForConnected(300):
                sock.abort()
                sock = None
                fullpath.unlink()
            else:
                if sock.writeData(bytes("hoi\n", 'ascii')) == -1:
                    sock.abort()
                    sock = None
                else:
                    sock.flush()

    if args.add_task:
        if sock is None:
            print(tr("Could not connect to running program"))
        else:
            sock.writeData(bytes("new\n", 'ascii'))
            sock.flush()
            sock.abort()
            return

    if sock is not None:
        print(tr(f"{common.QTPROGRAMNAME} is already running. "\
                 f"If you know that not to be true, delete {fullpath}"))
        return
    fullpath.write_text("-")

    app = QApplication([])
    app.setApplicationName(common.QTPROGRAMNAME)
    app.setApplicationVersion(version.__version__)
    p = Program(configuration.get_config(args), utils.open_sources(args), fullpath)
    p.window.actionShowAboutQt.triggered.connect(app.aboutQt)
    p.window.activateWindow()

    if args.add_task:
        p.window.actionNew.trigger()

    return app.exec_()

