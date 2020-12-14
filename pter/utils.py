import datetime
import string
import re
import webbrowser
import pathlib
import urllib.parse
import subprocess
import sys
import os

from pytodotxt import Task, TodoTxt

from pter import common
from pter.searcher import get_relative_date
from pter.source import Source


DATETIME_FMT = '%Y-%m-%d-%H-%M-%S'
FORMAT_TOKEN_RE = re.compile('^([^a-z]*)([a-z][a-z-]*)(.*)$')


def duration_as_str(duration):
    seconds = int(duration.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    result = ''
    if hours > 0:
        result += f'{hours}h'
    if minutes > 0:
        result += f'{minutes}m'

    return result


def parse_duration(text):
    duration = datetime.timedelta(0)

    sign = 1
    if text.startswith('-'):
        sign = -1
        text = text[1:]
    elif text.startswith('+'):
        text = text[1:]

    value = ''
    for char in text.lower():
        if char in string.digits:
            value += char
        elif char == 'h' and len(value) > 0:
            duration += datetime.timedelta(hours=int(value))
            value = ''
        elif char == 'm' and len(value) > 0:
            duration += datetime.timedelta(minutes=int(value))
            value = ''
        elif char == 's' and len(value) > 0:
            duration += datetime.timedelta(seconds=int(value))
            value = ''
        elif char == 'd' and len(value) > 0:
            duration += datetime.timedelta(days=int(value))
            value = ''
        elif char == 'w' and len(value) > 0:
            duration += datetime.timedelta(days=int(value)*7)
            value = ''
        else:
            # parse error
            return None

    if len(value) > 0:
        duration += datetime.timedelta(minutes=int(value))
    
    duration *= sign

    return duration


def task_due_in_days(task):
    if len(task.attr_due) == 0:
        return None
    today = datetime.datetime.now().date()
    try:
        then = datetime.datetime.strptime(task.attr_due[0], Task.DATE_FMT).date()
        return (then - today).days
    except ValueError:
        return None


def dehumanize_dates(text, tags=None):
    """Replace occurrences of relative dates in tags"""
    if tags is None:
        tags = ['due', 't']

    offset = 0
    found_any = True

    while found_any and offset < len(text):
        found_any = False
        for match in Task.KEYVALUE_RE.finditer(text, offset):
            if match is None:
                offset = len(text)
                break
            found_any = True
            if match.group(2) in tags and not Task.DATE_RE.match(match.group(3)):
                then = get_relative_date(match.group(3))
                if then is not None:
                    then = then.strftime(Task.DATE_FMT)
                    text = text[:match.start(3)] + \
                           then + \
                           text[match.end(3):]
                    offset = match.start(3) + len(then)
                    break
            offset = match.end(3) + 1
    return text


def ensure_up_to_date(task):
    ok = True
    if task.todotxt.refresh():
        ok = False
        task.todotxt.parse()
        tasks = [other for other in source.tasks if other.raw.strip() == task.raw.strip()]
        if len(tasks) > 0:
            ok = True
            task = tasks[0]

    if ok:
        return task

    return None


def toggle_tracking(task):
    if 'tracking' in task.attributes:
        return update_spent(task)
    task.add_attribute('tracking', datetime.datetime.now().strftime(DATETIME_FMT))
    return True


def toggle_done(task, clear_contexts):
    task.is_completed = not task.is_completed
    if task.is_completed:
        task.completion_date = datetime.datetime.now().date()
        if task.priority is not None:
            task.add_attribute('pri', task.priority)
            task.priority = None
        if len(clear_contexts) > 0 and task.description is not None:
            for context in clear_contexts:
                while f'@{context}' in task.description:
                    task.remove_context(context)
    else:
        task.completion_date = None
        attrs = task.attributes
        if 'pri' in attrs:
            task.priority = attrs['pri'][0]
            task.remove_attribute('pri')
    task.parse(str(task))


def toggle_hidden(task):
    is_hidden = len(task.attr_h) > 0 and task.attr_h[0] == '1'
    if len(task.attr_h) > 0:
        is_hidden = task.attr_h[0] == '1'
        task.remove_attribute('h', '1')
        if not is_hidden:
            task.add_attribute('h', '1')
    else:
        task.add_attribute('h', '1')


def sign(n):
    if n < 0:
        return -1
    elif n > 0:
        return 1
    return 0


def sort_fnc(a):
    if isinstance(a, tuple):
        task, _ = a
    else:
        task = a
    daydiff = task_due_in_days(task)
    if daydiff is None:
        daydiff = sys.maxsize
    prio = task.priority
    if prio is None:
        prio = 'ZZZ'
    tracking = len(task.attr_tracking) > 0
    return [task.is_completed, daydiff, prio, task.linenr]


def update_spent(task):
    now = datetime.datetime.now()
    tracking = task.attr_tracking
    raw_spent = task.attr_spent

    if len(tracking) == 0:
        return False

    try:
        then = datetime.datetime.strptime(tracking[0], DATETIME_FMT)
    except ValueError:
        return False

    if len(raw_spent) > 0:
        spent = parse_duration(raw_spent[0])
        if spent is None:
            self.status_bar.addstr(0, 0, "Failed to parse 'spent' time", self.color(Window.ERROR))
            self.status_bar.noutrefresh()
            return False
    else:
        spent = datetime.timedelta(0)
    
    diff = now - then
    if diff <= datetime.timedelta(minutes=1):
        diff = datetime.timedelta(0)

    task.remove_attribute('tracking', tracking[0])

    # TODO: make the minimal duration configurable
    if diff >= datetime.timedelta(minutes=1):
        spent = duration_as_str(spent + diff)
        if len(raw_spent) == 0:
            task.add_attribute('spent', spent)
        else:
            task.replace_attribute('spent', raw_spent[0], spent)

        return True

    return False


def human_friendly_date(text):
    if isinstance(text, datetime.datetime):
        then = text.date
    elif isinstance(text, datetime.date):
        then = text
    elif isinstance(text, str):
        try:
            then = datetime.datetime.strptime(text, Task.DATE_FMT).date()
        except ValueError:
            return text
    today = datetime.date.today()
    diff = abs((then - today).days)
    then_wd = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
               'friday', 'saturday', 'sunday'][then.isoweekday()]

    if today == then:
        return 'today'
    if diff == 1:
        if then > today:
            return 'tomorrow'
        return 'yesterday'
    if diff == 2:
        if then > today:
            return 'in 2 days'
        return '2 days ago'
    if diff == 3:
        if then > today:
            return 'in 3 days'
    if diff < 8:
        if then > today:
            return 'next ' + then_wd
        return 'last ' + then_wd
    if diff < 34:
        diff_wk = diff//7
        plural = '' if diff_wk == 1 else 's'
        if then > today:
            return f'in {diff_wk} week{plural}'
        return f'{diff_wk} week{plural} ago'
    if diff < 180:
        diff_mnth = diff//30
        plural = '' if diff_mnth == 1 else 's'
        if then > today:
            return f'in {diff_mnth} month{plural}'
        return f'{diff_mnth} month{plural} ago'
    if diff < 350:
        if then > today:
            return 'in half a year'
        return 'half a year ago'
    return then.strftime(Task.DATE_FMT)


