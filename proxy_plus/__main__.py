# -*- coding: utf-8 -*-

"""Console script for proxy_plus."""
import sys
import signal
import asyncio
import warnings

import click
import proxy_plus

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    warnings.warn("uvloop is not installed and is recommended for enhanced performance")


loop = asyncio.get_event_loop()


@click.group()
def main(args=None):
    """Console script for proxy_plus."""
    pass

@click.command()
@click.option("--lhost", default="")
@click.option("--lport", default=0)
@click.option("--rhost")
@click.option("--rport")
def lpf(lhost, lport, rhost, rport):
    """
    Listen-Connect proxy(local port forwarding).

    :param lhost: Local host to bind on.
    :param lport: Local port to bind on.
    :param rhost: Remote host to connect to.
    :param rport: Remote port to connect to.
    """
    loop.run_until_complete(
        proxy_plus.start_local_port_forwarding(
            (lhost, lport), loop.create_connection,
            (rhost, rport)
        )
    )
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
    return 0


if __name__ == "__main__":
    for signame in ('SIGINT', 'SIGTERM'):

        signal.signal(getattr(signal, signame),
                      lambda a: loop.stop())
    main.add_command(lpf)
    sys.exit(main())  # pragma: no cover
