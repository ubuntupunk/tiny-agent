import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import asyncio
import logging

from .core import Agent
from .tools import get_default_tools

app = typer.Typer()
console = Console()


@app.command()
def run(
    task: str = typer.Argument(..., help="Task to execute"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    tools: Optional[str] = typer.Option(None, "--tools", "-t", help="Comma-separated list of tools to use")
):
    """Run the tiny agent with a specific task."""
    
    async def _run():
        agent = Agent(verbose=verbose)
        
        # Register default tools
        default_tools = get_default_tools()
        if tools:
            tool_names = [t.strip() for t in tools.split(",")]
            for tool_name in tool_names:
                if tool_name in default_tools:
                    agent.register_tool(default_tools[tool_name])
                else:
                    console.print(f"[red]Unknown tool: {tool_name}[/red]")
                    return
        else:
            # Register all default tools
            for tool in default_tools.values():
                agent.register_tool(tool)
        
        console.print(f"[green]Running task:[/green] {task}")
        console.print(f"[blue]Available tools:[/blue] {list(agent.tools.keys())}")
        
        result = await agent.run(task)
        
        console.print("\n[green]Result:[/green]")
        console.print(result)
    
    asyncio.run(_run())


@app.command()
def list_tools():
    """List all available tools."""
    default_tools = get_default_tools()
    
    table = Table(title="Available Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    
    for name, tool in default_tools.items():
        table.add_row(name, tool.description)
    
    console.print(table)


@app.command()
def shell():
    """Start an interactive shell with the agent."""
    console.print("[green]Tiny Agent Interactive Shell[/green]")
    console.print("Type 'exit' to quit, 'help' for commands")
    
    async def _shell():
        agent = Agent(verbose=True)
        
        # Register all default tools
        default_tools = get_default_tools()
        for tool in default_tools.values():
            agent.register_tool(tool)
        
        while True:
            try:
                user_input = typer.prompt("tiny-agent> ")
                
                if user_input.lower() == "exit":
                    break
                elif user_input.lower() == "help":
                    console.print("[blue]Available commands:[/blue]")
                    console.print("  help - Show this help")
                    console.print("  exit - Exit the shell")
                    console.print("  tools - List available tools")
                    console.print("  memory - Show memory contents")
                    console.print("  <task> - Execute a task")
                    continue
                elif user_input.lower() == "tools":
                    console.print(f"[blue]Tools:[/blue] {list(agent.tools.keys())}")
                    continue
                elif user_input.lower() == "memory":
                    keys = agent.memory.list_keys()
                    console.print(f"[blue]Memory keys:[/blue] {keys}")
                    continue
                
                result = await agent.run(user_input)
                console.print(f"[green]Result:[/green] {result}")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    
    asyncio.run(_shell())


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()