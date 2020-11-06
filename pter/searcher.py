import datetime
import string

from pytodotxt import Task


class Searcher:
    def __init__(self, text=None, casesensitive=True, default_threshold=None, hide_sequential=True):
        self.words = set()
        self.not_words = set()
        self.projects = set()
        self.not_projects = set()
        self.contexts = set()
        self.not_contexts = set()
        self.ids = set()
        self.not_ids = set()
        self.after = set()
        self.refs = set()
        self.done = None
        self.show_hidden = False
        self.priority = None
        self.default_threshold = default_threshold
        self.hide_sequential = hide_sequential
        if default_threshold is None or len(default_threshold) == 0:
            self.default_threshold = 'today'
        self.threshold = self.default_threshold
        self.due = None
        self.created = None
        self.completed = None
        self.casesensitive = casesensitive
        self.sources = None
        self.task_by_id = None

        self.text = text

        if text is not None:
            self.parse()

    def reset(self):
        self.words = set()
        self.not_words = set()
        self.projects = set()
        self.not_projects = set()
        self.contexts = set()
        self.not_contexts = set()
        self.ids = set()
        self.not_ids = set()
        self.after = set()
        self.refs = set()
        self.done = None
        self.show_hidden = False
        self.priority = None
        self.threshold = get_relative_date(self.default_threshold, Task.DATE_FMT) or self.default_threshold
        self.due = None
        self.created = None
        self.completed = None

    def update_sources(self, sources):
        self.sources = sources
        self.task_by_id = {}
        self.parents = {}
        with_sequence = set()
        for source in self.sources:
            for task in source.tasks:
                if len(task.attr_id) == 0:
                    continue
                if len(task.attr_after) > 0:
                    with_sequence.add(task)
                for taskid in task.attr_id:
                    if taskid not in self.task_by_id:
                        self.task_by_id[taskid] = set()
                    self.task_by_id[taskid].add(task)

        # for each task obtain a set of their direct and indirect parents
        for task in with_sequence:
            parents = self._parse_ids('after', task)
            queue = parents.copy()
            while len(queue) > 0:
                otherid = queue.pop()
                if otherid in self.parents:
                    parents |= self.parents[otherid]
                    break
                parents.add(otherid)

                if otherid not in self.task_by_id:
                    continue
                for other in self.task_by_id[otherid]:
                    queue |= self._parse_ids('after', other).difference(parents)
            if len(parents) > 0:
                for taskid in task.attr_id:
                    if taskid not in self.parents:
                        self.parents[taskid] = set()
                    self.parents[taskid] |= parents

    def _parse_ids(self, keyword, task):
        these = set()
        for value in task.attributes.get(keyword, []):
            these |= {that for that in value.split(',')}
        if self.casesensitive:
            return {that.lower() for that in these}
        else:
            return these

    def parse(self):
        self.reset()
        text = self.text
        if not self.casesensitive:
            text = text.lower()

        for part in text.split(' '):
            do_not = False

            if part.startswith('not:'):
                do_not = True
                part = part[4:]
            elif part.startswith('-'):
                do_not = True
                part = part[1:]

            if len(part) == 0:
                continue

            if part.startswith('@') and len(part) > 1:
                if do_not:
                    self.not_contexts.add(part[1:])
                else:
                    self.contexts.add(part[1:])
            
            elif part.startswith('+') and len(part) > 1:
                if do_not:
                    self.not_projects.add(part[1:])
                else:
                    self.projects.add(part[1:])
            
            elif part.startswith('done:'):
                _, value = part.split(':', 1)
                if len(value) == 0:
                    self.done = None
                else:
                    self.done = value.lower().startswith('y')
            
            elif part.startswith('hidden:') or part.startswith('h:'):
                _, value = part.split(':', 1)
                self.show_hidden = value.lower().startswith('y') or value == '1'
            
            elif part.startswith('pri:'):
                _, value = part.split(':', 1)
                self.priority = (value, value)
            
            elif part.startswith('moreimportant:') or part.startswith('mi:'):
                _, value = part.split(':', 1)
                if self.priority is None:
                    self.priority = ['ZZZZ', ' ']
                self.priority[0] = value.upper()
            
            elif part.startswith('lessimportant:') or part.startswith('li:'):
                _, value = part.split(':', 1)
                if self.priority is None:
                    self.priority = ['ZZZZ', ' ']
                self.priority[1] = value.upper()
            
            elif part.startswith('due:'):
                _, value = part.split(':', 1)
                if value.lower().startswith('y'):
                    self.due = ['0000-00-00', '9999-99-99']
                else:
                    self.due = [value, value]
            
            elif part.startswith('duebefore:') or part.startswith('db:'):
                _, value = part.split(':', 1)
                if self.due is None:
                    self.due = ['0000-00-00', '9999-99-99']
                self.due[1] = value
            
            elif part.startswith('dueafter:') or part.startswith('da:'):
                _, value = part.split(':', 1)
                if self.due is None:
                    self.due = ['0000-00-00', '9999-99-99']
                self.due[0] = value

            elif part.startswith('created:'):
                _, value = part.split(':', 1)
                self.created = [value, value]

            elif part.startswith('createdbefore:') or part.startswith('crb:'):
                _, value = part.split(':', 1)
                if self.created is None:
                    self.created = ['0000-00-00', '9999-99-99']
                self.created[1] = value

            elif part.startswith('createdafter:') or part.startswith('cra:'):
                _, value = part.split(':', 1)
                if self.created is None:
                    self.created = ['0000-00-00', '9999-99-99']
                self.created[0] = value

            elif part.startswith('completed:'):
                _, value = part.split(':', 1)
                self.completed = [value, value]

            elif part.startswith('completedbefore:') or part.startswith('cob:'):
                _, value = part.split(':', 1)
                if self.completed is None:
                    self.completed = ['0000-00-00', '9999-99-99']
                self.completed[1] = value

            elif part.startswith('completedafter:') or part.startswith('coa:'):
                _, value = part.split(':', 1)
                if self.completed is None:
                    self.completed = ['0000-00-00', '9999-99-99']
                self.completed[0] = value

            elif part.startswith('t:') or part.startswith('tickler:') or part.startswith('threshold:'):
                _, value = part.split(':', 1)
                if len(value) == 0:
                    self.threshold = None
                else:
                    self.threshold = get_relative_date(value, Task.DATE_FMT) or value

            elif part.startswith('id:'):
                _, value = part.split(':', 1)
                if len(value) > 0:
                    value = {that for that in value.split(',')}

                    if do_not:
                        self.not_ids |= value
                    else:
                        self.ids |= value
                else:
                    if do_not:
                        self.not_words.add('id:')
                    else:
                        self.words.add('id:')

            elif part.startswith('after:') and self.after is not None:
                _, value = part.split(':', 1)
                if len(value) == 0:
                    self.after = None
                else:
                    values = set(value.split(','))
                    if do_not:
                        pass
                    else:
                        self.after |= values

            elif part.startswith('ref:') and self.refs is not None:
                _, value = part.split(':', 1)
                if len(value) > 0:
                    values = set(value.split(','))
                    if do_not:
                        pass
                    else:
                        self.refs |= values
            
            else:
                if do_not:
                    self.not_words.add(part)
                else:
                    self.words.add(part)

    def match(self, task):
        attrs = dict([(k if self.casesensitive else k.lower(), v)
                      for k, v in task.attributes.items()])
        return all([self.match_words(task),
                    self.match_contexts(task),
                    self.match_projects(task),
                    self.match_done(task),
                    self.match_hidden(attrs),
                    self.match_priority(task),
                    self.match_ids(task),
                    self.match_refs(task),
                    self.match_after(task, attrs),
                    self.match_due(attrs),
                    self.match_created(task),
                    self.match_completed(task),
                    self.match_threshold(attrs)])

    def match_words(self, task):
        if len(self.words) == 0 and len(self.not_words) == 0:
            return True

        description = task.description
        if not self.casesensitive:
            description = description.lower()

        return all([word in description for word in self.words]) \
                and not any([word in description for word in self.not_words])

    def match_contexts(self, task):
        if len(self.contexts) == 0 and len(self.not_contexts) == 0:
            return True

        contexts = task.contexts
        if not self.casesensitive:
            contexts = [context.lower() for context in contexts]

        return all([context in contexts for context in self.contexts]) \
                and not any([context in contexts for context in self.not_contexts])

    def match_projects(self, task):
        if len(self.projects) == 0 and len(self.not_projects) == 0:
            return True

        projects = task.projects
        if not self.casesensitive:
            projects = [project.lower() for project in projects]

        return all([project in projects for project in self.projects]) \
                and not any([project in projects for project in self.not_projects])

    def match_hidden(self, attrs):
        return 'h' not in attrs or (attrs['h'][0] == '1') == self.show_hidden

    def match_done(self, task):
        return self.done is None or task.is_completed == self.done

    def match_priority(self, task):
        if self.priority is None:
            return True

        pri = 'ZZZ'
        if task.priority is not None:
            pri = task.priority
        if not self.casesensitive:
            pri = pri.lower()

        return (self.priority[0] == self.priority[1] and pri == self.priority[0]) or \
               self.priority[0] > pri > self.priority[1]

    def match_threshold(self, attrs):
        if self.threshold is None:
            return True
        return 't' not in attrs or attrs['t'][0] <= self.threshold

    def match_due(self, attrs):
        if self.due is None:
            return True

        if 'due' not in attrs:
            return False

        due = [get_relative_date(self.due[0], Task.DATE_FMT) or self.due[0],
               get_relative_date(self.due[1], Task.DATE_FMT) or self.due[1]]

        if due[0] == due[1]:
            return attrs['due'][0] == due[0]

        return due[0] < attrs['due'][0] < due[1]

    def match_created(self, task):
        if self.created is None:
            return True

        if task.creation_date is None:
            return False

        created = [get_relative_date(self.created[0], Task.DATE_FMT) or self.created[0],
                   get_relative_date(self.created[1], Task.DATE_FMT) or self.created[1]]
        task_created = task.creation_date.strftime(Task.DATE_FMT)

        if created[0] == created[1]:
            return created[0] == task_created

        return created[0] < task_created < created[1]

    def match_completed(self, task):
        if self.completed is None:
            return True

        if task.completion_date is None:
            return False

        completed = [get_relative_date(self.completed[0], Task.DATE_FMT) or self.completed[0],
                     get_relative_date(self.completed[1], Task.DATE_FMT) or self.completed[1]]
        task_completed = task.completion_date.strftime(Task.DATE_FMT)

        if completed[0] == completed[1]:
            return completed[0] == task_completed

        return completed[0] < task_completed < completed[1]

    def match_ids(self, task):
        if len(self.not_ids) == 0 and len(self.ids) == 0:
            return True

        ids = self._parse_ids('id', task)

        return (len(self.ids) == 0 or len(self.ids.intersection(ids)) > 0) and \
               (len(self.not_ids) == 0 or len(self.not_ids.intersection(ids)) == 0)

    def match_refs(self, task):
        if len(self.refs) == 0:
            return True

        ids = self._parse_ids('after', task)
        ids |= self._parse_ids('ref', task)

        return len(ids) > 0 and \
               len(self.refs.intersection(ids)) > 0

    def match_after(self, task, attrs):
        if self.after is None:
            return True

        if len(self.after) == 0 and \
           len(attrs.get('after', [])) == 0:
            return True

        if self.task_by_id is None:
            return True

        parents = self._parse_ids('after', task)

        if len(self.after) == 0:
            # normal sequence behaviour
            return not self.hide_sequential or \
                   all([parentid not in self.task_by_id or
                        any([other.is_completed for other in self.task_by_id[parentid]]) 
                        for parentid in parents])
        else:
            # collect all indirect parents, too
            for taskid in task.attr_id:
                parents |= self.parents.get(taskid, set())
            return any([parent in parents for parent in self.after])