def parse_task_format(text):
    rawtokens = []
    token = ''
    in_block = False
    
    for char in text:
        if in_block:
            if char == '}':
                token += char
                rawtokens.append(token)
                token = ''
                in_block = False
                continue
        elif char == '{':
            if len(token) > 0:
                rawtokens.append(token)
            token = char
            in_block = True
            continue
        token += char

    if len(token) > 0:
        rawtokens.append(token)

    tokens = []
    for token in rawtokens:
        if len(token) > 2 and token.startswith('{') and token.endswith('}'):
            align = None
            token = token[1:-1]
            extra_left = None
            extra_right = None
            if ':' in token and len(token) > 3:
                token, align = token.split(':')

            match = FORMAT_TOKEN_RE.match(token)

            if match is None:
                continue

            if len(match.group(1)) > 0:
                extra_left = match.group(1)
            token = match.group(2)
            if len(match.group(3)) > 0:
                extra_right = match.group(3)

            tokens.append((token, align, extra_left, extra_right))
        else:
            tokens.append(token)

    return tokens


def unquote(text):
    if len(text) <= 1:
        return text
    if text[0] in '"\'' and text[0] == text[-1]:
        return text[1:-1]
    return text


def open_manual():
    docloc = common.HERE / "docs" / "pter.html"

    if docloc.exists():
        webbrowser.open('file://' + str(docloc))


