import datetime
import string
import re

from pter.searcher import get_relative_date
from pytodotxt import Task


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


def ensure_up_to_date(source, task):
    ok = True
    if source.refresh():
        ok = False
        source.parse()
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


def update_spent(task):
    attrs = task.attributes
    now = datetime.datetime.now()
    tracking = attrs.get('tracking', None)
    raw_spent = attrs.get('spent', None)

    if tracking is None:
        return False

    try:
        then = datetime.datetime.strptime(tracking[0], DATETIME_FMT)
    except ValueError:
        return False

    if raw_spent is not None:
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
        if raw_spent is None:
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

