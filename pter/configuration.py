class Configuration:
    def __init__(self, conf):
        self.conf = conf

    def __getitem__(self, group):
        return self.conf[group]

    @property
    def sections(self):
        return self.conf.sections()

    def __contains__(self, item):
        return item in self.conf

    def get(self, group, item, default=None):
        if group in self.conf:
            return self.conf[group].get(item, default)
        else:
            return default

    def bool(self, group, item, default='n'):
        return self.get(group, item, default).lower() in ['y', 'yes', '1', 'true', 'on']

    def list(self, group, item, default='', sep=',', strip=True):
        return [e.strip() if strip else e for e in self.get(group, item, default).split(sep)]

    def number(self, group, item, default='0'):
        value = self.get(group, item, default)
        if value.isnumeric():
            return int(value)
        return None

    def color_pair(self, group, item, default=None):
        value = self.get(group, item, default)
        if value is None or len(value) == 0:
            return None

        result = [None, None]
        for idx, colnr in enumerate(value.split(',')):
            if idx >= 2:
                break
            
            colnr = colnr.strip()

            if not colnr.isnumeric():
                # TODO: accept some colors by name
                continue

            result[idx] = int(colnr)

        return result

