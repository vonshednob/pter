class Source:
    def __init__(self, source):
        self.source = source
        self.last_change = 0
        self.displayname = self.filename.name
        self._contexts = set()
        self._projects = set()
        self.refresh()

    @property
    def contexts(self):
        return self._contexts

    @property
    def projects(self):
        return self._projects

    def __lt__(self, other):
        return self.displayname < other.displayname

    def update_contexts_and_projects(self):
        self._projects = set()
        self._contexts = set()
        for task in self.source.tasks:
            if task.description is None or len(task.description) == 0:
                continue
            self._projects |= {word for word in task.description.split(' ') if word.startswith('+')}
            self._contexts |= {word for word in task.description.split(' ') if word.startswith('@')}

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
        for task in self.source.parse():
            task.todotxt = self
            if task.description is None or len(task.description) == 0:
                continue
            self._projects |= {word for word in task.description.split(' ') if word.startswith('+')}
            self._contexts |= {word for word in task.description.split(' ') if word.startswith('@')}
        return self.source.tasks

    @property
    def tasks(self):
        return self.source.tasks

    @property
    def filename(self):
        return self.source.filename

