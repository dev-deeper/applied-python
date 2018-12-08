from subprocess import Popen
from time import sleep


if __name__ == '__main__':
    Popen(['python3', 'asyncfs.py', '-n', 'node01'])
    Popen(['python3', 'asyncfs.py', '-n', 'node02'])
    Popen(['python3', 'asyncfs.py', '-n', 'node03'])

    try:
        sleep(100)
    except KeyboardInterrupt:
        pass
