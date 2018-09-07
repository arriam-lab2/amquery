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

PORT = 'PORT'
NAME = 'NAME'

logging.basicConfig(format='%(asctime)s %(message)s')


def gentoken(nbytes=32) -> str:
    return secrets.token_hex(nbytes)


@click.group('cli', context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-p', '--port', required=True, type=int)
@click.option('-n', '--name', type=str)
@click.pass_context
def cli(ctx, port: int, name: str):
    ctx.obj[PORT] = port
    ctx.obj[NAME] = name


@cli.command('start')
@click.option('-c', '--config', required=True,
              type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.pass_context
def start(ctx, config):
    with open(config) as lines:
        # feed test name for now
        database = Database('DevDB', *parse(lines))
    key = gentoken(32)  # add an option to use a stable password instead
    # start a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(f'Access token: {key}')
    server = Server(database, ctx.obj[PORT], key, logger)
    run(server.run())


@cli.command('call')
@click.option('--token', prompt=True, hide_input=True, type=str)
@click.argument('message', nargs=-1, type=str)
@click.pass_context
def call(ctx, token, message):
    wrapped_msg = (Message(MessageType.CALL, token, message) if message else
                   Message(MessageType.HELP, token, ''))
    run(client_connection(ctx.obj[PORT], wrapped_msg))


if __name__ == '__main__':
    cli(obj={})

