import datetime
from pprint import pprint

import click

from btsearch.searchers import RegioJetSearcher
from btsearch.exceptions import InvalidDateFormat
from btsearch.config_loader import ConfigLoader

# def validate_rolls(ctx, param, value):
#     try:
#         rolls, dice = map(int, value.split('d', 2))
#         return (dice, rolls)
#     except ValueError:
#         raise click.BadParameter('rolls need to be in format NdM')

def validate_date(ctx, param, value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise InvalidDateFormat()


@click.command()
@click.option('--from_')
@click.option('--to')
@click.option('--date', callback=validate_date)
@click.option('--passengers', default=1)
# @click.option('--rolls', callback=validate_rolls, default='1d6')
def search(from_, to, date, passengers):
    click.echo('Start from: {from_} to: {to} when: {date} passengers:{passengers}'.format(from_=from_,
                                                                                           to=to,
                                                                                           date=date,
                                                                                           passengers=passengers))

    config_loader = ConfigLoader('config.json')
    searcher = RegioJetSearcher(config_loader.config)
    results = searcher.get_route(from_, to, date)
    click.echo(pprint(results))
    click.echo(len(results))

if __name__ == '__main__':
    search()