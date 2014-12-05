import os

import click
import yaml

from .build import Build
from .config import Configuration


@click.command()
@click.argument('config_path', type=click.Path(), default='.bade.yaml')
@click.option('--debug', is_flag=True, help='Print debugging info')
def main(config_path, debug):
    'Command line interface for bade'
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_dict = yaml.load(config_file.read())
            config_dict.update({'debug': debug})
            config = Configuration(config_dict)
    else:
        config = Configuration({})
    build = Build(config)
    build.run()
