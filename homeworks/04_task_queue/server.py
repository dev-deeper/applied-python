import argparse
import socket
from datetime import datetime, timedelta
from os import path as osp
from pickle import dump, load
from uuid import uuid4


class Task:
    def __init__(self, length, data, timeout):
        self._length = int(length)
        self._data = data
        self._timeout = timeout
        self._id = uuid4().hex
        self._in_progress = False
        self._expired_time = None

    @property
    def id(self):
        return self._id

    @property
    def length(self):
        return self._length

    @property
    def data(self):
        return self._data

    @property
    def in_progress(self):
        return self._in_progress

    @property
    def expired_time(self):
        return self._expired_time

    def get(self):
        self._expired_time = datetime.now() + timedelta(0, self._timeout)
        self._in_progress = True

    def stop(self):
        self._in_progress = False


class Queue:
    def __init__(self):
        self._task_count = 0
        self._task_id_list = []
        self._tasks = []

    def check_timeout(self):
        for task in self._tasks:
            if task.in_progress and datetime.now() > task.expired_time:
                task.stop()

    def add_task(self, length, data, timeout):
        task = Task(length, data, timeout)
        self._task_id_list.append(task.id)
        self._tasks.append(task)
        self._task_count += 1
        return task.id

    def in_check_task(self, task_id):
        return 'YES' if task_id in self._task_id_list else 'NO'

    def get_task(self):
        if not self._task_id_list:
            return 'NONE'
        else:
            for task in self._tasks:
                if not task.in_progress:
                    task.get()
                    return f'{task.id} {task.length} {task.data}'
            return 'NONE'

    def ack_task(self, task_id):
        if task_id not in self._task_id_list:
            return 'NO'
        idx = self._task_id_list.index(task_id)
        if not self._tasks[idx].in_progress:
            return 'NO'
        del self._task_id_list[idx], self._tasks[idx]
        self._task_count -= 1
        return 'YES'


class Queues:
    def __init__(self, timeout):
        self._queues = {}
        self._timeout = timeout

    def _check_timeout(self):
        for queue in self._queues:
            self._queues[queue].check_timeout()

    def do_task(self, input_data):
        try:
            req_type = input_data[0]
            if req_type == 'ADD':
                queue, length, data = input_data[1:]
                if queue not in self._queues:
                    self._queues[queue] = Queue()
                return self._queues[queue].add_task(length, data, self._timeout)
            elif req_type == 'GET':
                self._check_timeout()
                queue = input_data[1]
                if queue not in self._queues:
                    return 'NONE'
                else:
                    return self._queues[queue].get_task()
            elif req_type == 'ACK':
                self._check_timeout()
                queue, task_id = input_data[1:]
                if queue not in self._queues:
                    return 'NO'
                else:
                    return self._queues[queue].ack_task(task_id)
            elif req_type == 'IN':
                queue, task_id = input_data[1:]
                if queue not in self._queues:
                    return 'NO'
                else:
                    return self._queues[queue].in_check_task(task_id)
            else:
                raise ValueError
        except (IndexError, ValueError):
            return 'ERROR'


class TaskQueueServer:
    dbfilename = 'server.db'

    def __init__(self, ip, port, path, timeout):
        self._ip = ip
        self._port = port
        self._path = path
        self._timeout = timeout
        self._buffer = 1024
        self._dbfile = osp.join(self._path, self.dbfilename)
        self._queues = self._load()

    def _load(self):
        if osp.isfile(self._dbfile):
            try:
                with open(self._dbfile, 'rb') as db:
                    q = load(db)
            except OSError:
                print('DB load error')
                exit(1)
        else:
            q = Queues(self._timeout)
        return q

    def _save(self):
        try:
            with open(self._dbfile, 'wb') as db:
                dump(self._queues, db)
            return 'OK'
        except OSError:
            return 'ERROR'

    def _start(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind((self._ip, self._port))
        connection.listen(1)
        return connection

    def _recvall(self, connection):
        data = b''
        while True:
            buff = connection.recv(self._buffer)
            data += buff
            if len(buff) < self._buffer:
                break
        return data

    def _work(self, connection):
        while True:
            current_connection, address = connection.accept()
            while True:
                conn_data = self._recvall(current_connection).decode().strip().split(' ')
                if conn_data[0] == 'SAVE':
                    current_connection.send(self._save().encode())
                else:
                    current_connection.send(self._queues.do_task(conn_data).encode())
                current_connection.shutdown(1)
                current_connection.close()
                break

    def run(self):
        connection = None
        try:
            connection = self._start()
            self._work(connection)
        except OSError as e:
            if e.errno == 98:
                """Exit if 'Address already in use' situation"""
                print('Address already in use')
                exit(1)
        except KeyboardInterrupt:
            connection.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip address')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
