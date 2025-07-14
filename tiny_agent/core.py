from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Tool(Protocol):
    """Protocol for tools that can be used by the agent."""
    
    name: str
    description: str
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        ...


class Memory:
    """Simple in-memory storage for agent state."""
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in memory."""
        self._store[key] = value
        self._history.append({
            "action": "set",
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from memory."""
        return self._store.get(key, default)
    
    def delete(self, key: str) -> None:
        """Delete a value from memory."""
        if key in self._store:
            del self._store[key]
            self._history.append({
                "action": "delete",
                "key": key,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def list_keys(self) -> List[str]:
        """List all keys in memory."""
        return list(self._store.keys())
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the history of memory operations."""
        return self._history.copy()


class Agent:
    """Core agent class that orchestrates tools and capabilities."""
    
    def __init__(self, name: str = "tiny-agent", verbose: bool = False):
        self.name = name
        self.verbose = verbose
        self.memory = Memory()
        self.tools: Dict[str, Tool] = {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        if not isinstance(tool, Tool):
            raise TypeError(f"Tool {tool} does not implement Tool protocol")
        
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a specific tool with given arguments."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            self.logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(**kwargs)
            
            # Store execution in memory
            self.memory.set(f"tool_{tool_name}_last_result", result.dict())
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """Run the agent with a high-level task."""
        self.logger.info(f"Starting task: {task}")
        
        # Store task in memory
        self.memory.set("current_task", task)
        
        # This is a basic implementation - could be enhanced with:
        # - Task decomposition
        # - Tool selection based on task
        # - Planning and execution loops
        
        return {
            "task": task,
            "status": "completed",
            "tools_available": list(self.tools.keys()),
            "memory_keys": self.memory.list_keys()
        }