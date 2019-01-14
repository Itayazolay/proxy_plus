import asyncio
import logging

logger = logging.getLogger(__name__)


class Proxy(asyncio.Protocol):
    """
    TCP Proxy protocol. Exposing events on one transport to the other.
    Only one direction.
    """
    def __init__(self, remote: asyncio.Transport):
        self.remote = remote
        self.transport = None

    def data_received(self, data):
        self.remote.write(data)

    def eof_received(self):
        self.remote.write_eof()

    def connection_made(self, transport):
        self.transport = transport
        super().connection_made(transport)

    def connection_lost(self, exc):
        super().connection_lost(exc)
        if not self.remote.is_closing():
            self.remote.close()

    def pause_writing(self):
        self.remote.pause_reading()

    def resume_writing(self):
        self.remote.resume_reading()
