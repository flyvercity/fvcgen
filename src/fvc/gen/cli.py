"""Command-line interface for FVC Generator."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .generator import FVCGenerator
from .utils import generate_config_template

console = Console()


@click.group()
@click.version_option()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    """FVC Generator - Generate FVC scenarios for UAS traffic management."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@main.command()
@click.option(
    '--config', '-c', 'config_path',
    required=True, help='Path to configuration file'
)
@click.option('--output', '-o', help='Output file path (overrides config)')
@click.option(
    '--stream', is_flag=True, help='Enable streaming output to stdout'
)
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

            # Load configuration
            config = Config.from_file(config_path)
            progress.update(task, description='Configuration loaded')

            # Override output path if provided
            if output:
                config.general.output_file = output

            # Generate FVC
            generator = FVCGenerator(config)
            progress.update(task, description='Generating FVC scenario...')

            if stream:
                generator.generate_stream()
            else:
                generator.generate()
                progress.update(task, description='FVC scenario generated successfully')

    except Exception as e:
        console.print(f'[red]Error: {e}[/red]')
        raise click.Abort()


@main.command()
@click.option('--output', '-o', default='config_template.yaml', help='Output template file path')
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
    '--config', '-c', 'config_path',
    required=True,
    help='Path to configuration file',
)
def validate(config_path):
    """Validate configuration file."""
    try:
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
        table.add_row('General', 'Output File', config.general.output_file or 'stdout')

        # Origins count
        origins_count = len(config.origins)
        table.add_row('Origins', 'Count', str(origins_count))

        # Objects count
        total_objects = sum(len(origin.objects) for origin in config.origins)
        table.add_row('Objects', 'Total Count', str(total_objects))

        console.print(table)

    except Exception as e:
        console.print(f'[red]Configuration validation failed: {e}[/red]')
        raise click.Abort()


if __name__ == '__main__':
    main()
