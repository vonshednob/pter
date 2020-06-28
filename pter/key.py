import curses


class Key:
    SPECIAL = {'<backspace>': '⌫',  # ⌫
               '<del>': '⌦',
               '<ins>': '⎀',
               '<left>': '→',
               '<right>': '←',
               '<up>': '↑',
               '<down>': '↓',
               '<home>': 'Home',
               '<end>': 'End',
               '<escape>': '⎋',
               '<return>': '⏎',  # ↵ ↲
               '<pgup>': 'PgUp',  # ⇞
               '<pgdn>': 'PgDn',  # ⇟
               '<space>': '␣',
               '<tab>': '⇥',
               '<f1>': 'F1',
               '<f2>': 'F2',
               '<f3>': 'F3',
               '<f4>': 'F4',
               '<f5>': 'F5',
               '<f6>': 'F6',
               '<f7>': 'F7',
               '<f8>': 'F8',
               '<f9>': 'F9',
               '<f10>': 'F10',
               '<f11>': 'F11',
               '<f12>': 'F12',
               }
    BACKSPACE = '<backspace>'
    DELETE = '<del>'
    LEFT = '<left>'
    RIGHT = '<right>'
    UP = '<up>'
    DOWN = '<down>'
    PGUP = '<pgup>'
    PGDN = '<pgdn>'
    HOME = '<home>'
    END = '<end>'
    RETURN = '<return>'
    ESCAPE = '<escape>'
    SPACE = '<space>'
    TAB = '<tab>'
    F1 = '<f1>'
    F2 = '<f2>'
    F3 = '<f3>'
    F4 = '<f4>'
    F5 = '<f5>'
    F6 = '<f6>'
    F7 = '<f7>'
    F8 = '<f8>'
    F9 = '<f9>'
    F10 = '<f10>'
    F11 = '<f11>'
    F12 = '<f12>'
    RESIZE = '<resize>'

    def __init__(self, value, special=False):
        self.value = value
        self.special = special

    @classmethod
    def read(cls, stdscr):
        try:
            value = stdscr.get_wch()
            return Key.parse(value)
        except (KeyboardInterrupt, curses.error):
            return Key('C', special=True)
        except EOFError:
            return Key('D', special=True)

    @classmethod
    def parse(cls, value):
        if value == curses.KEY_BACKSPACE:
            return Key(Key.BACKSPACE, True)
        elif value == curses.KEY_DC:
            return Key(Key.DELETE, True)
        elif value == curses.KEY_LEFT:
            return Key(Key.LEFT, True)
        elif value == curses.KEY_RIGHT:
            return Key(Key.RIGHT, True)
        elif value == curses.KEY_UP:
            return Key(Key.UP, True)
        elif value == curses.KEY_DOWN:
            return Key(Key.DOWN, True)
        elif value == curses.KEY_END:
            return Key(Key.END, True)
        elif value == curses.KEY_HOME:
            return Key(Key.HOME, True)
        elif value == curses.KEY_NPAGE:
            return Key(Key.PGDN, True)
        elif value == curses.KEY_PPAGE:
            return Key(Key.PGUP, True)
        elif value == curses.KEY_F1:
            return Key(Key.F1, True)
        elif value == curses.KEY_F2:
            return Key(Key.F2, True)
        elif value == curses.KEY_F3:
            return Key(Key.F3, True)
        elif value == curses.KEY_F4:
            return Key(Key.F4, True)
        elif value == curses.KEY_F5:
            return Key(Key.F5, True)
        elif value == curses.KEY_F6:
            return Key(Key.F6, True)
        elif value == curses.KEY_F7:
            return Key(Key.F7, True)
        elif value == curses.KEY_F8:
            return Key(Key.F8, True)
        elif value == curses.KEY_F9:
            return Key(Key.F9, True)
        elif value == curses.KEY_F10:
            return Key(Key.F10, True)
        elif value == curses.KEY_F11:
            return Key(Key.F11, True)
        elif value == curses.KEY_F12:
            return Key(Key.F12, True)
        elif value == curses.KEY_RESIZE:
            return Key(Key.RESIZE, True)
        elif isinstance(value, int):
            # no idea what key that is
            return Key('', True)
        elif isinstance(value, str):
            try:
                ctrlkey = str(curses.unctrl(value), 'ascii')
            except OverflowError:
                # some unicode, you probably want to see it
                return Key(value, False)

            if value in "\n\r":
                return Key(Key.RETURN, special=True)

            if ctrlkey in ['^H', '^?']:
                return Key(Key.BACKSPACE, special=True)

            if ctrlkey == '^[':
                return Key(Key.ESCAPE, True)

            if ctrlkey != value:
                return Key(ctrlkey[1:], True)
            else:
                return Key(value)

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        if isinstance(other, Key):
            return self.value == other.value and self.special == other.special
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, bytes):
            return str(self) == str(other, 'ascii')
        raise ValueError("'other' has unexpected type {type(other)}")

    def __str__(self):
        if self.special:
            if self.value.startswith('<'):
                return self.value
            return  '^' + self.value
        return self.value

