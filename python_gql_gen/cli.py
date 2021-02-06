# -*- coding: utf-8 -*-

"""Console script for python_gql_gen."""
import sys
import click
from python_gql_gen import get_schema, parse_schema_to_gql


@click.command()
@click.option('--url','-u', help='the graphql api url  ', required=True)
@click.option('--directory', '-d', help='the output directory name ')
def main(url,directory ):
    """Console script for python_gql_gen."""
    click.echo("get schema from url ".format(url))
    schema_str=get_schema(url=url,directory=directory)

    click.echo("parse the schema to query(mutation...) file to  ".format(directory))
    parse_schema_to_gql(schema_str=schema_str,directory=directory)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
