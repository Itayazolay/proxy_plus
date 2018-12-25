import asyncio
import pytest
from proxy_plus.forwarder import Proxy
from proxy_plus.port_forwarding import PortForwarding

loop = asyncio.get_event_loop()


class EchoServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.transport.write(data)


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture
def free_port(unused_tcp_port_factory):
    return unused_tcp_port_factory


@pytest.fixture
async def echo_server(free_port):
    port = free_port()
    server = await loop.create_server(EchoServer, "", port)
    yield ("127.0.0.1", port)
    server.close()


@pytest.fixture
async def proxy(echo_server, free_port):
    port = free_port()
    proto = PortForwarding(echo_server, loop.create_connection)
    server = await loop.create_server(lambda: proto, "", port)
    h, p = "127.0.0.1", port
    reader, writer = await asyncio.open_connection(h, p)
    writer.write(b"H")
    assert await reader.read(1) == b"H"
    yield reader, writer, proto
    server.close()


@pytest.mark.asyncio
class TestForwarder:
    @pytest.mark.parametrize("size", [1024, 1024 * 1024, 1024 * 1024 * 50])
    async def test_large_data(self, proxy, size):
        reader, writer, _ = proxy
        msg = b"A" * size
        writer.write(msg)
        assert await reader.readexactly(len(msg)) == msg

    async def test_pauses(self, proxy):
        reader, writer, proto = proxy
        ## Make sure everything works
        msg = b"Hello"
        writer.write(msg)
        assert await reader.read(len(msg)) == msg
        local_proxy, remote_proxy = proto._proxy, proto._remote_proxy
        local_proxy.pause_writing(), remote_proxy.pause_writing()
        assert local_proxy.remote._paused
        assert remote_proxy.remote._paused
        local_proxy.resume_writing(), remote_proxy.resume_writing()
        assert not local_proxy.remote._paused
        assert not remote_proxy.remote._paused

    async def test_eof(self, proxy):
        reader, writer, proto = proxy
        writer.write_eof()
        await reader.read()
        assert proto._proxy.remote.is_closing()
        assert proto._remote_proxy.remote.is_closing()
