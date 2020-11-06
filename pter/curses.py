import argparse
import locale
import pathlib
import os
import sys
import datetime
import configparser
import string
import webbrowser
import curses
import curses.panel

from pytodotxt import TodoTxt, Task, version

from pter import common
from pter import utils
from pter import configuration
from pter.searcher import Searcher, get_relative_date
from pter.key import Key
from pter.source import Source
from pter.tr import tr


class Color:
    def __init__(self, fg, bg=None):
        self.fg = fg
        self.bg = bg

    def pair(self):
        return [self.fg, self.bg]

    def __eq__(self, other):
        return self.fg == other.fg and self.bg == other.bg


class TaskLineGroup:
    def __init__(self):
        self.elements = []

    def append(self, *args, **kwargs):
        self.elements.append(TaskLineElement(*args, **kwargs))


class TaskLine:
    def __init__(self, task, source):
        self.elements = {}
        self.task = task
        self.source = source
        self._due = None

    def add(self, kind, *args, **kwargs):
        self.elements[kind] = TaskLineElement(*args, **kwargs)
        self.elements[kind].name = kind

    @property
    def due(self):
        due = self.task.attr_due
        if self._due is None and len(due) > 0:
            try:
                self._due = datetime.datetime.strptime(due[0], Task.DATE_FMT).date()
            except ValueError:
                self._due = None
        return self._due

    @property
    def is_overdue(self):
        return self.due is not None and self.due < datetime.date.today() and not self.task.is_completed

    @property
    def is_due_tomorrow(self):
        return self.due is not None and self.due == datetime.date.today() + datetime.timedelta(days=1)

    @property
    def is_due_today(self):
        return self.due is not None and self.due == datetime.date.today()


