import pytest
import socks5
from proxy_plus.socks import Socks5Server


@pytest.fixture
async def socks_s(loop, free_bind):
    addr = free_bind()
    server = await loop.create_server(Socks5Server, *addr)
    yield addr
    server.close()
    await server.wait_closed()


async def handshake_socks5(reader, writer):
    scon = socks5.Connection(our_role="client")
    scon.initiate_connection()
    data = scon.send(socks5.GreetingRequest(socks5.AUTH_TYPE["NO_AUTH"]))
    writer.write(data)
    gr_resp = _recv(reader, scon)
    socks5.Request(socks5.REQ_COMMAND["CONNECT"],
                   atyp=socks5.ADDR_TYPE["IPV4"], )

async def _recv(reader, con):
    while True:
        event = con.recv(await reader.read(1024))
        if event != socks5.NeedMoreData:
            return event




@pytest.mark.asyncio
class TestSocks:
    async def test_socks5(self, socks_s, echo_server):
