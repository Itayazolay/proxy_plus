#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `proxy_plus` package."""
import asyncio

import pytest

from proxy_plus import PortForwarding

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
