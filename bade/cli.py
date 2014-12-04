import click
import yaml
from .build import Build
from .config import Configuration


@click.command()
@click.argument(
    'config_path',
    type=click.Path(exists=True),
    default='.baderc.yaml'
)
def main(config_path):
    with open(config_path, 'r') as config_file:
        config = Configuration(yaml.load(config_file.read()))
    build = Build(config)
