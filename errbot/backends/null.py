import logging
from time import sleep
from errbot.backends.base import ONLINE

from errbot.backends.test import TestIdentifier
from errbot.errBot import ErrBot


# Can't use __name__ because of Yapsy
log = logging.getLogger('errbot.backends.null')


class ConnectionMock(object):
    def send(self, mess):
        pass

    def send_message(self, mess):
        pass


class NullBackend(ErrBot):
    conn = ConnectionMock()
    running = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_identifier = self.build_identifier('Err')  # whatever

    def serve_forever(self):
        self.connect()  # be sure we are "connected" before the first command
        self.connect_callback()  # notify that the connection occured
        try:
            while self.running:
                sleep(1)

        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            log.debug("Trigger disconnect callback")
            self.disconnect_callback()
            log.debug("Trigger shutdown")
            self.shutdown()

    def connect(self):
        if not self.conn:
            self.conn = ConnectionMock()
        return self.conn

    def build_identifier(self, strrep):
        return TestIdentifier(strrep)

    def join_room(self, room, username=None, password=None):
        pass  # just ignore that

    def shutdown(self):
        if self.running:
            self.running = False
            super().shutdown()  # only once (hackish)

    def change_presence(self, status: str = ONLINE, message: str = '') -> None:
        pass

    def build_reply(self, mess, text=None, private=False):
        pass

    def prefix_groupchat_reply(self, message, identifier):
        pass

    def query_room(self, room):
        pass

    def rooms(self):
        pass

    @property
    def mode(self):
        return 'null'
