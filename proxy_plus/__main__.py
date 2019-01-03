# -*- coding: utf-8 -*-

"""Console script for proxy_plus."""
import sys
import click
import asyncio
import proxy_plus

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

loop = asyncio.get_event_loop()


@click.group()
def main(args=None):
    """Console script for proxy_plus."""
    pass


def async_command(func):
    def wrapper(*args, **kwargs):
        try:
            loop.run_until_complete(func(*args, **kwargs))
        except KeyboardInterrupt:
            pass
        finally:
            loop.stop()

    return wrapper


@click.command()
@click.option("--lhost", default="127.0.0.1")
@click.option("--lport", default=0)
@click.option("--rhost")
@click.option("--rport")
@async_command
async def listen_connect(lhost, lport, rhost, rport):
        server = await proxy_plus.start_local_port_forwarding(
            (lhost, lport), loop.create_connection,
            (rhost, rport))
        await server.wait_closed()


if __name__ == "__main__":
    main.add_command(listen_connect)
    sys.exit(main())  # pragma: no cover
