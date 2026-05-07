"""Command-line interface for FVC Generator."""

import logging
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from importlib.metadata import version

from .config import Config
from .generator import FVCGenerator
from .utils import generate_config_template
from .schema import validate_config_schema

console = Console()


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


@click.group()
@click.version_option(version=version('fvcgen'))
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    """FVC Generator - Generate FVC scenarios for UAS traffic management."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@main.command()
@click.option('--config', '-c', 'config_path', required=True, help='Path to configuration file')
@click.option('--output', '-o', help='Output file path')
@click.option('--stream', is_flag=True, help='Enable streaming output to stdout')
@click.pass_context
def generate(ctx, config_path, output, stream):
    """Generate FVC scenario from configuration file."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            console=console,
        ) as progress:
            task = progress.add_task('Loading configuration...', total=None)

            # Schema validation first
            from pathlib import Path
            import yaml as _yaml

            path = Path(config_path)
            if not path.exists():
                console.print(f'[red]Configuration file not found: {path}[/red]')
                raise click.Abort()

            with open(path, 'r', encoding='utf-8') as f:
                raw_data = _yaml.safe_load(f)

            schema_errors = validate_config_schema(raw_data)
            if schema_errors:
                console.print('[red]Configuration validation failed:[/red]')
                for err in schema_errors:
                    console.print(f'  [yellow]•[/yellow] {err}')
                raise click.Abort()

            # Load configuration
            config = Config.from_file(config_path)
            progress.update(task, description='Configuration loaded')

            # Generate FVC
            generator = FVCGenerator(config)
            progress.update(task, description='Generating FVC scenario...')

            if stream:
                generator.generate_stream()
            else:
                generator.generate(output)
                progress.update(task, description='FVC scenario generated successfully')

    except click.Abort:
        raise
    except Exception as e:
        console.print(f'[red]Error: {e}[/red]')
        raise click.Abort()


@main.command()
@click.option('--output', '-o', default='config-template.yaml', help='Output template file path')
def template(output):
    """Generate a configuration file template."""
    try:
        generate_config_template(output)
        console.print(f'[green]Configuration template generated: {output}[/green]')
    except Exception as e:
        console.print(f'[red]Error generating template: {e}[/red]')
        raise click.Abort()


@main.command()
@click.option(
    '--config',
    '-c',
    'config_path',
    required=True,
    help='Path to configuration file',
)
def validate(config_path):
    """Validate configuration file."""
    try:
        # Load raw YAML for schema validation
        from pathlib import Path
        import yaml as _yaml

        path = Path(config_path)
        if not path.exists():
            console.print(f'[red]Configuration file not found: {path}[/red]')
            raise click.Abort()

        with open(path, 'r', encoding='utf-8') as f:
            raw_data = _yaml.safe_load(f)

        # Schema validation (catches unknown fields and structural issues)
        schema_errors = validate_config_schema(raw_data)
        if schema_errors:
            console.print('[red]Configuration validation failed:[/red]')
            for err in schema_errors:
                console.print(f'  [yellow]•[/yellow] {err}')
            raise click.Abort()

        # Pydantic validation (type coercion, value constraints)
        config = Config.from_file(config_path)
        console.print('[green]Configuration is valid[/green]')

        # Display configuration summary
        table = Table(title='Configuration Summary')
        table.add_column('Section', style='cyan')
        table.add_column('Property', style='magenta')
        table.add_column('Value', style='green')

        # General settings
        base_point = config.general.base_point
        table.add_row('General', 'Base Point', f'{base_point.lat:.6f}, {base_point.lon:.6f}')
        table.add_row('General', 'Default Speed', f'{config.general.defaults.speed} m/s')
        table.add_row('General', 'Default Altitude', f'{config.general.defaults.altitude} m')
        table.add_row('General', 'Time Step', f'{config.general.defaults.time_step} s')
        table.add_row('General', 'Output File', 'provided via CLI or stdout')

        # Origins count
        origins_count = len(config.origins)
        table.add_row('Origins', 'Count', str(origins_count))

        # Objects count
        total_objects = sum(len(origin.objects) for origin in config.origins)
        table.add_row('Objects', 'Total Count', str(total_objects))

        console.print(table)

    except click.Abort:
        raise
    except Exception as e:
        console.print(f'[red]Configuration validation failed: {e}[/red]')
        raise click.Abort()


if __name__ == '__main__':
    main()
