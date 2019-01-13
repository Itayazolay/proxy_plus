import pytest

from proxy_plus import port_forwarding


@pytest.mark.asyncio
class TestServer:
    async def test_start_server(self, loop, echo_server, free_bind, echo_tester):
        addr = free_bind()
        server = await port_forwarding.start_port_forwarding(
            loop.create_server, loop.create_connection,
            addr, echo_server)
        await echo_tester(addr, sizes=(10, 30, 50), tests=3)
        server.close()

    async def test_start_lpf_server(self, loop, echo_server, free_bind, echo_tester):
        addr = free_bind()
        server = await port_forwarding.start_local_port_forwarding(addr,
                                                                   loop.create_connection,
                                                                   echo_server)
        await echo_tester(addr, sizes=(10, 30, 50), tests=3)
        server.close()

    async def test_start_rpf_server(self, loop, echo_server, free_bind, echo_tester):
        addr = free_bind()
        server = await port_forwarding.start_remote_port_forwarding(
            addr, loop.create_server, echo_server)

        await echo_tester(addr, sizes=(10, 30, 50), tests=3)
        server.close()