def parse_searches():
    if not common.SEARCHES_FILE.exists():
        return {}

    searches = {}
    with open(common.SEARCHES_FILE, 'rt', encoding="utf-8") as fd:
        for linenr, line in enumerate(fd.readlines()):
            if '=' not in line:
                continue
            name, searchdef = line.split("=", 1)
            name = name.strip()
            searchdef = searchdef.strip()
            if len(name) == 0 or len(searchdef) == 0:
                continue
            searches[name.strip()] = searchdef.strip()

    return searches


def save_searches(searches):
    common.SEARCHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(common.SEARCHES_FILE, 'wt', encoding="utf-8") as fd:
        for name in sorted(searches.keys()):
            value = searches[name].strip()
            if len(value) == 0:
                continue
            fd.write(f"{name} = {value}\n")


def update_displaynames(sources):
    if len(sources) == 0:
        return

    pos = 2
    while True:
        displaynames = {source.displayname for source in sources}
        if len(displaynames) == len(sources):
            return
        for source in sources:
            source.displayname = os.sep.join(str(source.filename).split(os.sep)[-1*pos:])
        pos += 1


def execute_delegate_action(task, to_attr, marker, action):
    if action == common.DELEGATE_ACTION_NONE:
        return

    recipient = ''
    if len(to_attr) > 0 and to_attr in task.attributes:
        recipient = ','.join(task.attributes[to_attr])

    if action == common.DELEGATE_ACTION_MAIL:
        # filter out "to:" (to_attr) and the delegation marker
        text = ' '.join([word for word in str(task).split(' ')
                         if word != marker
                            and (len(to_attr) == 0
                                 or not word.startswith(to_attr + ':'))])
        uri = 'mailto:' + urllib.parse.quote(recipient) + '?Subject=' + urllib.parse.quote(text)
        webbrowser.open(uri)


def new_task_id(sources, prefix=""):
    """Generate a new unique task ID
    The task ID will be unique for the given sources, and with the given prefix.
    """
    existing_ids = set()
    for source in sources:
        existing_ids |= {int(key[len(prefix):]) for key in source.task_ids
                         if key.startswith(prefix) and key[len(prefix):].isnumeric()}

    if len(existing_ids) > 0:
        highest = max(existing_ids)
    else:
        highest = 0

    return prefix + str(highest+1)


def query_latest_version():
    installed_re = re.compile(r'^[\s]+IN_STALLED:[\s]+([^\s]+)(.*)$')
    latest_re = re.compile(r'^[\s]+LATEST:[\s]+([^\s]+)$')
    output = subprocess.run([sys.executable, "-m", "pip", "search", common.PROGRAMNAME], capture_output=True)
    for line in str(output.stdout, 'utf-8').split("\n"):
        match = installed_re.match(line)
        if match is not None:
            if len(match.groups()) > 1:
                return match.group(1)
        match = latest_re.match(line)
        if match is not None:
            return match.group(1)

    return ''


def open_sources(args):
    sources = [Source(TodoTxt(pathlib.Path(fn).expanduser().resolve())) for fn in args.filename]
    for source in sources:
        if source.filename.exists():
            source.parse()
    return sources


def create_from_search(searcher):
    text = []
    for group, prefix in [('contexts', '@'), ('projects', '+'), ('words', '')]:
        text += [prefix+word for word in getattr(searcher, group, set())]
    return ' '.join(text)


def auto_task_id(sources, text):
    words = []
    for word in text.split(' '):
        if word.startswith('id:'):
            _, base = word.split(':', 1)
            if '#' in base:
                base, keyword = base.split('#', 1)
                if keyword == '' or keyword == 'auto':
                    word = 'id:{}'.format(new_task_id(sources, base))
        words.append(word)
    return ' '.join(words)

