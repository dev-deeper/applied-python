import os
from collections.abc import MutableMapping
from random import randint


class DirDict(MutableMapping):
    def __init__(self, folder):
        self._path = folder
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def _get_file_content(self, filename) -> str:
        """Get file content"""
        try:
            with open(os.path.join(self._path, filename), 'r') as db:
                lines = ''
                while True:
                    line = db.readline()
                    if line == '':
                        break
                    else:
                        lines += line
            return lines
        except OSError as e:
            raise OSError(f'Loading Error: {e.strerror} \'{e.filename}\'')

    def __getitem__(self, key) -> str:
        """
        Return the item of the dictionary with key 'key'.
        Raises a KeyError if key is not in the map"""
        if not key:
            """Raise error if key is empty"""
            raise SyntaxError(key)
        elif not os.path.isfile(os.path.join(self._path, key)):
            """Raise error if key not exist"""
            raise KeyError(key)
        else:
            return self._get_file_content(key)

    def __setitem__(self, key, value) -> None:
        """Set d[key] to value"""
        if not key:
            """Raise error if key is empty"""
            raise SyntaxError(key)
        else:
            try:
                with open(os.path.join(self._path, str(key)), 'w') as db:
                    db.write(str(value))
            except OSError as e:
                print(f'Saving Error: {e.strerror} \'{e.filename}\'')

    def __delitem__(self, key) -> None:
        """
        Remove d[key] from d.
        Raises a KeyError if key is not in the map."""
        if not key:
            """Raise error if key is empty"""
            raise SyntaxError(key)
        else:
            file = os.path.join(self._path, key)
            if not os.path.isfile(file):
                raise KeyError(key)
            else:
                os.remove(file)

    def __len__(self) -> int:
        """Return the number of items in the dictionary"""
        return len(os.listdir(self._path))

    def __iter__(self):
        """Return an iterator over the keys of the dictionary."""
        for key in os.listdir(self._path):
            yield key

    def clear(self) -> None:
        """Removes all items from the dictionary"""
        for key in os.listdir(self._path):
            os.remove(os.path.join(self._path, key))

    def copy(self, folder):
        """
        Returns a shallow copy of the dictionary.

        :param folder: The folder path for new DirDict
        """
        if not folder:
            """Raise error if folder is empty"""
            raise SyntaxError(folder)
        keys = [key for key in os.listdir(self._path)]
        if not keys:
            return DirDict(folder)
        else:
            new_dict = DirDict(folder)
            for key in keys:
                new_dict[key] = self._get_file_content(key)
            return new_dict

    @classmethod
    def fromkeys(cls, seq, folder, value=None):
        """
        Create a new dictionary with keys from seq and values set to value.
        fromkeys() is a class method that returns a new dictionary.
        value defaults to None."""
        new_dict = DirDict(folder)
        for item in seq:
            new_dict[item] = value
        return new_dict

    def get(self, key, default=None):
        """Returns the value for the specified key if key is in dictionary."""
        return self._get_file_content(key) if key in os.listdir(self._path) else default

    def items(self) -> list:
        """Returns a list containing the a tuple for each key value pair"""
        return [(key, self._get_file_content(key)) for key in os.listdir(self._path)]

    def keys(self) -> list:
        """Returns a list containing the dictionary's keys"""
        return os.listdir(self._path)

    def pop(self, key, default=None):
        """Removes and returns an element from a dictionary having the given key"""
        file = os.path.join(self._path, key)
        if os.path.isfile(file):
            content = self._get_file_content(file)
            os.remove(file)
            return content
        elif default is None:
            raise KeyError(key)
        else:
            return default

    def popitem(self) -> tuple:
        """Returns and removes an arbitrary element (key, value) pair from the dictionary"""
        keys = os.listdir(self._path)
        if not keys:
            raise KeyError('popitem(): dictionary is empty')
        rand_key = keys[randint(0, len(keys) - 1)]
        r_tuple = rand_key, self._get_file_content(rand_key)
        os.remove(os.path.join(self._path, rand_key))
        return r_tuple

    def setdefault(self, key, default=None):
        """If key is in the dictionary, return its value.
        If not, insert key with a value of default and return default.
        default defaults to None."""
        if key in os.listdir(self._path):
            return self._get_file_content(os.path.join(self._path, key))
        else:
            self.__setitem__(key, default)
            return default

    def values(self) -> list:
        """Returns a list of all the values in the dictionary"""
        return [self._get_file_content(os.path.join(self._path, key)) for key in os.listdir(self._path)]


if __name__ == '__main__':
    d = DirDict('/tmp/dirname')
    d['key2'] = '2'
    d['key1'] = '1'
    dd = dict()
    dd['key2'] = '2'
    dd['key1'] = '1'
