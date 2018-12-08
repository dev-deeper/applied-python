import argparse
import asyncio
import concurrent.futures
import os
import sys
from datetime import datetime, timedelta

import yaml
from aiohttp import web, ClientSession


class FS:
    """FILE STORAGE CLASS"""

    def __init__(self, cfg):
        self._port = int(cfg['port'])
        self._host = cfg['host']
        self._wdir = cfg['wdir']
        self._nodes = cfg['nodes']
        self._save_local = cfg['save_local']
        self._save_timeout = cfg['save_timeout']
        self._files_expired_time = {}
        self._app = None

    def run(self):
        self._app = web.Application()
        self._app.add_routes([
            web.get('/{file}', self._handler)
        ])
        web.run_app(self._app,
                    host=self._host,
                    port=self._port)

    async def _handler(self, request):
        """
        `strict` var  - find the file in the local or a remote repos (default)
                        or in the local only

        Examples:
                http://localhost:8080/file     - find in all repos (default)
                http://localhost:8080/file?s=1 - find local only
        """
        filename = request.match_info.get('file')
        strict = request.query.get('s') == '1'

        # CHECK FILES EXPIRED TIME FROM OTHER HOSTS
        if filename in self._files_expired_time and bool(datetime.now() > self._files_expired_time[filename]):
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, self._remove_file, filename)
            del self._files_expired_time[filename]

        if filename not in os.listdir(self._wdir):
            # FILE NOT FOUND LOCALLY
            if strict:
                return web.Response(text='404: File not Found\n', status=404)

            node_id, text = await self.fetch_all(filename)
            if node_id is not None:
                # FILE FOUND ON REMOTE HOST
                save_local = self._nodes[node_id].get('save_local',  # NODE VALUE
                                                      self._save_local)  # GLOBAL VALUE
                if save_local:
                    timeout = self._nodes[node_id].get('save_timeout',  # NODE VALUE
                                                       self._save_timeout)  # GLOBAL VALUE
                    self._files_expired_time[filename] = datetime.now() + timedelta(0, timeout)

                    loop = asyncio.get_running_loop()
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        await loop.run_in_executor(pool, self._write_file, filename, text)
                return web.Response(text=text)

            # FILE NOT FOUND ON REMOTE HOSTS
            return web.Response(text='404: File not Found\n', status=404)

        else:
            # FILE FOUND LOCALLY
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, self._read_file, filename)
            return web.Response(text=result)

    async def fetch_all(self, file_name):
        futures = [self.get_remote(node_id, node, file_name) for node_id, node in enumerate(self._nodes)]
        results, _ = await asyncio.wait(futures)
        for response in results:
            if not response.exception():
                return response.result()
        return None, None

    async def get_remote(self, node_id, node, filename):
        text = await self.fetch_url(f"{node['url']}/{filename}?s=1")
        if text:
            return node_id, text
        else:
            raise FileNotFoundError

    @staticmethod
    async def fetch_url(url):
        async with ClientSession() as session, session.get(url) as resp:
            return await resp.text() if resp.status == 200 else False

    def _read_file(self, file):
        with open(os.path.join(self._wdir, file), "r") as f:
            return f.read()

    def _write_file(self, file, text):
        with open(os.path.join(self._wdir, file), "w") as f:
            f.write(text)

    def _remove_file(self, file):
        os.remove(os.path.join(self._wdir, file))


def parse_args(args):
    parser = argparse.ArgumentParser(description="This is a aiohttp web daemon")
    parser.add_argument(
        '-n',
        action="store",
        dest="node_name",
        default=False,
        help='Node name')
    return parser.parse_args(args)


if __name__ == '__main__':
    config = None
    try:
        with open('config.yaml', 'r') as stream:
            config = yaml.load(stream)
    except (Exception, yaml.YAMLError) as err:
        print(err)
        exit(1)

    args = parse_args(sys.argv[1:])
    node = FS(config[args.node_name])
    node.run()
