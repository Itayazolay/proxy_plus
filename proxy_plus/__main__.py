# -*- coding: utf-8 -*-

"""Console script for proxy_plus."""
import sys
import click
import asyncio
import proxy_plus
import signal

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

@click.command()
@click.option('-s', '--string-to-echo', 'string')
def echo(string):
    click.echo(string)

if __name__ == "__main__":
    for signame in ('SIGINT', 'SIGTERM'):

        signal.signal(getattr(signal, signame),
                    lambda a: loop.stop())
    main.add_command(echo)
    main.add_command(lpf)
    sys.exit(main())  # pragma: no cover