class TaskLineDescription(TaskLineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = common.TF_DESCRIPTION

    @property
    def space_around(self):
        return True


class TaskLineElement:
    def __init__(self, content, color=None, space_around=False, name=None):
        self.content = content
        self.color = color
        self.space_around = space_around
        self.name = name


class TaskLineSelectionIcon(TaskLineElement):
    def __init__(self, content):
        super().__init__(content, space_around=False)
        self.name = common.TF_SELECTION


class Window:
    def __init__(self, sources, conf):
        self.scr = curses.initscr()
        self.quit = False
        self.sources = sources
        self.conf = conf

        self.safe_save = conf.bool(common.SETTING_GROUP_GENERAL,
                                   common.SETTING_SAFE_SAVE, 'y')

        self.key_mapping = {'q': 'quit',
                            '^C': 'cancel',
                            '<escape>': 'cancel',
                            '<down>': 'next-item',
                            '<up>': 'prev-item',
                            'j': 'next-item',
                            'k': 'prev-item',
                            '<return>': 'select-item',
                            '<pgup>': 'half-page-up',
                            '<pgdn>': 'half-page-down',
                            '<home>': 'first-item',
                            '<end>': 'last-item',
                            'h': 'toggle-hidden',
                            'd': 'toggle-done',
                            'e': 'edit-task',
                            'n': 'create-task',
                            ':': 'jump-to',
                            '/': 'search',
                            'c': 'search-context',
                            'p': 'search-project',
                            't': 'toggle-tracking',
                            '^L': 'refresh-screen',
                            '^R': 'reload-tasks',
                            'u': 'open-url',
                            '>': 'delegate',
                            'l': 'load-search',
                            's': 'save-search',
                            '?': 'show-help',
                            'm': 'open-manual',}
        self.editor_key_mapping = {'^C': 'cancel',
                                   '<escape>': 'cancel',
                                   '<left>': 'go-left',
                                   '<right>': 'go-right',
                                   '^U': 'del-to-bol',
                                   '<backspace>': 'del-left',
                                   '<del>': 'del-right',
                                   '<home>': 'go-bol',
                                   '<end>': 'go-eol',
                                   '<f6>': 'select-file',
                                   '<return>': 'submit-input',
                                   }
        self.scroll_margin = conf.number(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_SCROLL_MARGIN)
        self.show_numbers = conf.bool(common.SETTING_GROUP_GENERAL,
                                      common.SETTING_SHOW_NUMBERS)
        self.use_colors = conf.bool(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_USE_COLORS)
        self.human_friendly_dates = conf.list(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HUMAN_DATES)
        self.task_format = utils.parse_task_format(conf.get(common.SETTING_GROUP_GENERAL,
                                                            common.SETTING_TASK_FORMAT,
                                                            common.DEFAULT_TASK_FORMAT))
        self.clear_contexts = [context for context in conf.list(common.SETTING_GROUP_GENERAL,
                                                                common.SETTING_CLEAR_CONTEXT)
                               if len(context) > 0]
        self.add_creation_date = conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_ADD_CREATED)
        self.create_from_search = conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_CREATE_FROM_SEARCH)
        self.auto_id = conf.bool(common.SETTING_GROUP_GENERAL, common.SETTING_AUTO_ID)
        self.protos = conf.list(common.SETTING_GROUP_GENERAL,
                                common.SETTING_PROTOCOLS)

        self.selection_indicator = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                          common.SETTING_ICON_SELECTION))
        self.done_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_NOT_DONE)),
                            utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_DONE)))
        self.overflow_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_LEFT)),
                                utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_RIGHT)))
        self.due_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_OVERDUE)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TODAY)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TOMORROW)))
        self.tracking_marker = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                      common.SETTING_ICON_TRACKING))

        # mapable functions
        self.functions = {'quit': self.do_quit,
                          'nop': lambda: True,
                          'next-item': self.do_next_task,
                          'prev-item': self.do_prev_task,
                          'half-page-up': self.do_half_page_up,
                          'half-page-down': self.do_half_page_down,
                          'refresh-screen': self.do_refresh_screen,
                          'reload-tasks': self.do_reload_tasks,
                          'search': self.do_start_search,
                          'search-context': self.do_search_context,
                          'search-project': self.do_search_project,
                          'load-search': self.do_load_search,
                          'save-search': self.do_save_search,
                          'first-item': self.do_go_first_task,
                          'last-item': self.do_go_last_task,
                          'edit-task': self.do_edit_task,
                          'create-task': self.do_create_task,
                          'jump-to': self.do_jump_to,
                          'open-url': self.do_open_url,
                          'toggle-tracking': self.do_toggle_tracking,
                          'toggle-done': self.do_toggle_done,
                          'toggle-hidden': self.do_toggle_hidden,
                          'show-help': self.do_show_help,
                          'delegate': self.do_delegate,
                          'open-manual': utils.open_manual,}
        self.short_name = {'quit': 'Quit',
                           'cancel': 'Cancel',
                           'select-item': 'Select',
                           'next-item': 'Next item',
                           'prev-item': 'Previous item',
                           'half-page-up': 'Half page up',
                           'half-page-down': 'Half page down',
                           'search': 'Search',
                           'open-url': 'Open URL',
                           'load-search': 'Load search',
                           'save-search': 'Save search',
                           'search-context': 'Search for context of this task',
                           'search-project': 'Search for project of this task',
                           'first-item': 'First item',
                           'last-item': 'Last item',
                           'edit-task': 'Edit task',
                           'create-task': 'New task',
                           'jump-to': 'Jump to item',
                           'toggle-hidden': 'Set/unset hidden',
                           'toggle-done': 'Set/unset done',
                           'toggle-tracking': 'Start/stop tracking',
                           'show-help': 'Help',
                           'open-manual': 'Read the manual',
                           'go-left': 'Go one character to the left',
                           'go-right': 'Go one character to the right',
                           'go-bol': 'Go to start of line',
                           'go-eol': 'Go to end of line',
                           'del-left': 'Delete to the left',
                           'del-right': 'Delete to the right',
                           'del-to-bol': 'Delete to start of line',
                           'submit-input': 'Apply changes',
                           'select-file': 'Select file',
                           'delegate': 'Delegate task',
                           }

        curses.start_color()
        self.colors = {}
        self.color_cache = {}
        if curses.has_colors() and self.use_colors:
            curses.use_default_colors()
            self.update_color_pairs()
        elif len(self.selection_indicator) == 0:
            self.selection_indicator = '>'
        curses.noecho()
        curses.cbreak()
        self.scr.keypad(True)
        try:
            curses.curs_set(0)
        except:
            pass

        self.tasks = []
        self.filtered_tasks = []
        self.task_lines = []
        self.max_widths = {}
        self.selected_task = -1
        self.scroll_offset = 0
        self.task_list = None
        self.task_panel = None
        self.search_bar = None
        self.status_bar = None
        self.help_bar = None
        self.search = Searcher('',
                               self.conf.bool(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_SEARCH_CASE_SENSITIVE),
                               self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_DEFAULT_THRESHOLD),
                               self.conf.bool(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HIDE_SEQUENTIAL))
        self.search.update_sources(self.sources)
        self.delegation_marker = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_MARKER)
        self.delegation_action = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_ACTION).lower()
        self.delegate_to = self.conf.get(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_DELEG_TO).lower()
        if self.delegation_action not in common.DELEGATE_ACTIONS:
            self.delegation_action = common.DELEGATE_ACTION_NONE

        for item in self.conf[common.SETTING_GROUP_KEYS]:
            fnc = self.conf.get(common.SETTING_GROUP_KEYS, item, None)
            if fnc is None or fnc not in self.functions:
                continue

            if len(item) == 1:
                self.key_mapping[item] = fnc
            elif len(item) == 2 and item[0] == '^':
                self.key_mapping[item.upper()] = fnc
            elif item in Key.SPECIAL:
                self.key_mapping[item] = fnc
            else:
                raise RuntimeError(f'Invalid key: {item}')
        to_exit = [k for k, fnc in self.key_mapping.items() if fnc == 'quit']
        if len(to_exit) == 0:
            raise RuntimeError("No key to exit")

        for item in self.conf[common.SETTING_GROUP_EDITORKEYS]:
            fnc = self.conf.get(common.SETTING_GROUP_EDITORKEYS, item, None)
            
            if len(item) == 1:
                self.editor_key_mapping[item] = fnc
            elif len(item) == 2 and item[0] == '^':
                self.editor_key_mapping[item.upper()] = fnc
            elif item in Key.SPECIAL:
                self.editor_key_mapping[item] = fnc
            else:
                raise RuntimError(f"Invalid key: {item}")
        to_exit = [k for k, fnc in self.editor_key_mapping.items() if fnc == 'cancel']
        if len(to_exit) == 0:
            raise RuntimeError("No key to cancel editing")

    def update_color_pairs(self):
        self.colors = {common.SETTING_COL_NORMAL: [Color(7, 0), Color(0, 7)],
                       common.SETTING_COL_INACTIVE: [Color(8), None],
                       common.SETTING_COL_ERROR: [Color(1), None],
                       common.SETTING_COL_PRI_A: [Color(1), None],
                       common.SETTING_COL_PRI_B: [Color(3), None],
                       common.SETTING_COL_PRI_C: [Color(6), None],
                       common.SETTING_COL_CONTEXT: [Color(4), None],
                       common.SETTING_COL_PROJECT: [Color(2), None],
                       common.SETTING_COL_HELP_TEXT: [Color(11, 8), None],
                       common.SETTING_COL_HELP_KEY: [Color(2, 8), None],
                       common.SETTING_COL_OVERFLOW: [Color(11), None],
                       common.SETTING_COL_OVERDUE: [Color(7, 1), Color(1, 7)],
                       common.SETTING_COL_DUE_TODAY: [Color(4), None],
                       common.SETTING_COL_DUE_TOMORROW: [Color(6), None],
                       common.SETTING_COL_TRACKING: [Color(7, 2), Color(2, 7)],
                       }
        if curses.has_colors() and self.use_colors:
            for colorname in self.conf[common.SETTING_GROUP_COLORS]:
                colpair = self.conf.color_pair(common.SETTING_GROUP_COLORS, colorname)

                if colpair is None:
                    continue
                fg, bg = colpair
                pairidx = 0

                if colorname.startswith('sel-'):
                    colorname = colorname[4:]
                    pairidx = 1

                if colorname not in self.colors:
                    # TODO: log the error in the configuration
                    continue

                self.colors[colorname][pairidx] = Color(fg, bg)

            # register the color pairs
            for colorname in self.colors.keys():
                self.color(colorname, 0)
                self.color(colorname, 1)

            for number, key in enumerate(self.conf[common.SETTING_GROUP_HIGHLIGHT]):
                hlcol = Color(*self.conf.color_pair(common.SETTING_GROUP_HIGHLIGHT, key))

                variant = 0
                if key.startswith('sel-'):
                    variant = 1
                    key = key[4:]

                if len(key.strip()) == 0:
                    continue

                if 'hl:' + key not in self.colors:
                    self.colors['hl:' + key] = [None, None]

                self.colors['hl:' + key][variant] = hlcol

                # and initialize the color
                self.color('hl:' + key, variant)

    def color(self, colorname, variant=0, default=None):
        """Return a color pair number for use with curses attributes
        variant can be 0/False (for normal) or 1/True (for selected text)
        If the color pair does not exist yet, it is registered, if possible."""

        if colorname is None:
            colorname = default or common.SETTING_COL_NORMAL

        if not self.use_colors or colorname not in self.colors:
            return 0

        if variant is True:
            variant = 1
        if variant is False:
            variant = 0
        if default is None:
            default = common.SETTING_COL_NORMAL

        colors = self.colors[colorname]
        if variant >= len(colors):
            raise ValueError(variant)

        color = colors[variant]
        if color is None:
            if variant > 0 and colors[0] is not None:
                color = colors[0].pair()
            else:
                color = self.colors[default][variant].pair()
        else:
            color = color.pair()

        default_variant = self.colors[default][variant]
        if default_variant is None and variant > 0:
            default_variant = self.colors[default][0]
        if default_variant is None:
            default_variant = self.colors[common.SETTING_COL_NORMAL][variant]

        if color[0] is None:
            color[0] = default_variant.fg
        if color[1] is None:
            color[1] = default_variant.bg
            if color[1] is None and self.colors[default][0] is not None:
                color[1] = self.colors[default][0].bg
            if color[1] is None:
                color[1] = self.colors[common.SETTING_COL_NORMAL][variant].bg

        color = (color[0], color[1])

        if color in self.color_cache:
            return curses.color_pair(self.color_cache[color])

        next_id = len(self.color_cache) + 1
        if next_id >= curses.COLOR_PAIRS:
            # sucks, we ran out of numbers
            return 0

        try:
            curses.init_pair(next_id, *color)
            self.color_cache[color] = next_id
        except curses.error:
            self.color_cache[color] = 0
            return 0
        return next_id


    def build_screen(self):
        self.scr.attrset(self.color(common.SETTING_COL_NORMAL))
        self.scr.noutrefresh()
        dim = self.scr.getmaxyx()
        if self.task_list is None:
            self.task_list = curses.newwin(dim[0]-4, dim[1], 2, 0)
            self.task_panel = curses.panel.new_panel(self.task_list)
        self.task_list.bkgd(' ', self.color(common.SETTING_COL_NORMAL))
        if self.search_bar is None:
            self.search_bar = curses.newwin(1, dim[1], 0, 0)
        self.search_bar.bkgd(' ', self.color(common.SETTING_COL_NORMAL))
        self.search_bar.addstr(0, 1, tr('(no search active)'), self.color(common.SETTING_COL_INACTIVE))
        self.search_bar.noutrefresh()
        if self.status_bar is None:
            self.status_bar = curses.newwin(1, dim[1], dim[0]-2, 0)
        self.status_bar.bkgd(' ', self.color(common.SETTING_COL_NORMAL))
        self.status_bar.noutrefresh()
        self.print_shortcut_bar()
        self.scr.addnstr(1, 0, '─'*dim[1], dim[1])

    def print_shortcut_bar(self, actions=None, mapping=None):
        if mapping is None:
            mapping = self.key_mapping
        if actions is None:
            actions = ['show-help', 'quit', 'edit-task',
                       'create-task', 'search', 'load-search', 'save-search',
                       'toggle-done', 'jump-to', 'next-item', 'prev-item']

        if self.help_bar is not None:
            del self.help_bar
        self.help_bar = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
        self.help_bar.bkgd(' ', self.color(common.SETTING_COL_NORMAL))
        self.help_bar.clear()
        x = 1
        for action in actions:
            label = self.short_name.get(action, None)
            if label is None:
                continue
            label = tr(label) + " "

            keys = [k for k, v in mapping.items() if v == action]
            if len(keys) == 0:
                continue

            if keys[0] in Key.SPECIAL:
                keytext = f" {tr(Key.SPECIAL[keys[0]])} "
            else:
                keytext = f" {tr(keys[0])} "
            if x + len(keytext) + len(label) >= self.help_bar.getmaxyx()[1]:
                break

            self.help_bar.addstr(0, x, keytext, self.color(common.SETTING_COL_HELP_KEY))
            x += len(keytext)
            self.help_bar.addstr(0, x, label, self.color(common.SETTING_COL_HELP_TEXT))
            x += len(label) + 1
        self.help_bar.noutrefresh()

    def update_tasks(self):
        self.tasks = []
        for source in self.sources:
            self.tasks += [(task, source) for task in source.tasks]
        self.tasks.sort(key=utils.sort_fnc)

        self.apply_search()

    def apply_search(self):
        self.filtered_tasks = [(task, source) for task, source in self.tasks
                               if self.search.match(task)]
        self.rebuild_task_lines()

    def rebuild_task_lines(self):
        self.task_lines = []
        self.max_widths = {}
        today = datetime.date.today()

        def update_max_width(name, textlen):
            if name not in self.max_widths:
                self.max_widths[name] = 0
            if isinstance(textlen, str):
                textlen = len(textlen)
            for tf in self.task_format:
                if not isinstance(tf, tuple):
                    continue
                tname, _, left, right = tf
                if tname == name:
                    textlen += 0 if left is None else len(left)
                    textlen += 0 if right is None else len(right)
            self.max_widths[name] = max(textlen, self.max_widths[name])

        update_max_width(common.TF_DONE, max(len(self.done_marker[0]), len(self.done_marker[1])))
        update_max_width(common.TF_SELECTION, self.selection_indicator)
        update_max_width(common.TF_TRACKING, self.tracking_marker)
        update_max_width(common.TF_DUE, max([len(m) for m in self.due_marker]))

        for nr, pair in enumerate(self.filtered_tasks):
            task, source = pair
            line = TaskLine(task, task.todotxt)

            # Selection indicator
            if len(self.selection_indicator) > 0:
                line.elements[common.TF_SELECTION] = TaskLineSelectionIcon(self.selection_indicator)

            # Item number
            text = str(nr+1)
            line.add(common.TF_NUMBER, text)
            update_max_width(common.TF_NUMBER, text)

            # Done marker
            line.add(common.TF_DONE, self.done_marker[1] if task.is_completed else self.done_marker[0])

            # Age
            if task.creation_date is not None:
                text = str((datetime.date.today() - task.creation_date).days)
                line.add(common.TF_AGE, text)
                update_max_width(common.TF_AGE, text)

            # Creation date
            if task.creation_date is not None:
                text = self.date_as_str(task.creation_date, common.TF_CREATED)
                line.add(common.TF_CREATED, text)
                update_max_width(common.TF_CREATED, text)

            # Completion date
            if task.completion_date is not None:
                text = self.date_as_str(task.completion_date, common.TF_COMPLETED)
                line.add(common.TF_COMPLETED, text)
                update_max_width(common.TF_COMPLETED, text)

            # Tracking
            if task.attributes.get(common.ATTR_TRACKING, None) is not None:
                line.add(common.TF_TRACKING, self.tracking_marker)

            # Due marker
            if line.due is not None:
                duedays = str((line.due - today).days)
                line.add(common.TF_DUEDAYS, duedays)
                update_max_width(common.TF_DUEDAYS, duedays)

                if not task.is_completed:
                    if line.due < today:
                        line.add(common.TF_DUE, self.due_marker[0], common.SETTING_COL_OVERDUE)
                    elif line.due == today:
                        line.add(common.TF_DUE, self.due_marker[1], common.SETTING_COL_DUE_TODAY)
                    elif line.due == today + datetime.timedelta(days=1):
                        line.add(common.TF_DUE, self.due_marker[2], common.SETTING_COL_DUE_TOMORROW)

            # Priority marker
            if task.priority is not None:
                pri = task.priority.upper()
                attrs = None
                if pri == 'A':
                    attrs = common.SETTING_COL_PRI_A
                elif pri == 'B':
                    attrs = common.SETTING_COL_PRI_B
                elif pri == 'C':
                    attrs = common.SETTING_COL_PRI_C
                line.add(common.TF_PRIORITY, f"{pri}", attrs)
                update_max_width(common.TF_PRIORITY, '(A)')

            # Description
            description = TaskLineDescription()
            if task.description is not None:
                for word in task.description.split(' '):
                    if len(word) == 0:
                        continue

                    attr = None

                    if word.startswith('@') and len(word) > 1:
                        attr = common.SETTING_COL_CONTEXT
                    elif word.startswith('+') and len(word) > 1:
                        attr = common.SETTING_COL_PROJECT
                    elif ':' in word:
                        key, value = word.split(':', 1)
                        if 'hl:' + key in self.colors:
                            attr = 'hl:' + key
                        if key in [common.ATTR_T, common.ATTR_DUE]:
                            word = key + ':' + self.date_as_str(value, key)
                        if key == common.ATTR_PRI:
                            attr = None
                            value = value.upper()
                            if value == 'A':
                                attr = common.SETTING_COL_PRI_A
                            elif value == 'B':
                                attr = common.SETTING_COL_PRI_B
                            elif value == 'C':
                                attr = common.SETTING_COL_PRI_C
                    description.append(word, attr, space_around=True)
            line.elements[common.TF_DESCRIPTION] = description
            update_max_width(common.TF_DESCRIPTION, ' '.join([e.content for e in description.elements]))

            self.task_lines.append(line)

    def show_tasks(self):
        list_height = self.task_list.getmaxyx()[0]
        if len(self.filtered_tasks) > 0:
            self.selected_task = max(0, min(self.selected_task, len(self.filtered_tasks)-1))

        if self.selected_task <= self.scroll_offset + self.scroll_margin:
            self.scroll_offset = max(0, self.selected_task - self.scroll_margin)
        elif self.selected_task >= self.scroll_offset + list_height - self.scroll_margin:
            self.scroll_offset = min(max(0, len(self.filtered_tasks) - list_height),
                                     self.selected_task - list_height + self.scroll_margin + 1)

        for nr, line in enumerate(self.task_lines):
            if nr < self.scroll_offset:
                continue
            if nr >= self.scroll_offset + list_height:
                break
            self.write_task(nr-self.scroll_offset, 1, nr, line)
        self.task_list.clrtobot()
        if len(self.filtered_tasks) == 0:
            self.task_list.erase()
        self.task_list.noutrefresh()

    def date_as_str(self, text, hint=''):
        if common.TF_ALL in self.human_friendly_dates or hint in self.human_friendly_dates:
            return utils.human_friendly_date(text)
        if not isinstance(text, str):
            return text.strftime(Task.DATE_FMT)
        return text

    def write_task(self, y, x, nr, taskline):
        line = ''
        is_selected = nr == self.selected_task
        is_tracked = len(taskline.task.attr_tracking) > 0

        baseattrs = common.SETTING_COL_NORMAL
        if taskline.is_overdue:
            baseattrs = common.SETTING_COL_OVERDUE
        elif taskline.is_due_tomorrow:
            baseattrs = common.SETTING_COL_DUE_TOMORROW
        elif taskline.is_due_today:
            baseattrs = common.SETTING_COL_DUE_TODAY
        if is_tracked:
            baseattrs = common.SETTING_COL_TRACKING

        maxwidth = self.task_list.getmaxyx()[1]-1

        def print_element(y, x, maxwidth, element, align, extra):
            cut_off = False
            if isinstance(element, TaskLineSelectionIcon) and not is_selected:
                elem = ''
            elif isinstance(element, TaskLineGroup):
                return print_group(y, x, maxwidth, element, align, extra)
            elif isinstance(element, str):
                element = TaskLineElement(element)
                elem = element.content
            else:
                elem = element.content

            if align is not None:
                width = self.max_widths.get(element.name, 0)
                if extra is not None and extra[0] is not None:
                    width -= len(extra[0])
                if extra is not None and extra[1] is not None:
                    width -= len(extra[1])
                width = max(0, width)
                elem = f"{elem:{align}{width}}"
            elif len(elem) == 0:
                return ''

            if extra_left is not None:
                elem = extra_left + elem

            if extra_right is not None:
                elem = elem + extra_right

            elemlen = len(elem)
            if elemlen >= maxwidth:
                cut_off = True
                elem = elem[:maxwidth]

            self.task_list.addstr(y, x, elem, self.color(element.color, is_selected, baseattrs))

            if cut_off:
                attrs = common.SETTING_COL_OVERFLOW
                self.task_list.addstr(y, x+maxwidth-len(self.overflow_marker[1]),
                                      self.overflow_marker[1],
                                      self.color(attrs, is_selected, baseattrs))
            return elem

        def print_group(y, x, maxwidth, group, align, extra):
            line = ''

            if extra is not None and extra[0] is not None:
                self.task_list.addstr(y, x + len(line), extra[0], self.color(baseattrs, is_selected))
                line = extra[0]

            if align is not None and align.endswith('>'):
                spacing = align[0] * min(maxwidth - len(line), self.max_widths[group.name] - len(' '.join([e.content for e in group.elements])))
                self.task_list.addstr(y, x + len(line), spacing, self.color(baseattrs, is_selected))
                line += spacing

            cut_off = False
            for elnr, element in enumerate(group.elements):
                word = ''

                if elnr > 0 and (element.space_around or group.elements[elnr-1].space_around):
                    if len(line) + 1 >= maxwidth:
                        cut_off = True
                    else:
                        self.task_list.addstr(y, x + len(line), " ", self.color(baseattrs, is_selected))
                        line += " "

                cut_off = cut_off or len(line) >= maxwidth

                if not cut_off:
                    if isinstance(element, TaskLineGroup):
                        word = print_group(y, x + len(line), maxwidth-len(line), element, None, None)
                    else:
                        word = print_element(y, x + len(line), maxwidth-len(line), element, None, None)
                    line += word

                if cut_off or len(line) >= maxwidth:
                    break

            if not cut_off and align is not None and align.endswith('<'):
                if len(line) < self.max_widths[group.name]:
                    spacing = align[0] * min(maxwidth-len(line), self.max_widths[group.name]-len(line))
                    self.task_list.addstr(y, x + len(line), spacing, self.color(baseattrs, is_selected))
                    line += spacing

            if not cut_off and extra is not None and extra[1] is not None and len(line) + 1 < maxwidth:
                self.task_list.addstr(y, x + len(line), extra[1], self.color(baseattrs, is_selected))
            return line

        self.task_list.move(y, x)
        self.task_list.clrtoeol()
        for token in self.task_format:
            align = None
            extra = None
            if isinstance(token, tuple):
                token, align, extra_left, extra_right = token
                extra = (extra_left, extra_right)
                token = taskline.elements.get(token, TaskLineElement('', name=token))
            elif isinstance(token, str):
                token = TaskLineElement(token)
            else:
                raise TypeError()

            x += len(print_element(y, x, maxwidth-x, token, align, extra))

            if x >= maxwidth:
                break

    def run(self):
        self.build_screen()
        self.update_tasks()

        while not self.quit:
            source_changed = False
            for source in self.sources:
                if source.refresh():
                    source.parse()
                    source_changed = True
            if source_changed:
                self.update_tasks()

            self.show_tasks()
            curses.panel.update_panels()
            curses.doupdate()

            key = Key.read(self.scr)
            self.status_bar.clear()
            self.status_bar.noutrefresh()

            if key == Key.RESIZE:
                self.do_refresh_screen()
            elif not key.special and str(key) in '123456789':
                self.do_jump_to(str(key))
            elif str(key) in self.key_mapping and self.key_mapping[str(key)] in self.functions:
                self.functions[self.key_mapping[str(key)]]()

        self.scr.clear()

    def read_jump_to(self, start):
        self.status_bar.clear()
        self.status_bar.addstr(0, 0, tr('Jump to:') + ' ')
        self.status_bar.refresh()
        number = self.read_text(curses.LINES-2, 9, text=start)
        self.status_bar.erase()
        self.status_bar.noutrefresh()

        if number is not None and number.isdigit():
            number = int(number)
            return number
        return None

    def read_search_input(self):
        backup_search = self.search.text
        new_search = self.search.text
        curpos = len(new_search)

        def update(text):
            self.search.text = text
            self.search.parse()
            self.apply_search()
            self.show_tasks()

        new_search = self.read_text(0, 0, text=self.search.text, callback=update)

        if new_search is None:
            new_search = backup_search

        if new_search.strip() != self.search.text:
            self.search.text = new_search.strip()
            self.search.parse()
        self.apply_search()
        self.show_tasks()
        self.refresh_search_bar()

    def refresh_search_bar(self):
        self.search_bar.erase()
        if len(self.search.text.strip()) == 0:
            self.search_bar.addstr(0, 1, tr('(no search active)'), self.color(common.SETTING_COL_INACTIVE))
        else:
            self.search_bar.addstr(0, 1, self.search.text)
        self.search_bar.refresh()

    def read_text(self, y, x, cols=None, text='', callback=None, select_source=None):
        if cols is None:
            cols = curses.COLS-x-1
        editor = curses.newwin(1, cols, y, x)
        editor.bkgdset(' ', self.color(common.SETTING_COL_NORMAL))
        scroll = 0
        margin = 5
        max_width = cols-1
        curpos = len(text)
        source = self.sources[0]

        show_select_source = select_source is not None and len(self.sources) > 1

        shortcuts = ['cancel', 'submit-input']
        if show_select_source:
            shortcuts.append('select-file')
        self.print_shortcut_bar(shortcuts, self.editor_key_mapping)

        def refresh_source_display():
            if not show_select_source:
                return
            right = cols - 3 - len(source.displayname)
            select_source.addstr(2, 1, "─"*(cols-2))
            select_source.addstr(2, right, f"┤{source.displayname}├")
            select_source.refresh()

        refresh_source_display()

        try:
            curses.curs_set(True)
        except:
            pass

        while True:
            unchanged = text
            editor.erase()
            if curpos >= scroll + max_width - 2 - margin:
                scroll = min(curpos-margin, curpos - max_width + margin + 2)
            elif curpos <= scroll + margin:
                scroll = max(0, curpos - margin)
            if scroll > 0:
                editor.addstr(0, 0, self.overflow_marker[0], self.color(common.SETTING_COL_OVERFLOW))
            if len(text)-scroll >= max_width-1:
                editor.addstr(0, max_width-len(self.overflow_marker[1]),
                              self.overflow_marker[1], self.color(common.SETTING_COL_OVERFLOW))
            editor.addstr(0, 1, text[scroll:scroll+max_width-2])
            editor.move(0, 1 + curpos-scroll)
            editor.refresh()

            key = Key.read(self.scr)

            if str(key) in self.editor_key_mapping:
                fnc = self.editor_key_mapping[str(key)]

                if fnc == 'cancel':
                    text = None
                    break
                elif fnc == 'del-left':
                    text = text[:curpos-1] + text[curpos:]
                    curpos = max(0, curpos-1)
                elif fnc == 'del-right':
                    text = text[:curpos] + text[curpos+1:]
                elif fnc == 'del-to-bol':
                    text = text[curpos:]
                    curpos = 0
                elif fnc == 'go-left':
                    curpos = max(0, curpos-1)
                elif fnc == 'go-right':
                    curpos = min(curpos+1, len(text))
                elif fnc == 'go-bol':
                    curpos = 0
                elif fnc == 'go-eol':
                    curpos = len(text)
                elif show_select_source and fnc == 'select-file':
                    curses.curs_set(0)
                    sourcename = self.select_one([s.displayname for s in self.sources], tr("Select source"))
                    curses.curs_set(1)
                    if sourcename is not None:
                        candidates = [s for s in self.sources if s.displayname == sourcename]
                        if len(candidates) == 1:
                            source = candidates[0]
                    refresh_source_display()
                elif fnc == 'submit-input':
                    break
            elif not key.special:
                text = text[:curpos] + str(key) + text[curpos:]
                curpos += len(key)

            if unchanged != text and callback is not None:
                callback(text)

        try:
            curses.curs_set(False)
        except:
            pass
        del editor
        curses.panel.update_panels()

        self.print_shortcut_bar()

        if select_source:
            return text, source
        return text

    def select_one(self, items, title=None, lblfnc=None, autoselect=True):
        if len(items) == 0:
            return None
        if len(items) == 1 and autoselect:
            return items[0]

        if lblfnc is None:
            lblfnc = lambda x: x

        self.print_shortcut_bar(['cancel', 'select-item', 'next-item', 'prev-item', 'jump-to'])

        options = items[:]
        options.sort(key=lblfnc)
        
        y = curses.LINES//2 - 1
        w_offset = 3 + len(self.selection_indicator) + \
                   len(str(len(options)))+1 if self.show_numbers else 0
        w = min(curses.COLS-6, w_offset + max([len(lblfnc(o)) for o in options]))
        h = min(curses.LINES-6, len(options))
        frame = curses.newwin(h+2, w+2,
                              curses.LINES//2 - h//2 - 1,
                              curses.COLS//2 - w//2 - 1)
        frame.bkgdset(' ', self.color(common.SETTING_COL_NORMAL))
        panel = curses.panel.new_panel(frame)

        scroll = 0
        margin = 2
        selection = 0

        while True:
            if selection < scroll + margin:
                scroll = max(0, selection - margin)
            elif selection >= scroll + h - margin:
                scroll = min(max(0, len(options) - h), selection - h + margin + 1)
            frame.erase()
            frame.border()
            if title is not None and w > len(title) + 6:
                frame.addstr(0, 2, f'┤{title}├')

            for nr, option in enumerate(options):
                if nr < scroll:
                    continue
                if nr-scroll >= h:
                    continue
                x = 1
                y = 1 + nr - scroll
                line = ''

                attrs = self.color(common.SETTING_COL_NORMAL, nr == selection)

                if len(self.selection_indicator) > 0:
                    if selection == nr:
                        indicator = f' {self.selection_indicator}'
                    else:
                        indicator = ' '*(len(self.selection_indicator)+1)
                    frame.addstr(y, x, indicator, attrs)
                    line += indicator
                    x += len(indicator)

                if self.show_numbers:
                    nrwidth = len(str(len(options)))+1
                    nrlbl = f' {nr+1:> {nrwidth}} '
                    frame.addstr(y, x, nrlbl, attrs)
                    line += nrlbl
                    x += len(nrlbl)

                frame.addstr(y, x, option[:max(0, w-len(line))], attrs)
            frame.refresh()

            key = Key.read(self.scr)

            if str(key) in self.key_mapping:
                fnc = self.key_mapping[str(key)]

                if fnc == 'next-item':
                    selection = min(selection + 1, len(options)-1)
                elif fnc == 'prev-item':
                    selection = max(selection - 1, 0)
                elif fnc == 'jump-to':
                    pos = self.read_jump_to('')
                    if pos is not None:
                        selection = min(max(0, pos-1), len(options)-1)
                elif fnc == 'select-item':
                    break
                elif fnc in ['quit', 'cancel']:
                    selection = None
                    break
            elif str(key) in '123456789':
                pos = self.read_jump_to(str(key))
                if pos is not None:
                    selection = min(max(0, pos-1), len(options)-1)

        panel.hide()
        curses.panel.update_panels()
        del panel
        del frame
        self.print_shortcut_bar()
        curses.doupdate()

        if selection is None:
            return None
        return options[selection]


    def do_quit(self):
        self.quit = True

    def do_next_task(self, skip=1):
        self.selected_task = min(self.selected_task + skip, len(self.filtered_tasks)-1)

    def do_prev_task(self, skip=1):
        self.selected_task = max(self.selected_task - skip, 0)

    def do_half_page_up(self):
        self.do_prev_task(skip=(self.task_list.getmaxyx()[0] // 2)-1)

    def do_half_page_down(self):
        self.do_next_task(skip=(self.task_list.getmaxyx()[0] // 2)-1)

    def do_go_last_task(self):
        self.do_next_task(skip=len(self.filtered_tasks))

    def do_go_first_task(self):
        self.do_prev_task(skip=len(self.filtered_tasks))

    def do_jump_to(self, init=''):
        pos = self.read_jump_to(init)
        if pos is not None:
            self.selected_task = min(max(0, pos-1), len(self.filtered_tasks))

    def do_start_search(self):
        self.read_search_input()

    def do_search_context(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        task, source = self.filtered_tasks[self.selected_task]
        contexts = [context for context in task.contexts if context not in self.search.contexts]

        if len(contexts) == 0:
            return

        contexts.sort()
        context = self.select_one(contexts, tr("Select Context"))

        if context is not None:
            context = '@' + context
            if len(self.search.text) > 0:
                context = " " + context
            self.search.text += context
            self.search.parse()
            self.apply_search()
            self.show_tasks()
            self.refresh_search_bar()

    def do_search_project(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        task, source = self.filtered_tasks[self.selected_task]
        projects = [project for project in task.projects if project not in self.search.projects]

        if len(projects) == 0:
            return

        projects.sort()
        project = self.select_one(projects, tr("Select Project"))

        if project is not None:
            project = '+' + project
            if len(self.search.text) > 0:
                project = " " + project
            self.search.text += project
            self.search.parse()
            self.apply_search()
            self.show_tasks()
            self.refresh_search_bar()

    def do_toggle_done(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        task, source = self.filtered_tasks[self.selected_task]
        task = utils.ensure_up_to_date(task)
        if task is not None:
            utils.toggle_done(task, self.clear_contexts)
            source.save(safe=self.safe_save)
        else:
            self.status_bar.addstr(0, 0,
                                   tr("Not changed: task was modified in the background"),
                                   self.color(common.SETTING_COL_ERROR))
            self.status_bar.noutrefresh()
        self.update_tasks()

    def do_toggle_hidden(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        task, source = self.filtered_tasks[self.selected_task]
        task = utils.ensure_up_to_date(task)
        if task is not None:
            utils.toggle_hidden(task)
            source.save(safe=self.safe_save)
        else:
            self.status_bar.addstr(0, 0,
                                   tr("Not changed: task was modified in the background"),
                                   self.color(common.SETTING_COL_ERROR))
            self.status_bar.noutrefresh()
        self.update_tasks()

    def do_create_task(self):
        source = self.sources[0]
        y = curses.LINES//2 - 1
        frame = curses.newwin(3, curses.COLS-6, y, 3)
        frame.bkgdset(' ', self.color(common.SETTING_COL_NORMAL))
        frame.erase()
        frame.border()
        panel = curses.panel.new_panel(frame)
        label = tr('New Task')
        if curses.COLS-8 > len(label):
            frame.addstr(0, 2, f'┤{label}├')
        frame.refresh()
        today = ''
        if self.add_creation_date:
            today = datetime.datetime.now().strftime(Task.DATE_FMT) + ' '
        if self.create_from_search:
            today += utils.create_from_search(self.search)
        text, source = self.read_text(y+1, 4, curses.COLS-8, today, select_source=frame)
        if text is not None:
            if self.auto_id and not any([word.startswith('id:') for word in text.split(' ')]):
                text += ' id:#'
            text = utils.auto_task_id(self.sources, text)
            text = utils.dehumanize_dates(text)
        frame.erase()
        del panel
        del frame
        if text is not None and len(text.strip()) > 0:
            task = Task(text)
            if source.refresh():
                source.parse()
            source.tasks.append(task)
            source.save(safe=self.safe_save)
            source.parse()
            source.update_contexts_and_projects()
            self.search.update_sources(self.sources)
            self.update_tasks()
        self.show_tasks()

    def do_edit_task(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        y = curses.LINES//2 - 1
        frame = curses.newwin(3, curses.COLS-6, y, 3)
        frame.bkgdset(' ', self.color(common.SETTING_COL_NORMAL))
        frame.erase()
        frame.border()
        label = tr('Edit Task')
        if curses.COLS-8 > len(label):
            frame.addstr(0, 2, f'┤{label}├')
        frame.refresh()
        task, source = self.filtered_tasks[self.selected_task]
        if source.refresh():
            source.parse()
            self.update_tasks()
            raw = str(task).strip()
            these = [other for other in source.tasks if str(other).strip() == raw]
            if len(these) > 0:
                task = these[0]
            else:
                frame.erase()
                self.status_bar.addstr(0, 0,
                                       tr("Cannot edit: task was modified in the background"),
                                       self.color(common.SETTING_COL_ERROR))
                self.status_bar.noutrefresh()
                return
        text = self.read_text(y+1, 4, curses.COLS-8, str(task).strip())
        if text is not None:
            text = utils.auto_task_id(self.sources, text)
            text = utils.dehumanize_dates(text)
        frame.erase()
        del frame
        if text is not None and text.strip() != str(task).strip():
            task = utils.ensure_up_to_date(task)
            if task is not None:
                task.parse(text)
                source.save(safe=self.safe_save)
                source.update_contexts_and_projects()
                self.search.update_sources(self.sources)
            else:
                self.status_bar.addstr(0, 0,
                                       tr("Not changed: task was modified in the background"),
                                       self.color(common.SETTING_COL_ERROR))
                self.status_bar.noutrefresh()
            self.update_tasks()

    def do_load_search(self):
        searches = utils.parse_searches()
        if len(searches) == 0:
            return
        names = [name for name in sorted(searches.keys())]
        name = self.select_one(names, tr('Load Search'), autoselect=False)
        if names is not None and name in searches:
            self.search.text = searches[name]
            self.refresh_search_bar()
            self.search.parse()
            self.apply_search()

    def do_save_search(self):
        y = curses.LINES//2 - 1
        frame = curses.newwin(3, curses.COLS-6, y, 3)
        frame.bkgdset(' ', self.color(common.SETTING_COL_NORMAL))
        frame.erase()
        frame.border()
        label = tr('Save Search')
        if curses.COLS-8 > len(label):
            frame.addstr(0, 2, f'┤{label}├')
        frame.refresh()

        text = self.read_text(y+1, 4, curses.COLS-8, '')

        if text is not None and len(text.strip()) > 0:
            searches = utils.parse_searches()
            searches[text] = self.search.text
            utils.save_searches(searches)

        frame.erase()
        del frame

    def do_reload_tasks(self):
        for source in self.sources:
            source.parse()
            source.update_contexts_and_projects()
        self.search.update_sources(self.sources)
        self.update_tasks()

    def do_toggle_tracking(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return
        task, source = self.filtered_tasks[self.selected_task]
        task = utils.ensure_up_to_date(task)
        if task is None:
            self.status_bar.addstr(0, 0,
                                   tr("Not tracked: task was modified in the background"),
                                   self.color(common.SETTING_COL_ERROR))
            self.status_bar.noutrefresh()
            self.update_tasks()
            return
        
        if utils.toggle_tracking(task):
            source.save(safe=self.safe_save)

        self.update_tasks()

    def do_refresh_screen(self):
        curses.update_lines_cols()
        self.build_screen()
        self.refresh_search_bar()

    def do_open_url(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return

        task, _ = self.filtered_tasks[self.selected_task]
        urls = []

        if task.description is None:
            return

        for match in common.URL_RE.finditer(task.description):
            if match.group(1) not in self.protos:
                continue
            urls.append(match.group(0))

        copy = urls[:]
        urls = []
        for url in copy:
            if url.startswith('<') and url.endswith('>'):
                url = url[1:-1]
            if len(url) == 0:
                continue
            urls.append(url)

        url = self.select_one(urls, tr("Select URL"))
        if url is not None:
            webbrowser.open(url)

    def do_delegate(self):
        if len(self.filtered_tasks) == 0 or self.selected_task >= len(self.filtered_tasks):
            return

        task, source = self.filtered_tasks[self.selected_task]

        if len(self.delegation_marker) == 0:
            # no delegation marker
            return

        if task.description is None:
            task.description = ''

        if self.delegation_marker in task.description.split(' '):
            # already delegated
            self.do_delegation_action(task)
            return
        
        task = utils.ensure_up_to_date(task)
        if task is not None:
            task.description += ' ' + self.delegation_marker.strip()
            source.save(safe=self.safe_save)
            self.do_delegation_action(task)
        else:
            self.status_bar.addstr(0, 0,
                                   tr("Not delegated: task was modified in the background"),
                                   self.color(common.SETTING_COL_ERROR))
            self.status_bar.noutrefresh()
        self.update_tasks()

    def do_delegation_action(self, task):
        utils.execute_delegate_action(task, self.delegate_to, self.delegation_marker, self.delegation_action)

    def do_show_help(self):
        def collect_name_fnc(fncs, mapping):
            for name, fnc in sorted([(v, k) for k, v in self.short_name.items() if k in fncs]):
                for key in [k for k, v in mapping.items() if v == fnc]:
                    yield name, key

        nav_fncs = ['next-item', 'prev-item', 'half-page-up', 'half-page-down',
                    'first-item', 'last-item', 'jump-to']
        edt_fncs = ['toggle-hidden', 'toggle-done', 'edit-task', 'create-task',
                    'toggle-tracking', 'delegate']
        search_fncs = ['search', 'load-search', 'save-search', 'search-context', 'search-project']
        meta_fncs = ['show-help', 'open-manual', 'quit', 'cancel', 'refresh-screen',
                     'reload-tasks']
        other_fncs = ['open-url']

        lines = [(tr('TASK LIST'), ''), ('', ''), (tr('Program'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(meta_fncs, self.key_mapping)]
        lines += [('', ''), (tr('Navigation'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(nav_fncs, self.key_mapping)]
        lines += [('', ''), (tr('Search'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(search_fncs, self.key_mapping)]
        lines += [('', ''), (tr('Change Tasks'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(edt_fncs, self.key_mapping)]
        lines += [('', ''), (tr('Other'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(other_fncs, self.key_mapping)]

        edt_nav_fncs = ['go-left', 'go-right', 'go-bol', 'go-eol']
        edt_edt_fncs = ['del-left', 'del-right', 'del-to-bol']
        edt_meta_fncs = ['cancel', 'submit-input']
        lines += [('', ''), ('', ''), (tr('TASK EDITING'), ''), ('', ''), (tr('General'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(edt_meta_fncs, self.editor_key_mapping)]
        lines += [('', ''), (tr('Navigation'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(edt_nav_fncs, self.editor_key_mapping)]
        lines += [('', ''), (tr('Deletion'), '')]
        lines += [(name, key) for name, key in collect_name_fnc(edt_edt_fncs, self.editor_key_mapping)]

        maxnamelen = max([len(n) for n, _ in lines])
        scroll = 0
        doupdate = 2

        while True:
            if doupdate > 0:
                if doupdate > 1:
                    curses.update_lines_cols()
                    frame = curses.newwin(curses.LINES-1, curses.COLS, 0, 0)
                    frame.clear()
                    frame.bkgd(' ', self.color(common.SETTING_COL_NORMAL))
                    self.print_shortcut_bar(['quit',])
                else:
                    frame.clear()
                maxscroll = max(0, len(lines) - frame.getmaxyx()[0] + 3)
                scroll = min(scroll, maxscroll)
                for idx, line in enumerate(lines):
                    if idx < scroll:
                        continue
                    if idx >= scroll + frame.getmaxyx()[0] - 2:
                        continue
                    attrs = common.SETTING_COL_NORMAL
                    if line[1] == '':
                        attrs = common.SETTING_COL_CONTEXT
                    frame.addstr(idx+1-scroll, 1, line[0] + " "*(maxnamelen-len(line[0])+3) + line[1], self.color(attrs))
                    frame.clrtoeol()
                frame.clrtobot()
                frame.border()
                frame.noutrefresh()
                curses.doupdate()
                doupdate = 0

            key = Key.read(self.scr)

            if key == Key.RESIZE:
                doupdate = 2
                continue

            if str(key) in self.key_mapping:
                fnc = self.key_mapping[str(key)]

                if fnc in ['quit', 'cancel']:
                    break
                elif fnc == 'refresh-screen':
                    doupdate = 2
                elif fnc == 'next-item':
                    scroll = min(scroll + 1, maxscroll)
                    doupdate = 1
                elif fnc == 'prev-item':
                    scroll = max(0, scroll - 1)
                    doupdate = 1
                elif fnc == 'first-item':
                    scroll = 0
                    doupdate = 1
                elif fnc == 'last-item':
                    scroll = maxscroll
                    doupdate = 1
                elif fnc == 'half-page-up':
                    scroll = max(0, scroll - frame.getmaxyx()[0]//2)
                    doupdate = 1
                elif fnc == 'half-page-down':
                    scroll = min(maxscroll, scroll + frame.getmaxyx()[0]//2)
                    doupdate = 1

        del frame
        self.do_refresh_screen()


def run_cursesui(args):
    success = 0
    sources = utils.open_sources(args)
    
    if len(sources) == 0:
        success = -1
        print(tr("To start pter you must provide at least one todo.txt file. See --help for more information."),
              file=sys.stderr)
    else:
        search = Searcher('', False)
        search.update_sources(sources)

        window = Window(sources, configuration.get_config(args))
        exception = None

        try:
            window.run()
        except Exception as exc:
            exception = exc
        
        curses.endwin()

        if exception is not None:
            raise exception
            success = -3

    return success

