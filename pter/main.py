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
from pter import version
from pter import utils
from pter.tr import tr


def parse_args(is_qtui):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        type=str,
                        default=common.CONFIGFILE,
                        help=tr("Location of your configuration file. Defaults to %(default)s."))
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'%(prog)s {version.__version__}')
    parser.add_argument('-u', '--check-for-updates',
                        default=False,
                        action='store_true',
                        help=tr("Check online whether a new version of pter is available."))
    parser.add_argument('-n', '--new-task',
                        type=str,
                        default=None,
                        help=tr("Add this as a new task to the selected file."))
    if is_qtui:
        parser.add_argument('-a', '--add-task',
                            default=False,
                            action='store_true',
                            help=tr("Directly start to create a new task"))

    parser.add_argument('filename',
                        type=str,
                        nargs='*',
                        help=tr('todo.txt file(s) to open'))

    return parser.parse_args()


def run():
    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()
    is_qtui = pathlib.Path(sys.argv[0]).name == common.QTPROGRAMNAME

    args = parse_args(is_qtui)

    if args.check_for_updates:
        latest_version = utils.query_latest_version()
        if version.__version__ < latest_version:
            print(tr("A newer version, {latest_version}, is available on pypi.org.")
                    .format(latest_version=latest_version))
        else:
            print(tr("{programname} is up to date.").format(programname=common.PROGRAMNAME))
        return 0

    if args.new_task is not None:
        if len(args.filename) != 1:
            print(tr("You have to provide exactly one todo.txt file."), file=sys.stderr)
            return 1

        text = args.new_task
        if text == '-':
            text = sys.stdin.read()

        if len(text) == 0:
            return -1
        
        with open(args.filename[0], "r+t", encoding="utf-8") as fd:
            fd.read()
            for line in text.split("\n"):
                if len(line.strip()) == 0:
                    continue
                fd.write(utils.dehumanize_dates(line) + "\n")
        return 0

    if is_qtui:
        success = -1
        if run_qtui is None:
            print(tr("PyQt5 is not installed or could otherwise not be imported: {}").format(qterr),
                  file=sys.stderr)
        else:
            success = 0
            run_qtui(args)

    elif run_cursesui is not None:
        success = run_cursesui(args)

    else:
        print(tr("Neither PyQt5 nor curses are installed."), file=sys.stderr)
        success = -2

    return success

