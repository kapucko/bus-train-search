import json
import os
import sys
from threading import Thread


class ConfigLoader(Thread):

    def __init__(self, file):
        super(ConfigLoader, self).__init__()
        # self.file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file)
        self.file = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), file)
        self.file_timestamp = None
        self._config = None

    def load(self):
        try:
            statbuf = os.stat(self.file)
        except FileNotFoundError:
            return

        if self.file_timestamp != statbuf.st_mtime:
            # load config
            with open(self.file, 'r') as f:
                self._config = json.load(f)
            # update timestamp
            self.file_timestamp = statbuf.st_mtime

    def run(self):
        while True:
            self.load()

    @property
    def config(self):
        if self._config is None:
            self.load()
        return self._config
