#!/usr/bin/env python3
"""
LLM Version Manager - CLI
Command-line interface for managing LLM versions across projects
"""
import click
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import Dict, List

from monitor.check_openai import OpenAIMonitor
from monitor.check_anthropic import AnthropicMonitor
from scanner.python_scanner import PythonScanner


console = Console()


def load_config() -> Dict:
    """Load configuration from models.yaml"""
    config_path = Path(__file__).parent / "config" / "models.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    LLM Version Manager - Keep your AI models up to date

    Monitors LLM providers for deprecations and helps update your codebase.
    """
    pass


@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'anthropic', 'all']), default='all')
def monitor(provider):
    """Check LLM providers for model updates and deprecations"""
    console.print("\n[bold cyan]🔍 LLM Provider Monitor[/bold cyan]\n")

    config = load_config()

    if provider in ['openai', 'all']:
        console.print("[yellow]Checking OpenAI...[/yellow]")
        try:
            openai_monitor = OpenAIMonitor()
            report = openai_monitor.generate_report()

            console.print(f"✅ Found {report['total_models']} OpenAI models")
            console.print(f"  - Chat models: {len(report['chat_models'])}")
            console.print(f"  - Embedding models: {len(report['embedding_models'])}")
            console.print(f"  - Whisper models: {len(report['whisper_models'])}")

            # Check for issues with configured models
            openai_config = config['providers']['openai']['models']
            test_models = {
                'chat': openai_config['chat']['current'],
                'embedding': openai_config['embedding']['current'],
                'transcription': openai_config['transcription']['current']
            }

            warnings = openai_monitor.check_deprecations(test_models)
            if warnings:
                console.print("\n[red]⚠️  Warnings:[/red]")
                for warning in warnings:
                    console.print(f"  - {warning['message']}")

        except Exception as e:
            console.print(f"[red]❌ Error checking OpenAI: {e}[/red]")

    if provider in ['anthropic', 'all']:
        console.print("\n[yellow]Checking Anthropic...[/yellow]")
        try:
            anthropic_monitor = AnthropicMonitor()
            report = anthropic_monitor.generate_report()

            console.print(f"✅ {report['total_current']} current Anthropic models")
            console.print(f"❌ {report['total_deprecated']} deprecated models")

            # Check for issues with configured models
            anthropic_config = config['providers']['anthropic']['models']['chat']['tiers']
            test_models = {
                'light': anthropic_config['light']['current'],
                'standard': anthropic_config['standard']['current'],
                'advanced': anthropic_config['advanced']['current']
            }

            warnings = anthropic_monitor.check_deprecations(test_models)
            if warnings:
                console.print("\n[red]⚠️  Warnings:[/red]")
                for warning in warnings:
                    console.print(f"  - {warning['message']}")
                    suggestions = anthropic_monitor.suggest_replacements(warning['model'])
                    if suggestions:
                        console.print(f"    [green]Suggested: {', '.join(suggestions)}[/green]")

        except Exception as e:
            console.print(f"[red]❌ Error checking Anthropic: {e}[/red]")

    console.print("\n✅ [green]Monitor check complete[/green]\n")


@cli.command()
@click.option('--project', help='Project name from config')
@click.option('--path', help='Direct path to scan')
@click.option('--language', type=click.Choice(['python', 'typescript', 'swift', 'kotlin']), default='python')
def scan(project, path, language):
    """Scan a project for LLM model references"""
    console.print("\n[bold cyan]🔎 Code Scanner[/bold cyan]\n")

    config = load_config()

    # Determine project path
    if project:
        project_config = config['projects'].get(project)
        if not project_config:
            console.print(f"[red]❌ Project '{project}' not found in config[/red]")
            return
        scan_path = project_config['path']
        project_name = project_config['name']
    elif path:
        scan_path = path
        project_name = Path(path).name
    else:
        console.print("[red]❌ Either --project or --path must be specified[/red]")
        return

    console.print(f"Scanning: [yellow]{project_name}[/yellow]")
    console.print(f"Path: {scan_path}")
    console.print(f"Language: {language}\n")

    # Create appropriate scanner
    if language == 'python':
        scanner = PythonScanner(scan_path)
    else:
        console.print(f"[red]❌ Scanner for {language} not yet implemented[/red]")
        return

    # Scan the project
    with console.status("[bold green]Scanning files..."):
        references = scanner.scan_project()

    if not references:
        console.print("[yellow]No model references found[/yellow]")
        return

    # Generate and display report
    report = scanner.generate_report(references)

    console.print(f"\n[green]✅ Found {report['total_references']} model references[/green]\n")

    # Table of models
    table = Table(title="Models Found")
    table.add_column("Model", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for model, count in sorted(report['by_model'].items(), key=lambda x: x[1], reverse=True):
        table.add_row(model, str(count))

    console.print(table)

    # Show details
    if click.confirm("\nShow detailed locations?", default=False):
        for ref in references[:20]:  # Limit to first 20
            console.print(f"\n[cyan]{ref.file_path}:{ref.line_number}[/cyan]")
            console.print(f"  Model: [yellow]{ref.model_name}[/yellow]")
            console.print(f"  Context: {ref.context}")
            console.print(f"  Line: {ref.line_content[:80]}...")

        if len(references) > 20:
            console.print(f"\n[dim]... and {len(references) - 20} more[/dim]")


@cli.command()
def list_projects():
    """List all configured projects"""
    console.print("\n[bold cyan]📋 Configured Projects[/bold cyan]\n")

    config = load_config()

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="yellow")
    table.add_column("Language", style="green")
    table.add_column("Mappings", justify="right", style="magenta")

    for project_id, project_config in config['projects'].items():
        table.add_row(
            project_config['name'],
            project_config['path'],
            project_config['language'],
            str(len(project_config['mappings']))
        )

    console.print(table)
    console.print()


@cli.command()
@click.option('--project', required=True, help='Project name from config')
def check(project):
    """
    Check a project for deprecated models and suggest updates
    Combines monitoring and scanning for a specific project
    """
    console.print(f"\n[bold cyan]🔍 Checking Project: {project}[/bold cyan]\n")

    config = load_config()

    # Get project config
    project_config = config['projects'].get(project)
    if not project_config:
        console.print(f"[red]❌ Project '{project}' not found in config[/red]")
        return

    # Initialize monitors
    openai_monitor = OpenAIMonitor()
    anthropic_monitor = AnthropicMonitor()

    issues = []

    # Check each mapping
    for mapping in project_config['mappings']:
        provider = mapping['provider']
        model_id = mapping['id']

        console.print(f"Checking: [yellow]{model_id}[/yellow]")

        # Get the expected model from config
        provider_config = config['providers'][provider]

        # Scan the actual files
        for location in mapping['locations']:
            file_path = Path(project_config['path']) / location['file']

            if not file_path.exists():
                issues.append({
                    'severity': 'warning',
                    'mapping_id': model_id,
                    'message': f"File not found: {location['file']}"
                })
                continue

            # Read the file and check the model
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                if location.get('line_number'):
                    line_num = location['line_number'] - 1
                    if line_num < len(lines):
                        line = lines[line_num]

                        # Extract model name from line
                        # This is a simple extraction - could be improved
                        for pattern in [r'gpt-[\w\.-]+', r'claude-[\w\.-]+', r'gemini-[\w\.-]+']:
                            import re
                            match = re.search(pattern, line)
                            if match:
                                found_model = match.group(0)

                                # Check if this model is valid
                                if provider == 'openai':
                                    if not openai_monitor.check_model_exists(found_model):
                                        suggestions = openai_monitor.suggest_replacements(found_model)
                                        issues.append({
                                            'severity': 'error',
                                            'mapping_id': model_id,
                                            'file': str(file_path),
                                            'line': line_num + 1,
                                            'current_model': found_model,
                                            'message': f"Model '{found_model}' not found",
                                            'suggestions': suggestions
                                        })

                                elif provider == 'anthropic':
                                    if not anthropic_monitor.check_model_exists(found_model):
                                        suggestions = anthropic_monitor.suggest_replacements(found_model)
                                        issues.append({
                                            'severity': 'error',
                                            'mapping_id': model_id,
                                            'file': str(file_path),
                                            'line': line_num + 1,
                                            'current_model': found_model,
                                            'message': f"Model '{found_model}' not found or deprecated",
                                            'suggestions': suggestions
                                        })

                                break

            except Exception as e:
                issues.append({
                    'severity': 'error',
                    'mapping_id': model_id,
                    'message': f"Error reading file: {e}"
                })

    # Display results
    if not issues:
        console.print("\n[green]✅ No issues found - all models are up to date![/green]\n")
    else:
        console.print(f"\n[red]⚠️  Found {len(issues)} issues:[/red]\n")

        for issue in issues:
            severity_color = "red" if issue['severity'] == 'error' else "yellow"
            console.print(f"[{severity_color}]●[/{severity_color}] {issue['message']}")

            if 'file' in issue:
                console.print(f"  File: {issue['file']}:{issue['line']}")
                console.print(f"  Current model: [yellow]{issue['current_model']}[/yellow]")

            if 'suggestions' in issue and issue['suggestions']:
                console.print(f"  [green]Suggested: {', '.join(issue['suggestions'])}[/green]")

            console.print()


@cli.command()
def report():
    """Generate a comprehensive status report"""
    console.print("\n[bold cyan]📊 LLM Version Manager - Status Report[/bold cyan]\n")

    config = load_config()

    # Provider status
    console.print(Panel.fit("[bold]Provider Status[/bold]", border_style="cyan"))

    # OpenAI
    try:
        openai_monitor = OpenAIMonitor()
        report = openai_monitor.generate_report()
        console.print(f"[green]✅ OpenAI:[/green] {report['total_models']} models available")
    except Exception as e:
        console.print(f"[red]❌ OpenAI:[/red] {e}")

    # Anthropic
    try:
        anthropic_monitor = AnthropicMonitor()
        report = anthropic_monitor.generate_report()
        console.print(f"[green]✅ Anthropic:[/green] {report['total_current']} current models")
    except Exception as e:
        console.print(f"[red]❌ Anthropic:[/red] {e}")

    console.print()

    # Project summary
    console.print(Panel.fit("[bold]Project Summary[/bold]", border_style="cyan"))
    console.print(f"Total projects configured: {len(config['projects'])}")

    for project_id, project_config in config['projects'].items():
        console.print(f"  • {project_config['name']}: {len(project_config['mappings'])} model mappings")

    console.print()


if __name__ == "__main__":
    cli()
