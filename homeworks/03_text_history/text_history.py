from copy import copy


class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._history = {}

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def add_history(self, action):
        self._history[self._version] = copy(action)

    def check(self, pos, length=None):
        if pos is None:
            pos = len(self._text)
        elif not 0 <= pos <= len(self._text) or length is not None and pos + length > len(self._text):
            raise ValueError
        return pos

    def insert(self, text, pos=None):
        pos = self.check(pos)
        action = InsertAction(pos, text, self._version)
        return self.action(action)

    def replace(self, text, pos=None):
        pos = self.check(pos)
        action = ReplaceAction(pos, text, self._version)
        return self.action(action)

    def delete(self, pos, length):
        pos = self.check(pos, length)
        action = DeleteAction(pos, length, self._version)
        return self.action(action)

    def action(self, action):
        if not (action.to_version > action.from_version):
            raise ValueError
        self._text = action.apply(self._text)
        self.add_history(action)
        self._version = action.to_version
        return self._version

    def get_actions(self, from_version=None, to_version=None):

        if from_version is None and to_version is None or from_version == to_version == 0:
            return []

        if not self._history:
            raise ValueError

        if from_version is None:
            from_version = 0
        elif from_version < 0:
            raise ValueError

        if to_version is None:
            to_version = max(self._history.keys())
        elif from_version > to_version or to_version > max(self._history.keys()):
            raise ValueError

        out = []
        for ver, obj in self._history.items():
            if ver < from_version:
                continue
            elif ver <= to_version:
                out.append(obj)
            else:
                break
        return out


class Action:
    def __init__(self, pos, from_version, to_version):
        if to_version is None:
            to_version = from_version + 1
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    @staticmethod
    def apply(self, text):
        ...


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version=None):
        super(InsertAction, self).__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, text):
        return text[:self.pos] + self.text + text[self.pos:]


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version=None):
        super(ReplaceAction, self).__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, text):
        return text[:self.pos] + self.text + text[self.pos + len(self.text):]


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version=None):
        super(DeleteAction, self).__init__(pos, from_version, to_version)
        self.length = length

    def apply(self, text):
        return text[:self.pos] + text[self.pos + self.length:]
