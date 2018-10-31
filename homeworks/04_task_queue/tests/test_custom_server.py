import socket
import subprocess
import time
from os import remove, path as osp
from unittest import TestCase, main as unittest_main


class ServerBaseTest(TestCase):
    port = 5555
    ip = '127.0.0.1'
    timeout = 300
    path = './'

    def setUp(self):
        self.server_start()

    def tearDown(self):
        self.db_remove()
        self.server_stop()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.__class__.ip, self.__class__.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def server_start(self):
        self.server = subprocess.Popen(['python3', 'server.py',
                                        '-i', self.__class__.ip,
                                        '-p', str(self.__class__.port),
                                        '-t', str(self.__class__.timeout),
                                        '-c', self.__class__.path])
        time.sleep(0.5)

    def server_stop(self):
        self.server.terminate()
        self.server.wait(timeout=2)

    def db_remove(self):
        db_file = osp.join(self.__class__.path, 'server.db')
        try:
            remove(db_file)
        except OSError as e:
            # PASS 'FILE NOT FOUND' SITUATION
            if e.errno == 2:
                pass

    def test_port_base_scenario(self):
        self.server_stop()
        self.__class__.port = 8015
        self.server_start()
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        task_id = self.send(b'ADD Q1 2 12')
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK Q1 ' + task_id))
        self.assertEqual(task_id + b' 2 12', self.send(b'GET Q1'))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))

    def test_early_get_ack_scenario(self):
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        task_id = self.send(b'ADD Q1 2 12')
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK Q1 ' + task_id))
        self.assertEqual(task_id + b' 2 12', self.send(b'GET Q1'))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))

    def test_timeout_scenario(self):
        self.server_stop()
        self.__class__.timeout = 5
        self.server_start()
        task_id1 = self.send(b'ADD Q1 2 12')
        task_id2 = self.send(b'ADD Q1 3 123')
        task_id3 = self.send(b'ADD Q1 4 1234')
        self.assertEqual(task_id1 + b' 2 12', self.send(b'GET Q1'))
        self.assertEqual(task_id2 + b' 3 123', self.send(b'GET Q1'))
        self.assertEqual(task_id3 + b' 4 1234', self.send(b'GET Q1'))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id1))
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id2))
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id3))
        time.sleep(6)
        self.assertEqual(b'NO', self.send(b'ACK Q1 ' + task_id1))
        self.assertEqual(b'NO', self.send(b'ACK Q1 ' + task_id2))
        self.assertEqual(b'NO', self.send(b'ACK Q1 ' + task_id3))
        self.assertEqual(task_id1 + b' 2 12', self.send(b'GET Q1'))
        self.assertEqual(task_id2 + b' 3 123', self.send(b'GET Q1'))
        self.assertEqual(task_id3 + b' 4 1234', self.send(b'GET Q1'))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id2))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id3))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id1))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))

    def test_save_scenario(self):
        self.server_stop()
        self.__class__.path = '/tmp'
        self.server_start()
        task_id1 = self.send(b'ADD Q1 2 12')
        task_id2 = self.send(b'ADD Q1 3 123')
        task_id3 = self.send(b'ADD Q1 4 1234')
        self.assertEqual(task_id1 + b' 2 12', self.send(b'GET Q1'))
        self.assertEqual(task_id2 + b' 3 123', self.send(b'GET Q1'))
        self.assertEqual(task_id3 + b' 4 1234', self.send(b'GET Q1'))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        self.assertEqual(b'OK', self.send(b'SAVE'))
        self.server_stop()
        self.server_start()
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id1))
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id2))
        self.assertEqual(b'YES', self.send(b'IN Q1 ' + task_id3))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id1))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id2))
        self.assertEqual(b'YES', self.send(b'ACK Q1 ' + task_id3))
        self.assertEqual(b'NONE', self.send(b'GET Q1'))
        self.assertEqual(b'OK', self.send(b'SAVE'))

    def test_bad_requests_scenario(self):
        self.assertEqual(b'ERROR', self.send(b'ADD'))
        self.assertEqual(b'ERROR', self.send(b'ADD 1'))
        self.assertEqual(b'ERROR', self.send(b'GET'))


if __name__ == '__main__':
    unittest_main()
