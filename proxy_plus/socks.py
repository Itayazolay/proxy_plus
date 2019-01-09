import asyncio
import socks5
import errno

from proxy_plus.forwarder import Proxy

FAILURES = {
    errno.ENETUNREACH: socks5.RESP_STATUS["NETWORK_UNREACHABLE"],
    errno.ECONNREFUSED: socks5.RESP_STATUS["CONNECTION_REFUSED"],
    errno.EHOSTUNREACH: socks5.RESP_STATUS["HOST_UNREACHABLE"],
}


class Socks5Server(asyncio.Protocol):
    def __init__(self, create_connection=None) -> None:
        super().__init__()
        self.transport = None
        self._loop = asyncio.get_event_loop()
        self._cc = create_connection or self._loop.create_connection
        self._conn = socks5.Connection(our_role="server")
        self._event = None
        self._greeting = socks5.GreetingRequest(socks5.AUTH_TYPE["NO_AUTH"])

    def data_received(self, data):
        super().data_received(data)
        self._event = self._conn.recv(data)
        if type(self._event) == socks5.NeedMoreData:
            return
        elif type(self._event) is socks5.GreetingRequest:
            event = socks5.GreetingResponse(socks5.AUTH_TYPE["NO_AUTH"])
            self.transport.write(self._conn.send(event))
        elif type(self._event) is socks5.Request:
            self.transport.pause_reading()
            self._loop.call_soon(self._connect(self._event))
        else:
            pass  # WHOT

    async def _connect(self, event):
        ip, port = str(event.addr), event.port
        try:
            trans, proto = await self._loop.create_connection(
                Proxy(self.transport),
                ip, port)
            response = socks5.Response(socks5.RESP_STATUS["SUCCESS"],
                                       event.atyp, event.addr, event.port)
            self.transport.set_protocol(Proxy(trans))
            self.transport.write(self._conn.send(response))
            self.transport.resume_reading()
        except OSError as err:
            reason = FAILURES.get(err.errno,
                                  socks5.RESP_STATUS["GENRAL_FAILURE"])
            response = socks5.Response(reason,
                                       event.atyp, event.addr, event.port)
            self.transport.write(self._conn.send(response))
            self.transport.send_eof()
            self.transport.close()

    def eof_received(self):
        super().eof_received()

    def connection_made(self, transport):
        super().connection_made(transport)
        self.transport = transport
        self._conn.initiate_connection()
