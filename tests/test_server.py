import asyncio

import pytest
from proxy_plus import port_forwarding

loop = asyncio.get_event_loop()


async def validate_echo(host, port, size=10):
    reader, writer = await asyncio.open_connection(host, port)
    msg = b"A" * size
    writer.write(msg)
    assert await reader.readexactly(len(msg)) == msg


async def concurrent_validate_echo(host, port):
    await asyncio.gather(*[validate_echo(host, port, size=1024 * i)
                           for i in range(0, 20, 2)])


@pytest.mark.asyncio
class TestServer:
    async def test_start_server(self, echo_server, free_port):
        addr = ("", free_port())
        server = await port_forwarding.start_port_forwarding(
            loop.create_server, loop.create_connection,
            addr, echo_server)
        await concurrent_validate_echo(*addr)
        server.close()

    async def test_start_lpf_server(self, echo_server, free_port):
        addr = ("", free_port())
        server = await port_forwarding.start_local_port_forwarding(addr,
                                                                   loop.create_connection,
                                                                   echo_server)
        await concurrent_validate_echo(*addr)
        server.close()

    async def test_start_rpf_server(self, echo_server, free_port):
        addr = ("", free_port())
        server = await port_forwarding.start_remote_port_forwarding(
            addr, loop.create_server, echo_server)
        await concurrent_validate_echo(*addr)
        server.close()
