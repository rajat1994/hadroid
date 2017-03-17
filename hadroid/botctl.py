"""
Hadroid Controller.

This is the controller for the bot, that sets up all of the plumbing for
authenticating to Gitter, listening on channel stream or executing commands.

Option --room=<room> can be either an organization or repo name room name,
e.g.: 'myorg', 'myorg/myrepo', or a Gitter username for a One-To-One
conversation. If skipped the 'ROOM' config variable is used.

Controller has multiple modes of operation:
'gitter' executes a single bot command and broadcast it to the gitter channel
'stream' launches the boot in the "listening" mode on given Gitter channel.
'cron' launches the periodic task loop.

Usage:
    botctl stream [--room=<room>] [--verbose]
    botctl cron [--room=<room>] [--verbose]
    botctl gitter <cmd>... [--room=<room>]
    botctl stdout <cmd>...

Examples:
    botctl stream test
    botctl cron test
    botctl gitter test "menu today"
    botctl gitter qa "echo Hello everyone!"

Options:
    -h --help       Show this help.
    --room=<room>   Room where the bot will run.
    --verbose       Show errors.
    --version       Show version.
"""


import socket
import pickle
from enum import Enum

from multiprocessing import Process
from uuid import uuid4
from hadroid import C

#from hadroid.client import StdoutClient, GitterClient, StreamClient, CronClient


# def main():
#     """Main function."""
#     args = docopt.docopt(__doc__, version=__version__)
#
#     if args['stdout']:
#         bot_args = docopt_parse(bot_doc, args['<cmd>'], version=__version__)
#         bot_main(StdoutClient(), bot_args)
#
#     room_id = GitterClient(C.GITTER_PERSONAL_ACCESS_TOKEN).resolve_room_id(
#         args.get('--room', C.ROOM))
#
#     if args['stream']:
#         client = StreamClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
#         client.listen()
#     if args['cron']:
#         client = CronClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
#         client.listen()
#     elif args['gitter']:
#         client = GitterClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
#         bot_args = docopt_parse(bot_doc, args['<cmd>'], version=__version__)
#         bot_main(client, bot_args)


class ClientAction(Enum):
    START = 1
    STOP = 2
    STATUS = 3
    LIST = 4

    def __init__(self, value):
        """Hack."""

    def __eq__(self, other):
        """Equality test."""
        return self.value == other

    def __str__(self):
        """Return its value."""
        return self.value


def manage(processes, action=None, client_name=None, **kwargs):
    if ClientAction[action] == ClientAction.START:
        client_class = C.CLIENTS[client_name]
        client_id = uuid4()
        args = (C.GITTER_PERSONAL_ACCESS_TOKEN, )
        p = Process(target=client_class, args=args, kwargs=kwargs)
        processes[client_id] = p
        p.start()
        return "Created {0}".format(client_id)
    elif ClientAction[action] == ClientAction.STOP:
        client_id = kwargs.get('id')
        p = processes[client_id]
        p.terminate()
        del processes[client_id]
        return "Stopped {0}".format(client_id)
    elif ClientAction[action] == ClientAction.STATUS:
        return [k for k in processes.keys()]
    elif ClientAction[action] == ClientAction.LIST:
        return [(k, v.__class) for k, v in processes.items()]


def server():
    HOST = 'localhost'
    PORT = 50007
    processes = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                print('Message from', addr)
                import ipdb; ipdb.set_trace()
                data = conn.recv(1024)
                kwargs = pickle.loads(data)
                ret = manage(processes, **kwargs)
                b_ret = pickle.dumps(ret)
                conn.sendall(b_ret)


def client():
    HOST = 'localhost'    # The remote host
    PORT = 50007              # The same port as used by the server
    action = input('Action?')
    name = input('Name?')
    msg = dict(action=action, name=name)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        b_msg = pickle.dumps(msg)
        s.sendall(b_msg)
        b_data = s.recv(1024)
        data = pickle.loads(b_data)
        print(data)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 's':
        server()
    if sys.argv[1] == 'c':
        client()
