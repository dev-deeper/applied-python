from subprocess import Popen
from time import sleep
from unittest import TestCase

from requests import get


class FSTest(TestCase):

    def setUp(self):
        self.servers = [
                Popen(['python3', 'asyncfs.py', '-n', 'node01']),
                Popen(['python3', 'asyncfs.py', '-n', 'node02']),
                Popen(['python3', 'asyncfs.py', '-n', 'node03']),
            ]
        sleep(1)

    def tearDown(self):
        for server in self.servers:
            server.terminate()
            server.wait()

    def test_local_file(self):
        response = get("http://localhost:25001/xxx")
        self.assertEqual('XXX content', response.text)
        self.assertEqual(200, response.status_code)

    def test_local_nonexistent_file(self):
        response = get("http://localhost:25001/yyy?s=1")
        self.assertEqual(404, response.status_code)

    def test_remote_file_with_save(self):
        response = get("http://localhost:25001/yyy")
        self.assertEqual('YYY content', response.text)
        self.assertEqual(200, response.status_code)

    def test_remote_file(self):
        response = get("http://localhost:25001/zzz")
        self.assertEqual('ZZZ content', response.text)
        self.assertEqual(200, response.status_code)

    def test_remote_file_without_save(self):
        response = get("http://localhost:25001/zzz?s=1")
        self.assertEqual(404, response.status_code)
