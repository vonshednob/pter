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


def run():
    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    is_qtui = pathlib.Path(sys.argv[0]).name == common.QTPROGRAMNAME

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
    if is_qtui:
        parser.add_argument('-a', '--add-task',
                            default=False,
                            action='store_true',
                            help=tr("Directly start to create a new task"))

    parser.add_argument('filename',
                        type=str,
                        nargs='*',
                        help=tr('todo.txt file(s) to open'))
    args = parser.parse_args(sys.argv[1:])

    if args.check_for_updates:
        latest_version = utils.query_latest_version()
        if version.__version__ < latest_version:
            print(tr("A newer version, {latest_version}, is available on pypi.org.")
                    .format(latest_version=latest_version))
        else:
            print(tr("{programname} is up to date.").format(programname=common.PROGRAMNAME))
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

