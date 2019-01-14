import asyncio
import errno
import typing

import socks5

from proxy_plus.forwarder import Proxy

FAILURES = {
    errno.ENETUNREACH: socks5.RESP_STATUS["NETWORK_UNREACHABLE"],
    errno.ECONNREFUSED: socks5.RESP_STATUS["CONNECTION_REFUSED"],
    errno.EHOSTUNREACH: socks5.RESP_STATUS["HOST_UNREACHABLE"],
}


class Socks5Server(asyncio.Protocol):
    """Socks5 server protocol implementation."""

    def __init__(self, create_connection: typing.Coroutine = None, loop: asyncio.AbstractEventLoop = None) -> None:
        """
        Initialized Socks Connection(single).
        :param create_connection: create connection to use on connect.
        """
        super().__init__()
        self.transport = None
        self._loop = loop or asyncio.get_event_loop()
        self._cc = create_connection or self._loop.create_connection
        self._conn = socks5.Connection(our_role="server")
        self._event = None

    def data_received(self, data):
        """Handling data from client - implementing the protocol and states."""
        super().data_received(data)
        self._event = self._conn.recv(data)
        if isinstance(self._event, socks5.NeedMoreData):
            pass
        elif isinstance(self._event, socks5.GreetingRequest):
            event = socks5.GreetingResponse(socks5.AUTH_TYPE["NO_AUTH"])
            self.transport.write(self._conn.send(event))
        elif isinstance(self._event, socks5.Request):
            self.transport.pause_reading()
            self._loop.create_task(self._handle_socks5_req(self._event))
        else: # Whot tf happened
            self.transport.close()

    async def _handle_socks5_req(self, req: socks5.Request):
        if req.cmd == socks5.REQ_COMMAND["CONNECT"]:
            await self._connect(req)
        else:
            resp = socks5.Response(socks5.RESP_STATUS["COMMAND_NOT_SUPPORTED"],
                                   req.atyp, req.addr, req.port)
            self.transport.write(self._conn.send(resp))

    async def _connect(self, req: socks5.Request):
        addr, port = str(req.addr), req.port
        try:
            trans, _ = await self._loop.create_connection(
                lambda: Proxy(self.transport),
                addr, port)
            response = socks5.Response(socks5.RESP_STATUS["SUCCESS"],
                                       req.atyp, req.addr, req.port)
            self.transport.set_protocol(Proxy(trans))
            self.transport.write(self._conn.send(response))
            self.transport.resume_reading()
        except OSError as err:
            reason = FAILURES.get(err.errno, socks5.RESP_STATUS["GENRAL_FAILURE"])
            response = socks5.Response(reason, req.atyp, req.addr, req.port)
            self.transport.write(self._conn.send(response))
            self.transport.send_eof()
            self.transport.close()

    def connection_made(self, transport):
        """Client connected. """
        super().connection_made(transport)
        self.transport = transport
        self._conn.initiate_connection()