def get_relative_date(text, fmt=None):
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri',
                'sat', 'sun']
    days = 0
    weeks = 0
    months = 0
    years = 0
    value = ''
    today = datetime.datetime.now()

    if text.lower() == 'today':
        if fmt is not None:
            return today.strftime(fmt)
        return today
    if text.lower() == 'tomorrow':
        then = today + datetime.timedelta(days=1)
        if fmt is not None:
            return then.strftime(fmt)
        return then
    if text.lower() in ['next-week', 'week']:
        return today + datetime.timedelta(weeks=1)
    if text.lower() in weekdays:
        index = weekdays.index(text.lower())
        days = (index - today.weekday()) % 7
        if days == 0:
            days = 7
        then = today + datetime.timedelta(days=days)
        if fmt is not None:
            return then.strftime(fmt)
        return then

    for char in text.lower():
        if char in string.digits:
            value += char
        elif char in '+-' and len(value) == 0:
            if char == '-':
                value = char
        elif value.isnumeric() or (value.startswith('-') and value[1:].isnumeric()):
            if char == 'd':
                days += int(value)
            elif char == 'w':
                weeks += int(value)
            elif char == 'm':
                months += int(value)
            elif char == 'y':
                years += int(value)
            else:
                # parse error
                return None
            value = ''
        else:
            # parse error
            return None

    if value.isnumeric() or (value.startswith('-') and value[1:].isnumeric()):
        days += int(value)

    month = today.month + months
    if month > 12:
        years += month // 12
        month = month % 12

    year = today.year + years

    if year + years > datetime.MAXYEAR:
        year = datetime.MAXYEAR

    then = datetime.date(year, month, 1) + \
           datetime.timedelta(days=today.day + days - 1,
                              weeks=weeks)
    if fmt is not None:
        then = then.strftime(fmt)
    return then

