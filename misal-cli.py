#! /usr/bin/env python

import logging
import secrets

import click
from aiorun import run

from misal.core import Database, parse
from misal.server import MessageType, Message, Server, client_connection


# TODO make --port optional in the start command
# TODO try the closest free port instead of throwing an error when an occupied --port is provided start
# TODO add the option to detect a database by name instead of port in the call command
# TODO automatically search for a config by name instead of demanding a config path in the start command
# TODO add password support in the start command

logging.basicConfig(format='%(asctime)s %(message)s')


def gentoken(nbytes=32) -> str:
    return secrets.token_hex(nbytes)


@click.group('cli', context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    pass


@cli.command('start')
@click.option('-p', '--port', type=int, required=True)
@click.option('-c', '--config', default=None)
def start(port, config):
    with open(config) as lines:
        # feed test name for now
        database = Database('DevDB', *parse(lines))
    key = gentoken(32)  # add an option to use a stable password instead
    # start a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(f'Access token: {key}')
    server = Server(database, port, key, logger)
    run(server.run())


@cli.command('call')
@click.option('-p', '--port', type=int, required=True)
@click.option('--token', prompt=True, hide_input=True, type=str)
@click.argument('message', nargs=-1, type=str)
def call(port, token, message):
    wrapped_msg = (Message(MessageType.CALL, token, message) if message else
                   Message(MessageType.HELP, token, ''))
    run(client_connection(port, wrapped_msg))


if __name__ == '__main__':
    cli()

