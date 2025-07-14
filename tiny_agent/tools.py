from typing import Dict, Any
import httpx
from .core import Tool, ToolResult


class HTTPTool(Tool):
    """Tool for making HTTP requests."""
    
    name = "http_request"
    description = "Make HTTP requests to web APIs"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def execute(self, method: str = "GET", url: str = "", **kwargs) -> ToolResult:
        """Make an HTTP request."""
        try:
            method = method.upper()
            response = await self.client.request(method, url, **kwargs)
            
            return ToolResult(
                success=True,
                data={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "text": response.text,
                    "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileTool(Tool):
    """Tool for file system operations."""
    
    name = "file_operations"
    description = "Read and write files"
    
    async def execute(self, action: str = "read", filepath: str = "", content: str = "", **kwargs) -> ToolResult:
        """Perform file operations."""
        try:
            if action == "read":
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = f.read()
                return ToolResult(success=True, data={"content": data})
            
            elif action == "write":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ToolResult(success=True, data={"message": f"File written: {filepath}"})
            
            elif action == "exists":
                import os
                exists = os.path.exists(filepath)
                return ToolResult(success=True, data={"exists": exists})
            
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ShellTool(Tool):
    """Tool for executing shell commands."""
    
    name = "shell_command"
    description = "Execute shell commands"
    
    async def execute(self, command: str = "", timeout: int = 30, **kwargs) -> ToolResult:
        """Execute a shell command."""
        import asyncio
        from asyncio.subprocess import PIPE
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=PIPE,
                stderr=PIPE,
                shell=True
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return ToolResult(
                success=process.returncode == 0,
                data={
                    "returncode": process.returncode,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8')
                }
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, error="Command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


def get_default_tools() -> Dict[str, Any]:
    """Get all default tools."""
    return {
        "http": HTTPTool(),
        "file": FileTool(),
        "shell": ShellTool(),
    }