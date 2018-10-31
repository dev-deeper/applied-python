import argparse
import socket
from os import path as osp
from pickle import dump, load
from uuid import uuid4
from datetime import datetime


class Task:
    def __init__(self, length, data):
        self._length = int(length)
        self._data = data
        self._id = uuid4().hex
        self._in_progress = False
        self._get_time = None

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
    def get_time(self):
        return self._get_time

    def get(self):
        self._get_time = datetime.now()
        self._in_progress = True

    def stop(self):
        self._in_progress = False


class Queue:
    def __init__(self, name):
        self._name = name
        self._task_count = 0
        self._task_id_list = []
        self._tasks = []
        self._last_get_idx = -1

    @property
    def name(self):
        return self._name

    def _task_count_increment(self):
        self._task_count += 1

    def _task_count_decrement(self):
        self._task_count -= 1

    def _last_get_idx_decrement(self):
        self._task_count -= 1

    def _get_next(self, task_idx):
        return task_idx + 1 if task_idx < self._task_count - 1 else 0

    def check_timeout(self, timeout):
        for task in self._tasks:
            if task.in_progress and (datetime.now() - task.get_time).seconds > timeout:
                task.stop()

    def add_task(self, length, data):
        task = Task(length, data)
        self._task_id_list.append(task.id)
        self._tasks.append(task)
        self._task_count_increment()
        return task.id

    def in_check_task(self, task_id):
        return 'YES' if task_id in self._task_id_list else 'NO'

    def get_task(self):
        if not self._task_id_list:
            return 'NONE'
        else:
            curr_idx = start_idx = self._get_next(self._last_get_idx)
            while True:
                task = self._tasks[curr_idx]
                if not task.in_progress:
                    task.get()
                    self._last_get_idx = curr_idx
                    return f'{task.id} {task.length} {task.data}'
                curr_idx = self._get_next(curr_idx)
                if curr_idx == start_idx:
                    break
            return 'NONE'

    def ack_task(self, task_id):
        if task_id not in self._task_id_list:
            return 'NO'
        idx = self._task_id_list.index(task_id)
        if not self._tasks[idx].in_progress:
            return 'NO'
        del self._task_id_list[idx], self._tasks[idx]
        self._task_count_decrement()
        self._last_get_idx_decrement()
        return 'YES'


class Queues:
    def __init__(self):
        self._queues = {}

    def check_timeout(self, timeout):
        for queue in self._queues:
            self._queues[queue].check_timeout(timeout)

    def add(self, queue, length, data):
        if queue not in self._queues:
            self._queues[queue] = Queue(queue)
        return self._queues[queue].add_task(length, data)

    def in_check(self, queue, task_id):
        return 'NO' if queue not in self._queues else \
            self._queues[queue].in_check_task(task_id)

    def get(self, queue):
        return 'NONE' if queue not in self._queues else \
            self._queues[queue].get_task()
    
    def ack(self, queue, task_id):
        return 'NO' if queue not in self._queues else \
            self._queues[queue].ack_task(task_id)


class TaskQueueServer:
    dbfilename = 'server.db'

    def __init__(self, ip, port, path, timeout):
        self._ip = ip
        self._port = port
        self._path = path
        self._dbfile = osp.join(self._path, self.dbfilename)
        self._queues = self._load()
        self._timeout = timeout
        self._buffer = 1024

    def _load(self):
        if osp.isfile(self._dbfile):
            try:
                with open(self._dbfile, 'rb') as db:
                    q = load(db)
            except OSError:
                print('DB load error')
                exit(1)
        else:
            q = Queues()
        return q

    def save(self):
        try:
            with open(self._dbfile, 'wb') as db:
                dump(self._queues, db)
            return 'OK'
        except OSError:
            raise ValueError

    def start(self):
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

    @staticmethod
    def _send(connection, data):
        connection.send(data.encode())

    def work(self, connection):
        while True:
            current_connection, address = connection.accept()
            while True:
                conn_data = self._recvall(current_connection).decode().strip().split(' ')
                req_type = conn_data[0]
                self._queues.check_timeout(self._timeout)
                try:
                    if req_type == 'ADD':
                        queue, length, data = conn_data[1:]
                        self._send(current_connection, self._queues.add(queue, length, data))
                    elif req_type == 'GET':
                        queue = conn_data[1]
                        self._send(current_connection, self._queues.get(queue))
                    elif req_type == 'ACK':
                        queue, task_id = conn_data[1:]
                        self._send(current_connection, self._queues.ack(queue, task_id))
                    elif req_type == 'IN':
                        queue, task_id = conn_data[1:]
                        self._send(current_connection, self._queues.in_check(queue, task_id))
                    elif req_type == 'SAVE':
                        self._send(current_connection, self.save())
                    else:
                        raise ValueError
                except (IndexError, ValueError):
                    self._send(current_connection, 'ERROR')

                current_connection.shutdown(1)
                current_connection.close()
                break

    def run(self):
        connection = None
        try:
            connection = self.start()
            self.work(connection)
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
