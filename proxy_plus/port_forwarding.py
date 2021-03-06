import asyncio

from proxy_plus.forwarder import Proxy


class PortForwarding(asyncio.Protocol):
    def __init__(self, remote_address, create_connection,
                 loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.remote_address = remote_address
        self.create_connection = create_connection
        self.task = None
        self.transport = None
        self._buffer = b""  # WHEN WILL PYTHON FIX THIS SHIT
        self._proxy = None
        self._remote_proxy = None

    def connection_made(self, transport: asyncio.Transport):
        """Client connected - connect to remote."""
        self.transport = transport
        self.transport.pause_reading()
        self._proxy = Proxy(self.transport)
        self.task = self.loop.create_task(
            self.create_connection(lambda: self._proxy,
                                   *self.remote_address))
        self.task.add_done_callback(self._connected)

    def _connected(self, task):
        if task.exception():
            return  # forward exception?
        trans, _ = task.result()
        self._remote_proxy = proxy = Proxy(trans)
        self.transport.set_protocol(proxy)
        self.transport.resume_reading()
        if self._buffer:
            proxy.data_received(self._buffer)

    def connection_lost(self, exc):
        """Client disconnected, cancel task if needed."""
        if self.task:
            self.task.cancel()
        self.transport.close()

    def data_received(self, data):
        """Handle buffer-pause reading doesn't completly prevent data receive."""
        self._buffer += data


async def start_port_forwarding(create_server, create_connection,
                                server_addr, remote_address,
                                *, loop=None):
    loop = loop or asyncio.get_event_loop()
    forward = lambda: PortForwarding(remote_address, create_connection,
                                     loop=loop)

    return await create_server(forward, *server_addr)


async def start_local_port_forwarding(bind_address,
                                      create_connection,
                                      remote_address,
                                      loop=None):
    loop = loop or asyncio.get_event_loop()
    return await start_port_forwarding(loop.create_server, create_connection,
                                       bind_address, remote_address, loop=loop)


async def start_remote_port_forwarding(bind_address, create_server,
                                       remote_address, *, loop=None):
    loop = loop or asyncio.get_event_loop()
    return await start_port_forwarding(create_server, loop.create_connection,
                                       bind_address, remote_address)
