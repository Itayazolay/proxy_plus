import asyncio
import pytest

loop = asyncio.get_event_loop()


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
