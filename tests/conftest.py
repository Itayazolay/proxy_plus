#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `proxy_plus` package."""
import asyncio
import socket

import pytest

from proxy_plus import PortForwarding



class EchoServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.transport.write(data)


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    return loop

@pytest.fixture
def loop(event_loop):
    return event_loop

@pytest.fixture
def free_bind():
    def get_addr():
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        addr = s.getsockname()
        s.close()
        return addr

    return get_addr


@pytest.fixture
async def echo_server(free_bind, loop):
    addr = free_bind()
    server = await loop.create_server(EchoServer, *addr)
    yield addr
    server.close()


@pytest.fixture
async def proxy(echo_server, free_bind, loop):
    addr = free_bind()
    proto = PortForwarding(echo_server, loop.create_connection)
    server = await loop.create_server(lambda: proto, *addr)
    reader, writer = await asyncio.open_connection(*addr)
    writer.write(b"H")
    assert await reader.read(1) == b"H"
    yield reader, writer, proto
    server.close()


@pytest.fixture
async def echo_tester():
    async def tester(addr, sizes=(10,), tests=1):
        coro = []
        for i in sizes:
            coro.extend([validate_echo(*addr, size=i) for _ in
                        range(tests)])
        return await asyncio.gather(*coro)
    return tester


async def validate_echo(host, port, size=10):
    reader, writer = await asyncio.open_connection(host, port)
    msg = b"A" * size
    writer.write(msg)
    assert await reader.readexactly(len(msg)) == msg
