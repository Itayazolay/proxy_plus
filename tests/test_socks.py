import asyncio

import pytest
import socks5
from proxy_plus.socks import Socks5Server


@pytest.fixture
async def socks_s(loop, free_bind):
    addr = free_bind()
    Socks5Server()
    server = await loop.create_server(Socks5Server, *addr)
    yield addr
    server.close()
    await server.wait_closed()

@pytest.fixture
def s_client():
    client = socks5.Connection(our_role="client")
    client.initiate_connection()
    return client


@pytest.fixture
def greeting():
    return socks5.GreetingRequest([socks5.AUTH_TYPE["NO_AUTH"]])

@pytest.fixture
async def greeted(socks_s, greeting, s_client):
    reader, writer = await asyncio.open_connection(*socks_s)
    writer.write(s_client.send(greeting))
    e = socks5.NeedMoreData()
    while isinstance(e, socks5.NeedMoreData):
        dt = await reader.read(1024)
        e = s_client.recv(dt)
    yield reader, writer
    writer.close()

@pytest.fixture
async def connected_echo(greeted, echo_server, s_client):
    r, w = greeted
    req = socks5.Request(socks5.REQ_COMMAND["CONNECT"], socks5.ADDR_TYPE["IPV4"], *echo_server)
    w.write(s_client.send(req))
    s_client.recv(await r.read(1024))
    return r, w

@pytest.mark.asyncio
class TestSocks:
    @pytest.mark.parametrize("req", (
            socks5.Request(socks5.REQ_COMMAND["CONNECT"], socks5.ADDR_TYPE["DOMAINNAME"], "localhost", 0),
            socks5.Request(socks5.REQ_COMMAND["CONNECT"], socks5.ADDR_TYPE["IPV4"], "127.0.0.1", 0),
            # socks5.Request(socks5.REQ_COMMAND["CONNECT"], socks5.ADDR_TYPE["IPV6"], "::1", 0)
    ))
    async def test_socks5_reqs(self, s_client, greeted, req, echo_server):
        req.port = echo_server[1]
        r, w = greeted
        w.write(s_client.send(req))
        resp = s_client.recv(await r.read(1024))
        assert resp.status == socks5.RESP_STATUS["SUCCESS"]

    @pytest.mark.parametrize("size", [10, 1000, 100000])
    async def test_socks5_connect(self, connected_echo, rw_echo, size):
        r, w = connected_echo
        await rw_echo(r, w, size=size)
