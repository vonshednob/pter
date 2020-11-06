from pter import common


class Source:
    def __init__(self, source):
        self.source = source
        self.last_change = 0
        self.displayname = self.filename.name
        self._contexts = set()
        self._projects = set()
        self._task_by_id = {}
        self.refresh()

    @property
    def contexts(self):
        return self._contexts

    @property
    def projects(self):
        return self._projects

    @property
    def task_ids(self):
        return set(self._task_by_id.keys())

    def __lt__(self, other):
        return self.displayname < other.displayname

    def update_contexts_and_projects(self):
        self._projects = set()
        self._contexts = set()
        self._task_by_id = {}
        for task in self.source.tasks:
            self.update_from_task(task)

    def update_from_task(self, task):
        if task.description is None or len(task.description) == 0:
            return
        for word in task.description.split(' '):
            if word.startswith('+'):
                self._projects.add(word)
            elif word.startswith('@'):
                self._contexts.add(word)
            elif word.startswith(common.ATTR_ID + ':'):
                _, taskid = word.split(':', 1)
                if len(taskid) > 0:
                    self._task_by_id[taskid] = task

    def refresh(self):
        last_change = self.last_change
        if self.filename.exists():
            last_change = self.source.filename.stat().st_mtime
        has_changed = False

        if last_change != self.last_change:
            self.last_change = last_change
            has_changed = True

        return has_changed

    def save(self, safe=True):
        self.source.save(safe=safe)
        self.refresh()

    def parse(self):
        self._projects = set()
        self._contexts = set()
        self._task_by_id = {}
        for task in self.source.parse():
            task.todotxt = self
            self.update_from_task(task)
        return self.source.tasks

    def task(self, taskid, default=None):
        return self._task_by_id.get(taskid, default)

    @property
    def tasks(self):
        return self.source.tasks

    @property
    def filename(self):
        return self.source.filename

